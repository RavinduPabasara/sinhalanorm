"""Evaluate legacy_to_unicode() on real FM-Abhaya and Damindu documents.

Downloads public Sri Lankan PDFs, extracts only the text set in the legacy
font, converts it, and reports the share of output words found in a Sinhala
Wikipedia vocabulary, plus the share of outputs that check() flags as
malformed.

Requirements (study only, not the library): pip install pymupdf

Usage:
    python study/legacy_eval.py --wiki-dump siwiki-latest-pages-articles.xml.bz2

Get the dump from
https://dumps.wikimedia.org/siwiki/latest/siwiki-latest-pages-articles.xml.bz2
(~85 MB). The PDFs are cached in study/.cache/ (git-ignored).
"""

import argparse
import bz2
import collections
import re
import urllib.request
from pathlib import Path
from typing import Counter, List, NamedTuple, Set

import pymupdf

import sinhalanorm


class Document(NamedTuple):
    name: str
    url: str
    font: str  # regex matched against PDF font names
    encoding: str  # sinhalanorm legacy font


_PUBAD = "https://www.pubad.gov.lk/web/images/circulars"

DOCUMENTS: List[Document] = [
    # FM-Abhaya
    Document(
        "moj_gazette_2187-27",
        "https://www.moj.gov.lk/images/Circulars/2187-27_S.pdf",
        r"^FM",
        "fm-abhaya",
    ),
    Document(
        "nie_kannangara",
        "https://nie.lk/pdffiles/cww/Kannangara%20Deshanaya%20-32%20si.pdf",
        r"^FM",
        "fm-abhaya",
    ),
    Document(
        "nie_art_part2",
        "https://nie.lk/pdffiles/art/PART_2FULL.pdf",
        r"^FM",
        "fm-abhaya",
    ),
    Document(
        "moe_cww",
        "https://e-thaksalawa.moe.gov.lk/lcms/pluginfile.php/25891/"
        "mod_resource/content/2/C.W.W.pdf",
        r"^FM",
        "fm-abhaya",
    ),
    Document(
        "edupub_maths_g9",
        "http://www.edupub.gov.lk/Administrator/Sinhala/9/"
        "mats%20g9%20p-I%20S/maths%20g9%20p-I%20S.pdf",
        r"^FM",
        "fm-abhaya",
    ),
    Document(
        "vacancy_notice",
        "https://s3-ap-southeast-1.amazonaws.com/mytutor.lk/vacancy/"
        "%5B8812977705bf68b53488b4%5D-15_si.pdf",
        r"^FM",
        "fm-abhaya",
    ),
    # Damindu. The embedded fonts have generated names (MSTT31c...); these were
    # identified as Damindu by the copyright glyph and glyph widths.
    Document(
        "pubad_07-2000",
        f"{_PUBAD}/2000/S/07-2000(s).pdf",
        r"^MSTT31c40b$",
        "damindu",
    ),
    Document(
        "pubad_12-2000",
        f"{_PUBAD}/2000/S/12-2000(s).pdf",
        r"^(MSTT31c41a|Damindu\*A)$",
        "damindu",
    ),
    Document(
        "pubad_18-2000",
        f"{_PUBAD}/2000/S/18-2000(s).pdf",
        r"MSTT31c4b8$",
        "damindu",
    ),
    Document(
        "pubad_04-2001",
        f"{_PUBAD}/2001/S/04-2001(s).pdf",
        r"^Damindu\*A$",
        "damindu",
    ),
    Document(
        "pubad_20-2001",
        f"{_PUBAD}/2001/S/20-2001(s).pdf",
        r"^MSTT31c729$",
        "damindu",
    ),
]

WORD = re.compile("[\u0d80-\u0dff\u200d]+")
ZWJ = "\u200d"
CACHE = Path(__file__).parent / ".cache"


def fetch(doc: Document) -> Path:
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"{doc.name}.pdf"
    if not path.exists():
        req = urllib.request.Request(doc.url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=180) as r:
            path.write_bytes(r.read())
    return path


def legacy_tokens(path: Path, font: str) -> List[str]:
    """Whitespace tokens from spans whose font name matches ``font``."""
    rx = re.compile(font)
    tokens: List[str] = []
    for page in pymupdf.open(path).pages():
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                text = "".join(s["text"] for s in line["spans"] if rx.search(s["font"]))
                tokens.extend(text.split())
    return tokens


def load_vocab(dump: Path) -> Set[str]:
    counts: Counter[str] = collections.Counter()
    with bz2.open(dump, "rt", encoding="utf-8") as f:
        for line in f:
            counts.update(WORD.findall(line))
    # ZWJ use varies between writers; compare without it.
    return {w.replace(ZWJ, "") for w, n in counts.items() if n >= 2}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--wiki-dump", type=Path, required=True)
    parser.add_argument("--unknown-out", type=Path, help="write unknown words here")
    args = parser.parse_args()

    vocab = load_vocab(args.wiki_dump)
    unknown: Counter[str] = collections.Counter()

    for encoding in ("fm-abhaya", "damindu"):
        total_words = total_known = total_tokens = flagged = 0
        print(f"\n{encoding}\n{'document':24} {'words':>8} {'in vocab':>9}")
        for doc in DOCUMENTS:
            if doc.encoding != encoding:
                continue
            words = known = 0
            for raw in legacy_tokens(fetch(doc), doc.font):
                out = sinhalanorm.legacy_to_unicode(raw, font=encoding)
                total_tokens += 1
                flagged += bool(sinhalanorm.check(out))
                for w in WORD.findall(out):
                    words += 1
                    if w.replace(ZWJ, "") in vocab:
                        known += 1
                    else:
                        unknown[w] += 1
            total_words += words
            total_known += known
            print(f"{doc.name:24} {words:8d} {known / words:9.2%}")
        print(f"{'TOTAL':24} {total_words:8d} {total_known / total_words:9.2%}")
        print(f"tokens flagged by check(): {flagged} / {total_tokens}")

    if args.unknown_out:
        with open(args.unknown_out, "w", encoding="utf-8") as f:
            for w, n in unknown.most_common():
                f.write(f"{n}\t{w}\n")


if __name__ == "__main__":
    main()
