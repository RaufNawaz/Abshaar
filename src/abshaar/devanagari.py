"""Approximate Devanagari→Roman transliteration, FOR MATCHING ONLY.

This is a comparison key, not a scholarly transliteration: no schwa-deletion
model, single letters for long vowels, anusvara/candrabindu flattened to `n`.
It exists so Devanagari-only witnesses can be fuzzily compared against the
project's Roman lines. Never store its output as witness text, and never let
a similarity derived from it reach 1.0 (the auto-merge threshold).
"""

from __future__ import annotations

import unicodedata


VIRAMA = "्"
NUKTA = "़"

INDEPENDENT_VOWELS = {
    "अ": "a", "आ": "a", "इ": "i", "ई": "i", "उ": "u", "ऊ": "u",
    "ऋ": "ri", "ॠ": "ri", "ऌ": "li", "ए": "e", "ऐ": "ai", "ओ": "o",
    "औ": "au", "ऑ": "o", "ऍ": "e", "ऎ": "e", "ऒ": "o",
}

MATRAS = {
    "ा": "a", "ि": "i", "ी": "i", "ु": "u", "ू": "u",
    "ृ": "ri", "ॄ": "ri", "ॅ": "e", "ॆ": "e", "े": "e",
    "ै": "ai", "ॉ": "o", "ॊ": "o", "ो": "o", "ौ": "au",
}

CONSONANTS = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "n",
    "च": "ch", "छ": "chh", "ज": "j", "झ": "jh", "ञ": "n",
    "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "ळ": "l", "व": "v",
    "श": "sh", "ष": "sh", "स": "s", "ह": "h",
    "क़": "q", "ख़": "kh", "ग़": "gh", "ज़": "z", "ड़": "r", "ढ़": "rh",
    "फ़": "f", "य़": "y", "ऱ": "r", "ऴ": "l", "ऩ": "n",
}

SIGNS = {
    "ं": "n",  # anusvara
    "ँ": "n",  # candrabindu
    "ः": "h",  # visarga
    "ऽ": "",
}

DIGITS = {chr(0x0966 + i): str(i) for i in range(10)}
PUNCTUATION = {"।": " ", "॥": " ", "॰": " "}

# NFC decomposes the precomposed nukta letters (क़ ख़ ग़ ज़ ड़ ढ़ फ़ य़) into
# base + combining nukta, so the nukta arrives as its own character and must
# upgrade the consonant just emitted.
NUKTA_UPGRADES = {"k": "q", "j": "z", "ph": "f", "d": "r", "dh": "rh"}


def transliterate_devanagari(text: str) -> str:
    text = unicodedata.normalize("NFC", text)
    out: list[str] = []
    pending_inherent = False

    def flush() -> None:
        nonlocal pending_inherent
        if pending_inherent:
            out.append("a")
            pending_inherent = False

    for character in text:
        if character in CONSONANTS:
            flush()
            out.append(CONSONANTS[character])
            pending_inherent = True
        elif character in MATRAS:
            out.append(MATRAS[character])
            pending_inherent = False
        elif character == VIRAMA:
            pending_inherent = False
        elif character == NUKTA:
            if out and out[-1] in NUKTA_UPGRADES:
                out[-1] = NUKTA_UPGRADES[out[-1]]
        elif character in INDEPENDENT_VOWELS:
            flush()
            out.append(INDEPENDENT_VOWELS[character])
        elif character in SIGNS:
            flush()
            out.append(SIGNS[character])
        elif character in DIGITS:
            flush()
            out.append(DIGITS[character])
        elif character in PUNCTUATION:
            flush()
            out.append(PUNCTUATION[character])
        else:
            flush()
            out.append(character)
    flush()
    return "".join(out)
