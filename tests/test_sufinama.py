from __future__ import annotations

import html
import tempfile
import unittest
from pathlib import Path

from abshaar.sufinama import (
    SufinamaClient,
    _audit_records,
    _catalog_records,
    _fetch_or_cache,
    _parse_catalog,
    _text_view_status,
    parse_inline_verses,
    parse_poem_page,
)


class SufinamaParserTest(unittest.TestCase):
    def test_offline_client_never_attempts_network(self) -> None:
        client = SufinamaClient("test", 0, offline=True)
        with self.assertRaisesRegex(RuntimeError, "offline mode cache miss"):
            client.fetch("https://example.test/missing")

    def test_audit_reports_layer_and_alignment_coverage(self) -> None:
        line = {
            "stanza_id": "1",
            "line_id": "1",
            "text": "example",
            "tokens": [{"mapping_id": "m1", "text": "example"}],
        }
        records = [
            {
                "id": "one",
                "views": {
                    "roman_plain": {"lines": [line]},
                    "urdu": {"lines": [line]},
                },
                "availability": {"roman": {"status": "ok"}, "urdu": {"status": "ok"}},
                "raw": {"roman": {"sha256": "a"}, "urdu": {"sha256": "b"}},
            }
        ]
        audit = _audit_records(records)
        self.assertEqual(audit["records"], 1)
        self.assertEqual(audit["layer_record_counts"]["urdu"], 1)
        self.assertEqual(audit["records_with_mapping_ids"], 1)
        self.assertEqual(audit["roman_urdu_line_id_matches"], 1)
        self.assertEqual(audit["roman_urdu_mapping_id_matches"], 1)

    def test_fetch_cache_write_is_cross_platform_and_reusable(self) -> None:
        class FakeClient:
            calls = 0

            def fetch(self, url: str) -> tuple[str, str, int]:
                self.calls += 1
                return "first\r\nsecond", f"{url}?final=1", 200

        client = FakeClient()
        with tempfile.TemporaryDirectory() as directory:
            cache_path = Path(directory) / "nested" / "page.html"
            fetched = _fetch_or_cache(client, "https://example.test/page", cache_path, False)
            self.assertEqual(fetched, ("first\r\nsecond", "https://example.test/page?final=1", 200, False))
            self.assertTrue(cache_path.exists())

            cached = _fetch_or_cache(client, "https://example.test/page", cache_path, False)
            self.assertEqual(cached, ("first\nsecond", "https://example.test/page", 200, True))
            self.assertEqual(client.calls, 1)

    def test_catalog_parser_keeps_uuid_url_title_and_next_page(self) -> None:
        catalog_html = """
        <div class="contentListItems nwPoetListBody">
          <a class="favorite" data-type="0" data-id="uuid-1"></a>
          <a title="roman title" href="/kaafi/example"><h3>roman title</h3></a>
        </div>
        <div class="contentLoadMorePaging" data-url="/PoetCollection?pageNumber=2"></div>
        """
        items, next_url = _parse_catalog(catalog_html)
        self.assertEqual(items[0]["content_id"], "uuid-1")
        self.assertEqual(items[0]["url"], "https://sufinama.org/kaafi/example")
        self.assertEqual(items[0]["title"], "roman title")
        self.assertEqual(next_url, "https://sufinama.org/PoetCollection?pageNumber=2")

    def test_catalog_parser_accepts_non_kaafi_category_paths(self) -> None:
        catalog_html = """
        <div class="contentListItems nwPoetListBody">
          <a class="favorite" data-type="0" data-id="uuid-shabad"></a>
          <a title="example" href="/shabad/example"><h3>example</h3></a>
        </div>
        """
        items, _ = _parse_catalog(catalog_html, ("/shabad/",))
        self.assertEqual(items[0]["content_id"], "uuid-shabad")
        self.assertEqual(items[0]["url"], "https://sufinama.org/shabad/example")

    def test_inline_parser_preserves_separate_verse_ids_layers_and_tokens(self) -> None:
        page = """
        <div class="sherSection" id="first-doha">
          <div class="sherLines">
            <div class='pMC' data-roman='off'><div class='w' data-p='1'>
              <p data-l='1'><span data-m='m1'>muñh </span><span data-m='m2'>dikhlāve</span></p>
            </div></div>
            <div class='pMC' data-roman='on'><div class='w' data-p='1'>
              <p data-l='1'><span data-m='m1'>munh </span><span data-m='m2'>dikhlawe</span></p>
            </div></div>
          </div>
          <a class="favorite" data-type="0" data-id="uuid-1"></a>
        </div>
        <div class="sherSection" id="second-doha">
          <div class="sherLines">
            <div class='pMC' data-roman='off'><div class='w' data-p='1'>
              <p data-l='1'><span data-m='m3'>خدا</span></p>
            </div></div>
          </div>
          <a class="favorite" data-type="0" data-id="uuid-2"></a>
        </div>
        """
        parsed = parse_inline_verses(page)
        self.assertEqual([item["content_id"] for item in parsed], ["uuid-1", "uuid-2"])
        self.assertEqual(parsed[0]["slug"], "first-doha")
        self.assertEqual(parsed[0]["views"]["roman_plain"]["lines"][0]["line_id"], "1")
        self.assertEqual(
            parsed[0]["views"]["roman_diacritic"]["lines"][0]["tokens"][1]["mapping_id"],
            "m2",
        )
        self.assertIn("urdu", parsed[1]["views"])

    def test_requested_text_view_reports_source_unavailable_without_dropping_layers(self) -> None:
        status, reason = _text_view_status("urdu", {"devanagari": {"lines": []}})
        self.assertEqual(status, "unavailable")
        self.assertIn("urdu", reason or "")

    def test_poem_parser_preserves_three_layers_and_alignment_ids(self) -> None:
        nested = """
        <div class='pMC' data-roman='off'><div class='w' data-p='1'>
          <p data-l='1'><span data-m='m1'>rāñjhā </span><span data-m='m2'>kardī</span></p>
        </div></div>
        <div class='pMC' data-roman='on'><div class='w' data-p='1'>
          <p data-l='1'><span data-m='m1'>ranjha </span><span data-m='m2'>kardi</span></p>
        </div></div>
        """
        page = (
            '<h1>Example</h1><div data-contentId="uuid-1"></div>'
            f'<input id="HtmlRawText" data-html="{html.escape(nested, quote=True)}">'
        )
        parsed = parse_poem_page(page, "roman")
        self.assertEqual(parsed["content_id"], "uuid-1")
        self.assertEqual(parsed["views"]["roman_diacritic"]["lines"][0]["line_id"], "1")
        self.assertEqual(
            parsed["views"]["roman_plain"]["lines"][0]["tokens"][1]["mapping_id"],
            "m2",
        )

        urdu_nested = """
        <div class='pMC' data-roman='off'><div class='w' data-p='1'>
          <p data-l='1'><span data-m='m1'>رانجھا </span><span data-m='m2'>کردی</span></p>
        </div></div>
        """
        urdu_page = (
            '<h1>مثال</h1><div data-contentId="uuid-1"></div>'
            f'<input id="HtmlRawText" data-html="{html.escape(urdu_nested, quote=True)}">'
        )
        urdu = parse_poem_page(urdu_page, "urdu")
        self.assertEqual(urdu["views"]["urdu"]["lines"][0]["stanza_id"], "1")
        self.assertEqual(urdu["views"]["urdu"]["lines"][0]["tokens"][0]["mapping_id"], "m1")

    def test_catalog_pairs_by_uuid_not_order(self) -> None:
        roman = [
            {"content_id": "a", "title": "A", "url": "https://sufinama.org/kaafi/a"},
            {"content_id": "b", "title": "B", "url": "https://sufinama.org/kaafi/b"},
        ]
        urdu = [
            {"content_id": "b", "title": "ب", "url": "https://sufinama.org/kaafi/b?lang=ur"},
            {"content_id": "a", "title": "ا", "url": "https://sufinama.org/kaafi/a?lang=ur"},
        ]
        paired = _catalog_records(roman, urdu)
        self.assertEqual(paired[0]["title_urdu"], "ا")
        self.assertEqual(paired[1]["title_urdu"], "ب")

    def test_catalog_normalizes_redirecting_ghazal_urls(self) -> None:
        roman = [
            {
                "content_id": "a",
                "title": "A",
                "url": "https://sufinama.org/ghazals/bulleh-shah-kaafi-13",
            }
        ]
        urdu = [
            {
                "content_id": "a",
                "title": "ا",
                "url": "https://sufinama.org/ghazals/bulleh-shah-kaafi-13?lang=ur",
            }
        ]
        paired = _catalog_records(roman, urdu)
        self.assertEqual(
            paired[0]["url_roman"],
            "https://sufinama.org/kaafi/bulleh-shah-kaafi-13",
        )
        self.assertEqual(
            paired[0]["url_urdu"],
            "https://sufinama.org/kaafi/bulleh-shah-kaafi-13?lang=ur",
        )

    def test_devanagari_is_not_accepted_as_a_roman_layer(self) -> None:
        nested = """
        <div class='pMC' data-roman='off'><div class='w' data-p='1'>
          <p data-l='1'><span data-m='m1'>झूठ आखां</span></p>
        </div></div>
        """
        page = (
            '<h1>Example</h1><div data-contentId="uuid-1"></div>'
            f'<input id="HtmlRawText" data-html="{html.escape(nested, quote=True)}">'
        )
        with self.assertRaisesRegex(ValueError, "Roman page"):
            parse_poem_page(page, "roman")
        parsed = parse_poem_page(page, None)
        self.assertIn("devanagari", parsed["views"])

    def test_mixed_roman_layer_uses_dominant_script(self) -> None:
        nested = """
        <div class='pMC' data-roman='off'><div class='w' data-p='1'>
          <p data-l='1'><span data-m='m1'>jit vall vekhan ut vall ohi कसम ose di</span></p>
        </div></div>
        """
        page = (
            '<h1>Example</h1><div data-contentId="uuid-1"></div>'
            f'<input id="HtmlRawText" data-html="{html.escape(nested, quote=True)}">'
        )
        parsed = parse_poem_page(page, "roman")
        self.assertIn("roman_diacritic", parsed["views"])


if __name__ == "__main__":
    unittest.main()
