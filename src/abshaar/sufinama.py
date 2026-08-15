from __future__ import annotations

import hashlib
import html
import json
import random
import subprocess
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from abshaar.jsonl import read_jsonl, write_json, write_jsonl
from abshaar.source_matching import match_source_manifest


BASE_URL = "https://sufinama.org"
ENGLISH_INDEX = f"{BASE_URL}/poets/bulleh-shah/kaafi"
URDU_INDEX = f"{ENGLISH_INDEX}?lang=ur"
PARSER_VERSION = "sufinama_v1"
TEXT_PARSER_VERSION = "sufinama_texts_v1"
DEFAULT_USER_AGENT = "Abshaar academic corpus builder; contact raufnawaz@college.harvard.edu"

TEXT_CATEGORY_CONFIGS: tuple[dict[str, Any], ...] = (
    {"category": "kalaam", "index_path": "kalaam", "expected_count": 3, "mode": "detail"},
    {"category": "doha", "index_path": "dohe", "expected_count": 23, "mode": "inline"},
    {"category": "shabad", "index_path": "shabad", "expected_count": 7, "mode": "detail"},
    {"category": "dohra", "index_path": "dohra", "expected_count": 12, "mode": "detail"},
    {"category": "athvara", "index_path": "athvara", "expected_count": 1, "mode": "detail"},
    {
        "category": "barahmasa",
        "index_path": "barahmasa",
        "expected_count": 1,
        "mode": "detail",
    },
    {"category": "holi", "index_path": "holi", "expected_count": 1, "mode": "detail"},
)
TEXT_EXPECTED_COUNT = sum(int(config["expected_count"]) for config in TEXT_CATEGORY_CONFIGS)
TEXT_REQUEST_VIEWS = ("default", "urdu", "hindi")


class CatalogParser(HTMLParser):
    def __init__(self, accepted_path_fragments: tuple[str, ...] = ("/kaafi/", "/ghazals/")) -> None:
        super().__init__(convert_charrefs=True)
        self.accepted_path_fragments = accepted_path_fragments
        self.items: list[dict[str, str]] = []
        self.next_url: str | None = None
        self._pending_id: str | None = None
        self._current_item: dict[str, str] | None = None
        self._capture_title = False
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        classes = set(values.get("class", "").split())

        if tag == "a" and "favorite" in classes and values.get("data-type") == "0":
            self._pending_id = values.get("data-id") or None

        href = values.get("href", "")
        if (
            tag == "a"
            and self._pending_id
            and any(fragment in href for fragment in self.accepted_path_fragments)
        ):
            self._current_item = {
                "content_id": self._pending_id,
                "url": urllib.parse.urljoin(BASE_URL, href),
                "title": values.get("title", "").strip(),
            }
            self._pending_id = None

        if tag == "h3" and self._current_item is not None:
            self._capture_title = True
            self._title_parts = []

        if tag == "div" and "contentLoadMorePaging" in classes and values.get("data-url"):
            self.next_url = urllib.parse.urljoin(BASE_URL, values["data-url"])

    def handle_data(self, data: str) -> None:
        if self._capture_title:
            self._title_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h3" and self._capture_title and self._current_item is not None:
            title = " ".join("".join(self._title_parts).split())
            if title:
                self._current_item["title"] = title
            self.items.append(self._current_item)
            self._current_item = None
            self._capture_title = False
            self._title_parts = []


class OuterPoemParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.content_id = ""
        self.raw_content_html = ""
        self._capture_h1 = False
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if not self.content_id and values.get("data-contentid"):
            self.content_id = values["data-contentid"]
        if tag == "input" and values.get("id") == "HtmlRawText" and values.get("data-html"):
            self.raw_content_html = html.unescape(values["data-html"])
        if tag == "h1" and not self.title:
            self._capture_h1 = True
            self._title_parts = []

    def handle_data(self, data: str) -> None:
        if self._capture_h1:
            self._title_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1" and self._capture_h1:
            self.title = " ".join("".join(self._title_parts).split())
            self._capture_h1 = False


class PoemContentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.layers: list[dict[str, Any]] = []
        self._depth = 0
        self._layer_depth: int | None = None
        self._stanza_depth: int | None = None
        self._layer: dict[str, Any] | None = None
        self._stanza_id = ""
        self._line: dict[str, Any] | None = None
        self._line_parts: list[str] = []
        self._token: dict[str, Any] | None = None
        self._token_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._depth += 1
        values = {key.lower(): value or "" for key, value in attrs}
        classes = set(values.get("class", "").split())

        if tag == "div" and "pMC" in classes and self._layer is None:
            self._layer_depth = self._depth
            self._layer = {"roman_mode": values.get("data-roman", ""), "lines": []}
            return

        if self._layer is None:
            return

        if tag == "div" and "w" in classes:
            self._stanza_depth = self._depth
            self._stanza_id = values.get("data-p", "")
        elif tag == "p" and values.get("data-l"):
            self._line = {
                "stanza_id": self._stanza_id,
                "line_id": values["data-l"],
                "tokens": [],
            }
            self._line_parts = []
        elif tag == "span" and self._line is not None:
            self._token = {"mapping_id": values.get("data-m", "")}
            self._token_parts = []

    def handle_data(self, data: str) -> None:
        if self._line is not None:
            self._line_parts.append(data)
        if self._token is not None:
            self._token_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "span" and self._token is not None and self._line is not None:
            self._token["text"] = " ".join("".join(self._token_parts).split())
            self._line["tokens"].append(self._token)
            self._token = None
            self._token_parts = []

        if tag == "p" and self._line is not None and self._layer is not None:
            self._line["text"] = " ".join("".join(self._line_parts).split())
            self._layer["lines"].append(self._line)
            self._line = None
            self._line_parts = []

        if tag == "div" and self._stanza_depth == self._depth:
            self._stanza_depth = None
            self._stanza_id = ""

        if tag == "div" and self._layer_depth == self._depth and self._layer is not None:
            self.layers.append(self._layer)
            self._layer = None
            self._layer_depth = None

        self._depth = max(0, self._depth - 1)


