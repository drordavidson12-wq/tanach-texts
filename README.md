# tanach-texts

The Hebrew Tanakh (all 39 books) with niqqud, and with niqqud and te'amim, as plain JSON.
Taken directly from the **Unicode/XML Leningrad Codex (UXLC)** published by [tanach.us](https://tanach.us). Public Domain.

## Files
| Path | Content |
|---|---|
| `tanakh/<book>.json` | Verses with niqqud: `{"book": "בראשית", "chapters": [["verse 1", "verse 2", ...], ...]}` |
| `tanakh-teamim/<book>.json` | Same structure, verses with niqqud **and** te'amim |
| `source.json` | The exact source file: version, build, download URL and SHA-256 |
| `scripts/uxlc.py` | Rebuilds both folders from the UXLC XML files |

- `chapters[0][0]` is chapter 1, verse 1.
- `<book>` is the English book name in lower case with `_` for spaces: `genesis`, `i_samuel`, `song_of_songs`.

## About the text (important for copying)
- **The Hebrew characters are exactly as in the UXLC XML files.** No Unicode normalization. **Do not apply Unicode normalization (NFC/NFKC) when copying:** it reorders the vowel and accent marks. The source also uses the invisible character U+034F (combining grapheme joiner) in some words, for example `יְרוּשָׁלָֽ͏ִם`, to keep two vowels under one letter in the right order. Copy it as is.
- **`tanakh-teamim/`:** every word exactly as in the source, with niqqud and te'amim.
- **`tanakh/`:** the same text with only the te'amim (Unicode U+0591–U+05AF) removed. Everything else stays: niqqud, **meteg** (the small vertical line, e.g. `הָרָֽעַשׁ`), maqaf, sof pasuq and paseq.
- **Ketiv and qere:** the ketiv appears without niqqud, followed by the qere with niqqud in square brackets: `הוצא [הַיְצֵא]`.
- **Parasha breaks:** in `tanakh-teamim/` the open and closed parasha marks appear as `(פ)` and `(ס)`. In `tanakh/` they are not included.
- **Large letters** (e.g. the ע and ד of שמע ישראל) are plain letters here. Editorial note markers from the XML are not included.
- **The text follows the Leningrad Codex**, so in a few places it differs from some printed editions. For example `ויחראף` (Numbers 12:9) and `הללויה` (Psalms 149–150) are written as one word, and the repeated verse at the end of Lamentations and Ecclesiastes is not included.

## Verse numbering
The verses use the **common Jewish numbering** (as in Sefaria and most printed Tanakhs). The Leningrad manuscript numbers three places differently. There, only the division between verses was joined, and no character was changed:
| Here | In UXLC |
|---|---|
| Exodus 20:13 (לא תרצח… לא תענה) | 20:13–16 |
| Deuteronomy 5:17 (לא תרצח… לא תענה) | 5:17–20 |
| Numbers 26:1 starts with "וַיְהִי אַחֲרֵי הַמַּגֵּפָה" | 25:19 |

## Source and license
| What | Source | License |
|---|---|---|
| `tanakh/`, `tanakh-teamim/` | Unicode/XML Leningrad Codex, UXLC 2.6 (build 27.7, Oct 2026), [tanach.us](https://tanach.us), file [Tanach.xml.zip](https://tanach.us/Books/Tanach.xml.zip) (SHA-256 in `source.json`) | **Public Domain.** The license in the zip: *"All biblical Hebrew text, in any format, may be viewed or copied without restriction."* |

**Attribution:** not legally required. tanach.us asks for this citation, which we're glad to give:

> Unicode/XML Leningrad Codex: UXLC 2.6 (27.7), Tanach.us Inc., West Redding, CT, USA, Oct 2026.

tanach.us asks that the text not be called the "Westminster Leningrad Codex (WLC)". It isn't.

## Not included
- **Commentaries** (Rashi and others): they were removed from this repository. Their digital editions were downloaded through Sefaria, whose terms of use require written permission for commercial use. They may come back once that permission is received.
- Nothing licensed CC-BY-SA, NC or "unknown", no app code, no keys or secrets.
