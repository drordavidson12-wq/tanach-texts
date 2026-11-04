#!/usr/bin/env python3
"""
Builds tanakh/ and tanakh-teamim/ directly from the Unicode/XML Leningrad Codex (UXLC),
as published by tanach.us (not through Sefaria).

    python3 scripts/uxlc.py                      # downloads the current Tanach.xml.zip (upgrade)
    python3 scripts/uxlc.py <folder with Books/>  # or: from an already unzipped copy

The Hebrew characters are copied exactly as they are in the XML (no Unicode normalization).
- tanakh-teamim/: the words as they are, with niqqud and te'amim.
- tanakh/: the same words with the te'amim (cantillation marks U+0591-U+05AF) removed.
  Nothing else is removed: niqqud, meteg, maqaf, sof pasuq and paseq stay.
Markup handled: <w> word, <k>/<q> ketiv/qere ("ketiv [qere]"), <s> large/small letter
(the letter is kept), <x> editorial note marker (removed), <pe/>/<samekh/> open/closed
parasha (written as "(פ)"/"(ס)" in tanakh-teamim/ only).
"""

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BOOKS = [  # (UXLC file, our id, Hebrew name)
    ("Genesis", "genesis", "בראשית"), ("Exodus", "exodus", "שמות"), ("Leviticus", "leviticus", "ויקרא"),
    ("Numbers", "numbers", "במדבר"), ("Deuteronomy", "deuteronomy", "דברים"), ("Joshua", "joshua", "יהושע"),
    ("Judges", "judges", "שופטים"), ("Samuel_1", "i_samuel", "שמואל א"), ("Samuel_2", "ii_samuel", "שמואל ב"),
    ("Kings_1", "i_kings", "מלכים א"), ("Kings_2", "ii_kings", "מלכים ב"), ("Isaiah", "isaiah", "ישעיהו"),
    ("Jeremiah", "jeremiah", "ירמיהו"), ("Ezekiel", "ezekiel", "יחזקאל"), ("Hosea", "hosea", "הושע"),
    ("Joel", "joel", "יואל"), ("Amos", "amos", "עמוס"), ("Obadiah", "obadiah", "עובדיה"), ("Jonah", "jonah", "יונה"),
    ("Micah", "micah", "מיכה"), ("Nahum", "nahum", "נחום"), ("Habakkuk", "habakkuk", "חבקוק"),
    ("Zephaniah", "zephaniah", "צפניה"), ("Haggai", "haggai", "חגי"), ("Zechariah", "zechariah", "זכריה"),
    ("Malachi", "malachi", "מלאכי"), ("Psalms", "psalms", "תהילים"), ("Proverbs", "proverbs", "משלי"),
    ("Job", "job", "איוב"), ("Song_of_Songs", "song_of_songs", "שיר השירים"), ("Ruth", "ruth", "רות"),
    ("Lamentations", "lamentations", "איכה"), ("Ecclesiastes", "ecclesiastes", "קהלת"), ("Esther", "esther", "אסתר"),
    ("Daniel", "daniel", "דניאל"), ("Ezra", "ezra", "עזרא"), ("Nehemiah", "nehemiah", "נחמיה"),
    ("Chronicles_1", "i_chronicles", "דברי הימים א"), ("Chronicles_2", "ii_chronicles", "דברי הימים ב"),
]

TEAMIM = re.compile("[֑-֯]")
MAQAF = "־"

# UXLC numbers verses as in the Leningrad manuscript. In three places this differs from the
# common Jewish numbering (used by Sefaria and most printed Tanakhs). There we only join the
# verse division; no character of the text changes.
#   (book, chapter, first UXLC verse, last UXLC verse) -> joined into one verse
MERGE_IN_CHAPTER = [
    ("exodus", 20, 13, 16),        # לא תרצח / לא תנאף / לא תגנב / לא תענה = שמות כ יג
    ("deuteronomy", 5, 17, 20),    # same in דברים ה יז
]
#   UXLC verse that opens the next chapter in the common numbering
MOVE_TO_NEXT_CHAPTER = [("numbers", 25, 19)]  # "ויהי אחרי המגפה" = במדבר כו א