class InlineVerseParser(HTMLParser):
    """Parse source-separated short works embedded directly in a category page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.items: list[dict[str, Any]] = []
        self._depth = 0
        self._section_depth: int | None = None
        self._section: dict[str, Any] | None = None
        self._layer_depth: int | None = None
        self._stanza_depth: int | None = None
        self._layer: dict[str, Any] | None = None
        self._stanza_id = ""
        self._line: dict[str, Any] | None = None
        self._line_parts: list[str] = []
        self._token: dict[str, Any] | None = None
        self._token_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._depth += 1
        values = {key.lower(): value or "" for key, value in attrs}
        classes = set(values.get("class", "").split())

        if tag == "div" and "sherSection" in classes and self._section is None:
            self._section_depth = self._depth
            self._section = {
                "slug": values.get("id", ""),
                "content_id": "",
                "layers": [],
            }
            return

        if self._section is None:
            return

        if tag == "a" and "favorite" in classes and values.get("data-id"):
            self._section["content_id"] = values["data-id"]

        if tag == "div" and "pMC" in classes and self._layer is None:
            self._layer_depth = self._depth
            self._layer = {"roman_mode": values.get("data-roman", ""), "lines": []}
            return

        if self._layer is None:
            return

        if tag == "div" and "w" in classes:
            self._stanza_depth = self._depth
            self._stanza_id = values.get("data-p", "")
        elif tag == "p" and values.get("data-l"):
            self._line = {
                "stanza_id": self._stanza_id,
                "line_id": values["data-l"],
                "tokens": [],
            }
            self._line_parts = []
        elif tag == "span" and self._line is not None:
            self._token = {"mapping_id": values.get("data-m", "")}
            self._token_parts = []

    def handle_data(self, data: str) -> None:
        if self._line is not None:
            self._line_parts.append(data)
        if self._token is not None:
            self._token_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "span" and self._token is not None and self._line is not None:
            self._token["text"] = " ".join("".join(self._token_parts).split())
            self._line["tokens"].append(self._token)
            self._token = None
            self._token_parts = []

        if tag == "p" and self._line is not None and self._layer is not None:
            self._line["text"] = " ".join("".join(self._line_parts).split())
            self._layer["lines"].append(self._line)
            self._line = None
            self._line_parts = []

        if tag == "div" and self._stanza_depth == self._depth:
            self._stanza_depth = None
            self._stanza_id = ""

        if tag == "div" and self._layer_depth == self._depth and self._layer is not None:
            if self._section is not None:
                self._section["layers"].append(self._layer)
            self._layer = None
            self._layer_depth = None

        if tag == "div" and self._section_depth == self._depth and self._section is not None:
            views = _views_from_layers(self._section.pop("layers"))
            preferred = (
                views.get("roman_diacritic")
                or views.get("roman_plain")
                or views.get("urdu")
                or views.get("devanagari")
                or views.get("other")
                or {}
            )
            first_line = next(
                (
                    str(line.get("text") or "").strip()
                    for line in preferred.get("lines", [])
                    if str(line.get("text") or "").strip()
                ),
                "",
            )
            self._section["title"] = first_line
            self._section["views"] = views
            if self._section.get("content_id") and views:
                self.items.append(self._section)
            self._section = None
            self._section_depth = None

        self._depth = max(0, self._depth - 1)


class RateLimiter:
    def __init__(self, delay_seconds: float) -> None:
        self.delay_seconds = max(0.0, delay_seconds)
        self._lock = threading.Lock()
        self._last_request = 0.0

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            remaining = self.delay_seconds - (now - self._last_request)
            if remaining > 0:
                time.sleep(remaining + random.uniform(0, min(0.25, self.delay_seconds / 4)))
            self._last_request = time.monotonic()


class SufinamaClient:
    def __init__(
        self,
        user_agent: str,
        delay_seconds: float,
        retries: int = 3,
        transport: str = "urllib",
        offline: bool = False,
    ) -> None:
        self.user_agent = user_agent
        self.rate_limiter = RateLimiter(delay_seconds)
        self.retries = max(1, retries)
        self.transport = transport
        self.offline = offline

    def fetch(self, url: str) -> tuple[str, str, int]:
        if self.offline:
            raise RuntimeError(f"offline mode cache miss for {url}")
        if self.transport == "curl":
            return self._fetch_curl(url)

        last_error: Exception | None = None
        for attempt in range(self.retries):
            self.rate_limiter.wait()
            request = urllib.request.Request(
                url,
                headers={"User-Agent": self.user_agent, "Accept-Language": "en,ur;q=0.9"},
            )
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    body = response.read().decode("utf-8", errors="replace")
                    return body, response.geturl(), int(response.status)
            except urllib.error.HTTPError as exc:
                last_error = exc
                if exc.code not in {429, 500, 502, 503, 504}:
                    break
            except OSError as exc:
                last_error = exc
            time.sleep(2**attempt)
        raise RuntimeError(f"could not fetch {url}: {last_error}")

    def _fetch_curl(self, url: str) -> tuple[str, str, int]:
        marker = "\n__ABSHAAR_CURL_META__"
        last_error = "unknown curl error"
        for attempt in range(self.retries):
            self.rate_limiter.wait()
            completed = subprocess.run(
                [
                    "curl",
                    "-L",
                    "--fail",
                    "--silent",
                    "--show-error",
                    "--compressed",
                    "--connect-timeout",
                    "20",
                    "--max-time",
                    "90",
                    "-A",
                    self.user_agent,
                    "-H",
                    "Accept-Language: en,ur;q=0.9",
                    "-w",
                    f"{marker}%{{url_effective}}\t%{{http_code}}",
                    url,
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )
            if completed.returncode == 0 and marker in completed.stdout:
                body, metadata = completed.stdout.rsplit(marker, 1)
                final_url, status_text = metadata.strip().split("\t", 1)
                return body, final_url, int(status_text)
            last_error = completed.stderr.strip() or f"curl exit {completed.returncode}"
            time.sleep(2**attempt)
        raise RuntimeError(f"could not fetch {url}: {last_error}")


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _parse_catalog(
    html_text: str,
    accepted_path_fragments: tuple[str, ...] = ("/kaafi/", "/ghazals/"),
) -> tuple[list[dict[str, str]], str | None]:
    parser = CatalogParser(accepted_path_fragments)
    parser.feed(html_text)
    return parser.items, parser.next_url


def discover_catalog(client: SufinamaClient, index_url: str) -> list[dict[str, str]]:
    first_html, _, _ = client.fetch(index_url)
    items, next_url = _parse_catalog(first_html)
    if next_url:
        next_html, _, _ = client.fetch(next_url)
        next_items, _ = _parse_catalog(next_html)
        items.extend(next_items)

    unique: dict[str, dict[str, str]] = {}
    for item in items:
        content_id = item["content_id"]
        if content_id in unique and unique[content_id]["url"] != item["url"]:
            raise ValueError(f"conflicting URLs for Sufinama content id {content_id}")
        unique[content_id] = item
    return list(unique.values())


def _dominant_script(value: str) -> str:
    counts = {"arabic": 0, "devanagari": 0, "latin": 0}
    for character in value:
        if "\u0600" <= character <= "\u06ff":
            counts["arabic"] += 1
        elif "\u0900" <= character <= "\u097f":
            counts["devanagari"] += 1
        elif ("a" <= character.lower() <= "z") or (
            "\u00c0" <= character <= "\u024f"
        ):
            counts["latin"] += 1
    script, count = max(counts.items(), key=lambda item: item[1])
    return script if count else "other"


def _layer_text(layer: dict[str, Any]) -> str:
    return "\n".join(line.get("text", "") for line in layer.get("lines", [])).strip()


def _views_from_layers(layers: list[dict[str, Any]]) -> dict[str, Any]:
    views: dict[str, Any] = {}
    for layer in layers:
        text = _layer_text(layer)
        if not text:
            continue
        script = _dominant_script(text)
        if script == "arabic":
            key = "urdu"
        elif script == "devanagari":
            key = "devanagari"
        elif script == "latin" and layer.get("roman_mode") == "on":
            key = "roman_plain"
        elif script == "latin":
            key = "roman_diacritic"
        else:
            key = "other"
        views.setdefault(key, layer)
    return views


def parse_inline_verses(html_text: str) -> list[dict[str, Any]]:
    parser = InlineVerseParser()
    parser.feed(html_text)
    return parser.items


def parse_poem_page(html_text: str, expected_view: str | None) -> dict[str, Any]:
    outer = OuterPoemParser()
    outer.feed(html_text)
    if not outer.raw_content_html:
        raise ValueError("page has no #HtmlRawText data-html content")

    content = PoemContentParser()
    content.feed(outer.raw_content_html)
    views = _views_from_layers(content.layers)

    if expected_view == "roman" and not {"roman_plain", "roman_diacritic"} & views.keys():
        raise ValueError("Roman page did not expose a Roman text layer")
    if expected_view == "urdu" and "urdu" not in views:
        raise ValueError("Urdu page did not expose an Urdu text layer")

    return {"title": outer.title, "content_id": outer.content_id, "views": views}


def _slug_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path.rstrip("/")
    return path.rsplit("/", 1)[-1]


def _cache_path(cache_dir: Path, content_id: str, view: str) -> Path:
    return cache_dir / f"{content_id}.{view}.html"


def _canonical_poem_url(url: str, view: str) -> str:
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.replace("/ghazals/", "/kaafi/")
    query = "lang=ur" if view == "urdu" else ""
    return urllib.parse.urlunparse(
        (parsed.scheme or "https", parsed.netloc or "sufinama.org", path, "", query, "")
    )


def _fetch_or_cache(
    client: SufinamaClient,
    url: str,
    cache_path: Path,
    refresh: bool,
) -> tuple[str, str, int, bool]:
    if cache_path.exists() and not refresh:
        return cache_path.read_text(encoding="utf-8"), url, 200, True
    html_text, final_url, status = client.fetch(url)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    # pathlib.Path.write_text does not accept ``newline`` on every supported
    # Python runtime. Use Path.open so cache writes stay portable across the
    # project's macOS and Windows environments.
    with cache_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(html_text)
    return html_text, final_url, status, False


def _fetch_item(
    client: SufinamaClient,
    item: dict[str, str],
    cache_dir: Path,
    refresh: bool,
) -> dict[str, Any]:
    content_id = item["content_id"]
    record: dict[str, Any] = {
        "id": f"sufinama_{content_id}",
        "source_id": "source_sufinama_bulleh_catalog",
        "sufinama_content_id": content_id,
        "slug": _slug_from_url(item["url_roman"]),
        "catalog_title_roman": item["title_roman"],
        "catalog_title_urdu": item["title_urdu"],
        "source_urls": {"roman": item["url_roman"], "urdu": item["url_urdu"]},
        "views": {},
        "availability": {},
        "raw": {},
        "parser_version": PARSER_VERSION,
    }

    for view, url in (("roman", item["url_roman"]), ("urdu", item["url_urdu"])):
        path = _cache_path(cache_dir, content_id, view)
        final_url: str | None = None
        status: int | None = None
        from_cache: bool | None = None
        try:
            raw_html, final_url, status, from_cache = _fetch_or_cache(
                client, url, path, refresh
            )
            parsed = parse_poem_page(raw_html, view)
            if parsed["content_id"] and parsed["content_id"] != content_id:
                raise ValueError(
                    f"content id mismatch: catalog={content_id} page={parsed['content_id']}"
                )
            record["views"].update(parsed["views"])
            record["availability"][view] = {
                "status": "ok",
                "http_status": status,
                "final_url": final_url,
                "from_cache": from_cache,
            }
            record["raw"][view] = {
                "cache_file": path.name,
                "sha256": _sha256_text(raw_html),
            }
        except ValueError as exc:
            if "did not expose" not in str(exc):
                error: dict[str, Any] = {"status": "error", "error": str(exc)}
                if final_url is not None:
                    error["final_url"] = final_url
                if status is not None:
                    error["http_status"] = status
                if from_cache is not None:
                    error["from_cache"] = from_cache
                record["availability"][view] = error
                continue

            # Some catalog links redirect a requested ENG/URD view to another
            # language that is the only layer Sufinama actually serves. Keep
            # that returned witness and report the requested view honestly as
            # unavailable rather than misclassifying or discarding the text.
            parsed = parse_poem_page(raw_html, None)
            record["views"].update(parsed["views"])
            record["availability"][view] = {
                "status": "unavailable",
                "reason": str(exc),
                "http_status": status,
                "final_url": final_url,
                "from_cache": from_cache,
                "returned_layers": sorted(parsed["views"]),
            }
            record["raw"][view] = {
                "cache_file": path.name,
                "sha256": _sha256_text(raw_html),
            }
        except Exception as exc:  # noqa: BLE001 - preserve partial corpus and error detail.
            error: dict[str, Any] = {"status": "error", "error": str(exc)}
            if final_url is not None:
                error["final_url"] = final_url
            if status is not None:
                error["http_status"] = status
            if from_cache is not None:
                error["from_cache"] = from_cache
            record["availability"][view] = error

    return record


def _catalog_records(
    roman_items: list[dict[str, str]], urdu_items: list[dict[str, str]]
) -> list[dict[str, Any]]:
    roman_by_id = {item["content_id"]: item for item in roman_items}
    urdu_by_id = {item["content_id"]: item for item in urdu_items}
    if roman_by_id.keys() != urdu_by_id.keys():
        missing_urdu = sorted(roman_by_id.keys() - urdu_by_id.keys())
        missing_roman = sorted(urdu_by_id.keys() - roman_by_id.keys())
        raise ValueError(
            f"catalog language ID sets differ; missing Urdu={missing_urdu}, "
            f"missing Roman={missing_roman}"
        )

    records: list[dict[str, Any]] = []
    for rank, roman in enumerate(roman_items, start=1):
        urdu = urdu_by_id[roman["content_id"]]
        records.append(
            {
                "id": f"sufinama_{roman['content_id']}",
                "content_id": roman["content_id"],
                "source_id": "source_sufinama_bulleh_catalog",
                "rank_roman": rank,
                "title_roman": roman["title"],
                "title_urdu": urdu["title"],
                "url_roman": _canonical_poem_url(roman["url"], "roman"),
                "url_urdu": _canonical_poem_url(urdu["url"], "urdu"),
            }
        )
    return records


def _match_manifest(records: list[dict[str, Any]], path: Path) -> None:
    manifest: list[dict[str, Any]] = []
    for record in records:
        views = record.get("views", {})
        roman_layer = views.get("roman_plain") or views.get("roman_diacritic") or {}
        urdu_layer = views.get("urdu") or {}
        devanagari_layer = views.get("devanagari") or {}
        manifest.append(
            {
                "id": record["id"],
                "source_id": record["source_id"],
                "url": record["source_urls"]["roman"],
                "url_urdu": record["source_urls"]["urdu"],
                "roman_title": record["catalog_title_roman"],
                "urdu_title": record["catalog_title_urdu"],
                "roman_text": _layer_text(roman_layer),
                "urdu_text": _layer_text(urdu_layer),
                "devanagari_title": _first_layer_line(devanagari_layer),
                "devanagari_text": _layer_text(devanagari_layer),
            }
        )
    write_jsonl(path, manifest)


def _first_layer_line(layer: dict[str, Any]) -> str:
    for line in layer.get("lines", []):
        text = str(line.get("text") or "").strip()
        if text:
            return text
    return ""


def _alignment_signature(layer: dict[str, Any]) -> list[tuple[str, str, tuple[str, ...]]]:
    signature: list[tuple[str, str, tuple[str, ...]]] = []
    for line in layer.get("lines", []):
        mapping_ids = tuple(
            str(token.get("mapping_id") or "") for token in line.get("tokens", [])
        )
        signature.append(
            (
                str(line.get("stanza_id") or ""),
                str(line.get("line_id") or ""),
                mapping_ids,
            )
        )
    return signature


def _mapping_set_signature(layer: dict[str, Any]) -> list[tuple[str, str, tuple[str, ...]]]:
    return [
        (stanza, line, tuple(sorted(set(mapping_ids) - {""})))
        for stanza, line, mapping_ids in _alignment_signature(layer)
    ]


def _audit_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    layer_names = ("roman_plain", "roman_diacritic", "urdu", "devanagari", "other")
    availability_counts: dict[str, int] = {}
    layer_counts = {name: 0 for name in layer_names}
    raw_hashes: list[str] = []
    records_with_mappings = 0
    paired_records = 0
    line_id_matches = 0
    mapping_id_matches = 0

    for record in records:
        for availability in record.get("availability", {}).values():
            status = str(availability.get("status") or "unknown")
            availability_counts[status] = availability_counts.get(status, 0) + 1

        views = record.get("views", {})
        for name in layer_names:
            if (views.get(name) or {}).get("lines"):
                layer_counts[name] += 1

        hashes = [
            str(raw.get("sha256") or "")
            for raw in record.get("raw", {}).values()
            if raw.get("sha256")
        ]
        raw_hashes.extend(hashes)

        all_mapping_ids = [
            token.get("mapping_id")
            for layer in views.values()
            for line in layer.get("lines", [])
            for token in line.get("tokens", [])
            if token.get("mapping_id")
        ]
        if all_mapping_ids:
            records_with_mappings += 1

        roman = views.get("roman_plain") or views.get("roman_diacritic")
        urdu = views.get("urdu")
        if not roman or not urdu:
            continue
        paired_records += 1
        roman_signature = _alignment_signature(roman)
        urdu_signature = _alignment_signature(urdu)
        roman_line_ids = [(stanza, line) for stanza, line, _ in roman_signature]
        urdu_line_ids = [(stanza, line) for stanza, line, _ in urdu_signature]
        if roman_line_ids == urdu_line_ids:
            line_id_matches += 1
        if _mapping_set_signature(roman) == _mapping_set_signature(urdu):
            mapping_id_matches += 1

    ids = [str(record.get("id") or "") for record in records]
    return {
        "records": len(records),
        "unique_ids": len(set(ids)),
        "duplicate_ids": sorted({record_id for record_id in ids if ids.count(record_id) > 1}),
        "availability_counts": availability_counts,
        "layer_record_counts": layer_counts,
        "raw_snapshots_recorded": len(raw_hashes),
        "distinct_raw_sha256": len(set(raw_hashes)),
        "records_with_mapping_ids": records_with_mappings,
        "roman_urdu_pair_records": paired_records,
        "roman_urdu_line_id_matches": line_id_matches,
        "roman_urdu_mapping_id_matches": mapping_id_matches,
    }


def _text_index_url(config: dict[str, Any], view: str = "default") -> str:
    base = f"{BASE_URL}/poets/bulleh-shah/{config['index_path']}"
    if view == "urdu":
        return f"{base}?lang=ur"
    if view == "hindi":
        return f"{base}?lang=hi"
    return base


def _url_for_text_view(url: str, view: str) -> str:
    parsed = urllib.parse.urlparse(url)
    query = "lang=ur" if view == "urdu" else "lang=hi" if view == "hindi" else ""
    return urllib.parse.urlunparse(
        (parsed.scheme or "https", parsed.netloc or "sufinama.org", parsed.path, "", query, "")
    )


def _text_index_cache_path(cache_dir: Path, category: str, view: str) -> Path:
    return cache_dir / f"text-index.{category}.{view}.html"


def _text_item_cache_path(
    cache_dir: Path,
    category: str,
    content_id: str,
    view: str,
) -> Path:
    return cache_dir / f"text-item.{category}.{content_id}.{view}.html"


def _text_catalog_record(
    config: dict[str, Any],
    rank: int,
    item: dict[str, Any],
) -> dict[str, Any]:
    category = str(config["category"])
    content_id = str(item["content_id"])
    index_url = _text_index_url(config)
    slug = str(item.get("slug") or _slug_from_url(str(item.get("url") or index_url)))
    if config["mode"] == "inline":
        source_url = f"{index_url}#{slug}"
    else:
        source_url = str(item["url"])
    return {
        "id": f"sufinama_text_item_{category}_{content_id}",
        "content_id": content_id,
        "source_id": "source_sufinama_bulleh_catalog",
        "poet_id": "bulleh_shah",
        "category": category,
        "rank_in_category": rank,
        "catalog_title": str(item.get("title") or ""),
        "slug": slug,
        "source_url": source_url,
        "index_url": index_url,
        "content_mode": str(config["mode"]),
        "review_status": "needs_review",
        "canonical_work_id": None,
    }


def discover_text_catalog(
    client: SufinamaClient,
    cache_dir: Path,
    refresh: bool,
) -> list[dict[str, Any]]:
    catalog: list[dict[str, Any]] = []
    for config in TEXT_CATEGORY_CONFIGS:
        category = str(config["category"])
        index_url = _text_index_url(config)
        raw_html, _, _, _ = _fetch_or_cache(
            client,
            index_url,
            _text_index_cache_path(cache_dir, category, "default"),
            refresh,
        )
        if config["mode"] == "inline":
            items = parse_inline_verses(raw_html)
        else:
            items, _ = _parse_catalog(raw_html, (f"/{category}/",))

        expected = int(config["expected_count"])
        if len(items) != expected:
            raise ValueError(
                f"expected {expected} Sufinama {category} records; discovered {len(items)}"
            )
        content_ids = [str(item.get("content_id") or "") for item in items]
        if len(set(content_ids)) != expected or "" in content_ids:
            raise ValueError(f"Sufinama {category} catalog has missing or duplicate content IDs")

        for rank, item in enumerate(items, start=1):
            catalog.append(_text_catalog_record(config, rank, item))

    if len(catalog) != TEXT_EXPECTED_COUNT:
        raise ValueError(
            f"expected {TEXT_EXPECTED_COUNT} non-kaafi Sufinama texts; discovered {len(catalog)}"
        )
    return catalog


def _base_text_record(item: dict[str, Any]) -> dict[str, Any]:
    category = str(item["category"])
    content_id = str(item["content_id"])
    base_url = str(item["index_url"] if item["content_mode"] == "inline" else item["source_url"])
    return {
        "id": f"sufinama_text_{category}_{content_id}",
        "source_id": str(item["source_id"]),
        "poet_id": "bulleh_shah",
        "source_category": category,
        "work_type": category,
        "sufinama_content_id": content_id,
        "slug": str(item["slug"]),
        "catalog_title": str(item.get("catalog_title") or ""),
        "rank_in_category": int(item["rank_in_category"]),
        "content_mode": str(item["content_mode"]),
        "source_urls": {
            view: _url_for_text_view(base_url, view) for view in TEXT_REQUEST_VIEWS
        },
        "views": {},
        "responses": {},
        "availability": {},
        "raw": {},
        "parser_version": TEXT_PARSER_VERSION,
        "review_status": "needs_review",
        "canonical_work_id": None,
        "training_eligibility": "needs_source_and_variant_review",
    }


def _text_view_status(view: str, returned_views: dict[str, Any]) -> tuple[str, str | None]:
    expected_layer = {"urdu": "urdu", "hindi": "devanagari"}.get(view)
    if expected_layer and expected_layer not in returned_views:
        return "unavailable", f"requested {view} view did not expose a {expected_layer} layer"
    return "ok", None


def _add_text_response(
    record: dict[str, Any],
    view: str,
    parsed_views: dict[str, Any],
    cache_path: Path,
    raw_html: str,
    final_url: str,
    status: int,
    from_cache: bool,
) -> None:
    for layer_name, layer in parsed_views.items():
        record["views"].setdefault(layer_name, layer)
    record["responses"][view] = {"views": parsed_views}
    availability_status, reason = _text_view_status(view, parsed_views)
    availability: dict[str, Any] = {
        "status": availability_status,
        "http_status": status,
        "final_url": final_url,
        "from_cache": from_cache,
        "returned_layers": sorted(parsed_views),
    }
    if reason:
        availability["reason"] = reason
    record["availability"][view] = availability
    record["raw"][view] = {
        "cache_file": cache_path.name,
        "sha256": _sha256_text(raw_html),
    }


def _fetch_text_detail_item(
    client: SufinamaClient,
    item: dict[str, Any],
    cache_dir: Path,
    refresh: bool,
) -> dict[str, Any]:
    record = _base_text_record(item)
    category = str(item["category"])
    content_id = str(item["content_id"])
    for view, url in record["source_urls"].items():
        cache_path = _text_item_cache_path(cache_dir, category, content_id, view)
        try:
            raw_html, final_url, status, from_cache = _fetch_or_cache(
                client, url, cache_path, refresh
            )
            parsed = parse_poem_page(raw_html, None)
            if parsed["content_id"] and parsed["content_id"] != content_id:
                raise ValueError(
                    f"content id mismatch: catalog={content_id} page={parsed['content_id']}"
                )
            _add_text_response(
                record,
                view,
                parsed["views"],
                cache_path,
                raw_html,
                final_url,
                status,
                from_cache,
            )
        except Exception as exc:  # noqa: BLE001 - preserve partial witness and error detail.
            record["availability"][view] = {"status": "error", "error": str(exc)}
    return record


def _fetch_inline_text_records(
    client: SufinamaClient,
    items: list[dict[str, Any]],
    cache_dir: Path,
    refresh: bool,
) -> list[dict[str, Any]]:
    if not items:
        return []
    config = next(config for config in TEXT_CATEGORY_CONFIGS if config["category"] == "doha")
    parsed_by_view: dict[str, dict[str, dict[str, Any]]] = {}
    response_metadata: dict[str, tuple[Path, str, str, int, bool]] = {}
    for view in TEXT_REQUEST_VIEWS:
        url = _text_index_url(config, view)
        cache_path = _text_index_cache_path(cache_dir, "doha", view)
        raw_html, final_url, status, from_cache = _fetch_or_cache(
            client, url, cache_path, refresh
        )
        parsed_items = parse_inline_verses(raw_html)
        if len(parsed_items) != int(config["expected_count"]):
            raise ValueError(
                f"expected {config['expected_count']} inline doha records in {view} view; "
                f"parsed {len(parsed_items)}"
            )
        parsed_by_view[view] = {
            str(parsed["content_id"]): parsed for parsed in parsed_items
        }
        response_metadata[view] = (
            cache_path,
            raw_html,
            final_url,
            status,
            from_cache,
        )

    records: list[dict[str, Any]] = []
    for item in items:
        record = _base_text_record(item)
        content_id = str(item["content_id"])
        for view in TEXT_REQUEST_VIEWS:
            parsed = parsed_by_view[view].get(content_id)
            if parsed is None:
                record["availability"][view] = {
                    "status": "error",
                    "error": f"inline {view} page omitted content id {content_id}",
                }
                continue
            cache_path, raw_html, final_url, status, from_cache = response_metadata[view]
            _add_text_response(
                record,
                view,
                parsed["views"],
                cache_path,
                raw_html,
                final_url,
                status,
                from_cache,
            )
        records.append(record)
    return records


def _text_match_manifest(records: list[dict[str, Any]], path: Path) -> None:
    manifest: list[dict[str, Any]] = []
    for record in records:
        views = record.get("views", {})
        roman = views.get("roman_plain") or views.get("roman_diacritic") or {}
        urdu = views.get("urdu") or {}
        devanagari = views.get("devanagari") or {}
        manifest.append(
            {
                "id": record["id"],
                "source_id": record["source_id"],
                "url": record["source_urls"]["default"],
                "url_urdu": record["source_urls"]["urdu"],
                "roman_title": record.get("catalog_title", ""),
                "urdu_title": _first_layer_line(urdu),
                "roman_text": _layer_text(roman),
                "urdu_text": _layer_text(urdu),
                "devanagari_title": _first_layer_line(devanagari),
                "devanagari_text": _layer_text(devanagari),
            }
        )
    write_jsonl(path, manifest)


def _audit_text_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    categories: dict[str, int] = {}
    availability: dict[str, int] = {}
    layer_counts = {
        name: 0
        for name in ("roman_plain", "roman_diacritic", "urdu", "devanagari", "other")
    }
    raw_files: set[str] = set()
    raw_hashes: set[str] = set()
    records_with_mappings = 0
    for record in records:
        category = str(record.get("source_category") or "unknown")
        categories[category] = categories.get(category, 0) + 1
        for view_status in record.get("availability", {}).values():
            status = str(view_status.get("status") or "unknown")
            availability[status] = availability.get(status, 0) + 1
        for layer_name in layer_counts:
            if (record.get("views", {}).get(layer_name) or {}).get("lines"):
                layer_counts[layer_name] += 1
        mappings = [
            token.get("mapping_id")
            for layer in record.get("views", {}).values()
            for line in layer.get("lines", [])
            for token in line.get("tokens", [])
            if token.get("mapping_id")
        ]
        if mappings:
            records_with_mappings += 1
        for raw in record.get("raw", {}).values():
            if raw.get("cache_file"):
                raw_files.add(str(raw["cache_file"]))
            if raw.get("sha256"):
                raw_hashes.add(str(raw["sha256"]))
    ids = [str(record.get("id") or "") for record in records]
    return {
        "records": len(records),
        "unique_ids": len(set(ids)),
        "duplicate_ids": sorted({record_id for record_id in ids if ids.count(record_id) > 1}),
        "category_record_counts": categories,
        "availability_counts": availability,
        "layer_record_counts": layer_counts,
        "raw_snapshot_files": len(raw_files),
        "distinct_raw_sha256": len(raw_hashes),
        "records_with_mapping_ids": records_with_mappings,
    }


def acquire_sufinama_texts(
    root: Path,
    output_path: Path,
    catalog_output_path: Path,
    match_output_path: Path,
    cache_dir: Path,
    delay_seconds: float = 0.75,
    workers: int = 3,
    limit: int | None = None,
    refresh: bool = False,
    discover_only: bool = False,
    user_agent: str = DEFAULT_USER_AGENT,
    transport: str = "urllib",
    offline: bool = False,
) -> dict[str, Any]:
    client = SufinamaClient(
        user_agent,
        delay_seconds,
        transport=transport,
        offline=offline,
    )
    if offline:
        catalog = read_jsonl(catalog_output_path)
        if not catalog:
            raise ValueError(f"offline text catalog is missing or empty: {catalog_output_path}")
    else:
        catalog = discover_text_catalog(client, cache_dir, refresh)
        write_jsonl(catalog_output_path, catalog)

    if len(catalog) != TEXT_EXPECTED_COUNT:
        raise ValueError(
            f"expected {TEXT_EXPECTED_COUNT} cataloged non-kaafi texts; found {len(catalog)}"
        )
    category_counts = {
        category: sum(1 for item in catalog if item.get("category") == category)
        for category in (str(config["category"]) for config in TEXT_CATEGORY_CONFIGS)
    }
    for config in TEXT_CATEGORY_CONFIGS:
        category = str(config["category"])
        expected = int(config["expected_count"])
        if category_counts[category] != expected:
            raise ValueError(
                f"catalog has {category_counts[category]} {category} records; expected {expected}"
            )
    if discover_only:
        return {"catalog_items": len(catalog), "records": 0, "errors": 0, "unavailable": 0}

    selected = catalog[:limit] if limit is not None else catalog
    inline_items = [item for item in selected if item.get("content_mode") == "inline"]
    detail_items = [item for item in selected if item.get("content_mode") == "detail"]
    records_by_id: dict[tuple[str, str], dict[str, Any]] = {}

    for record in _fetch_inline_text_records(client, inline_items, cache_dir, refresh):
        records_by_id[(record["source_category"], record["sufinama_content_id"])] = record
    if inline_items:
        print(f"Fetched and parsed {len(inline_items)} inline doha witnesses", flush=True)

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {
            executor.submit(_fetch_text_detail_item, client, item, cache_dir, refresh): item
            for item in detail_items
        }
        for completed_count, future in enumerate(as_completed(futures), start=1):
            record = future.result()
            records_by_id[(record["source_category"], record["sufinama_content_id"])] = record
            if (
                completed_count == 1
                or completed_count % 5 == 0
                or completed_count == len(detail_items)
            ):
                print(
                    f"Fetched and parsed {completed_count}/{len(detail_items)} detail witnesses",
                    flush=True,
                )

    records = [
        records_by_id[(str(item["category"]), str(item["content_id"]))]
        for item in selected
    ]
    write_jsonl(output_path, records)
    private_manifest = output_path.with_name("sufinama_texts_match_manifest.jsonl")
    _text_match_manifest(records, private_manifest)
    match_source_manifest(root, private_manifest, match_output_path, top_n=5)

    errors = sum(
        1
        for record in records
        for status in record.get("availability", {}).values()
        if status.get("status") == "error"
    )
    unavailable = sum(
        1
        for record in records
        for status in record.get("availability", {}).values()
        if status.get("status") == "unavailable"
    )
    audit = _audit_text_records(records)

    def manifest_path(path: Path) -> str:
        try:
            return path.relative_to(root).as_posix()
        except ValueError:
            return path.as_posix()

    run_manifest = {
        "source": "Sufinama Bulleh Shah non-kaafi textual categories",
        "started_or_completed_at": datetime.now(timezone.utc).isoformat(),
        "parser_version": TEXT_PARSER_VERSION,
        "catalog_items": len(catalog),
        "records_requested": len(selected),
        "records_written": len(records),
        "view_errors": errors,
        "view_unavailable": unavailable,
        "offline_rebuild": offline,
        "audit": audit,
        "output_path": manifest_path(output_path),
        "catalog_output_path": manifest_path(catalog_output_path),
        "match_output_path": manifest_path(match_output_path),
        "cache_dir": manifest_path(cache_dir),
    }
    write_json(output_path.with_name("sufinama_texts_run.json"), run_manifest)
    return {
        "catalog_items": len(catalog),
        "records": len(records),
        "errors": errors,
        "unavailable": unavailable,
        "audit": audit,
    }


def acquire_sufinama_corpus(
    root: Path,
    output_path: Path,
    catalog_output_path: Path,
    match_output_path: Path,
    cache_dir: Path,
    delay_seconds: float = 0.75,
    workers: int = 3,
    limit: int | None = None,
    refresh: bool = False,
    discover_only: bool = False,
    user_agent: str = DEFAULT_USER_AGENT,
    transport: str = "urllib",
    offline: bool = False,
) -> dict[str, Any]:
    client = SufinamaClient(
        user_agent,
        delay_seconds,
        transport=transport,
        offline=offline,
    )
    if offline:
        catalog = read_jsonl(catalog_output_path)
        if not catalog:
            raise ValueError(f"offline catalog is missing or empty: {catalog_output_path}")
    else:
        roman_items = discover_catalog(client, ENGLISH_INDEX)
        urdu_items = discover_catalog(client, URDU_INDEX)
        catalog = _catalog_records(roman_items, urdu_items)

    if len(catalog) != 76:
        raise ValueError(f"expected 76 paired Sufinama kaafi; discovered {len(catalog)}")

    if not offline:
        write_jsonl(catalog_output_path, catalog)
    if discover_only:
        return {"catalog_items": len(catalog), "records": 0, "errors": 0}

    selected = catalog[:limit] if limit is not None else catalog
    records_by_id: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = {
            executor.submit(_fetch_item, client, item, cache_dir, refresh): item
            for item in selected
        }
        for completed_count, future in enumerate(as_completed(futures), start=1):
            record = future.result()
            records_by_id[record["sufinama_content_id"]] = record
            if completed_count == 1 or completed_count % 5 == 0 or completed_count == len(selected):
                print(f"Fetched and parsed {completed_count}/{len(selected)} witnesses", flush=True)

    records = [records_by_id[item["content_id"]] for item in selected]
    write_jsonl(output_path, records)

    private_manifest = output_path.with_name("sufinama_match_manifest.jsonl")
    _match_manifest(records, private_manifest)
    match_source_manifest(root, private_manifest, match_output_path, top_n=5)

    errors = sum(
        1
        for record in records
        for availability in record.get("availability", {}).values()
        if availability.get("status") == "error"
    )
    unavailable = sum(
        1
        for record in records
        for availability in record.get("availability", {}).values()
        if availability.get("status") == "unavailable"
    )
    audit = _audit_records(records)

    def manifest_path(path: Path) -> str:
        try:
            return path.relative_to(root).as_posix()
        except ValueError:
            return path.as_posix()

    run_manifest = {
        "source": "Sufinama Bulleh Shah kaafi",
        "started_or_completed_at": datetime.now(timezone.utc).isoformat(),
        "parser_version": PARSER_VERSION,
        "catalog_items": len(catalog),
        "records_requested": len(selected),
        "records_written": len(records),
        "view_errors": errors,
        "view_unavailable": unavailable,
        "offline_rebuild": offline,
        "audit": audit,
        "output_path": manifest_path(output_path),
        "catalog_output_path": manifest_path(catalog_output_path),
        "match_output_path": manifest_path(match_output_path),
        "cache_dir": manifest_path(cache_dir),
    }
    write_json(output_path.with_name("sufinama_run.json"), run_manifest)
    return {
        "catalog_items": len(catalog),
        "records": len(records),
        "errors": errors,
        "unavailable": unavailable,
        "audit": audit,
    }