def common_numbering(fid, chapters):
    for book, c, first, last in MERGE_IN_CHAPTER:
        if book == fid:
            ch = chapters[c - 1]
            ch[first - 1:last] = [" ".join(ch[first - 1:last])]
    for book, c, v in MOVE_TO_NEXT_CHAPTER:
        if book == fid:
            assert len(chapters[c - 1]) == v, (fid, c, len(chapters[c - 1]))
            moved = chapters[c - 1].pop()
            chapters[c][0] = moved + " " + chapters[c][0]
    return chapters


def text_of(el):
    """The Hebrew text of a <w>/<k>/<q>, keeping <s> letters and dropping <x> notes."""
    out = [el.text or ""]
    for child in el:
        if child.tag != "x":
            out.append(text_of(child))
        out.append(child.tail or "")
    return "".join(out).strip()


def verse_text(v):
    parts, brk = [], None
    i, kids = 0, list(v)
    while i < len(kids):
        el = kids[i]
        if el.tag == "w":
            parts.append(text_of(el))
        elif el.tag == "k":
            ketiv = text_of(el)
            if i + 1 < len(kids) and kids[i + 1].tag == "q":
                sep = "" if ketiv.endswith(MAQAF) else " "
                parts.append(f"{ketiv}{sep}[{text_of(kids[i + 1])}]")
                i += 1
            else:
                parts.append(ketiv)
        elif el.tag == "q":  # qere without ketiv
            parts.append(f"[{text_of(el)}]")
        elif el.tag in ("pe", "samekh"):
            brk = "פ" if el.tag == "pe" else "ס"
            parts.append(f"({brk})")
        i += 1
    s = ""
    for p in parts:
        s += p if (not s or s.endswith(MAQAF)) else " " + p
    return s


ZIP_URL = "https://tanach.us/Books/Tanach.xml.zip"


def download():
    """Downloads the current Tanach.xml.zip and records its version, build and SHA-256 in source.json.
    Returns a function that reads one book's XML from the zip."""
    import hashlib, io, urllib.request, zipfile
    req = urllib.request.Request(ZIP_URL, headers={"User-Agent": "tanach-texts/1.0 (+https://github.com/drordavidson12-wq/tanach-texts)"})
    raw = urllib.request.urlopen(req, timeout=120).read()
    zf = zipfile.ZipFile(io.BytesIO(raw))
    header = zf.read("Books/TanachHeader.xml").decode("utf-8")
    version = re.search(r"<version>([^<]+)</version>", header).group(1).strip()
    build = re.search(r"<build>([^<]+)</build>", header).group(1).strip()
    src = json.load(open(ROOT / "source.json", encoding="utf-8"))
    sha = hashlib.sha256(raw).hexdigest()
    if (src.get("build"), src.get("sha256")) != (build, sha):
        # a new version: check build_date against https://tanach.us/Pages/Technical.html and fill it in by hand
        src.update({
            "version": version, "build": build, "build_date": None, "sha256": sha,
            "citation": f"Unicode/XML Leningrad Codex: {version} ({build}), Tanach.us Inc., West Redding, CT, USA.",
        })
    with open(ROOT / "source.json", "w", encoding="utf-8") as f:
        json.dump(src, f, ensure_ascii=False, indent=1)
    print(f"downloaded {version}, build {build}, sha256 {src['sha256']}")
    return lambda name: ET.fromstring(zf.read(f"Books/{name}.xml"))


def main():
    # no argument: download the current version from tanach.us (this is how to upgrade)
    # with an argument: a folder with the unzipped Books/*.xml
    if len(sys.argv) > 1:
        books_dir = Path(sys.argv[1])
        read = lambda name: ET.parse(books_dir / f"{name}.xml").getroot()
    else:
        read = download()
    for xml_name, fid, he in BOOKS:
        root = read(xml_name)
        chapters = []
        for c in root.iter("c"):
            chapters.append([verse_text(v) for v in c.findall("v")])
        teamim = common_numbering(fid, chapters)
        nikud = [[TEAMIM.sub("", re.sub(r"\s*\((פ|ס)\)", "", v)) for v in ch] for ch in chapters]
        for folder, data in (("tanakh-teamim", teamim), ("tanakh", nikud)):
            path = ROOT / folder / f"{fid}.json"
            path.parent.mkdir(exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"book": he, "chapters": data}, f, ensure_ascii=False, indent=1)
        print(fid, len(chapters), sum(len(c) for c in chapters))


if __name__ == "__main__":
    main()
