# sinhalanorm

**Normalize Sinhala text, and convert legacy-font Sinhala (FM-Abhaya, Damindu) to Unicode.**

[![PyPI version](https://img.shields.io/pypi/v/sinhalanorm.svg)](https://pypi.org/project/sinhalanorm/)
[![Python versions](https://img.shields.io/pypi/pyversions/sinhalanorm.svg)](https://pypi.org/project/sinhalanorm/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Two Sinhala strings can look identical on screen and still be different bytes.
Text typed with different keyboards, copied from PDFs, or scraped from the web
mixes zero-width joiners in the wrong place, vowel signs typed in the order
they are *drawn* instead of the order Unicode *stores* them, and lookalike
pairs such as `අ + ා` standing in for `ආ`. Search misses matches,
deduplication fails, and tokenizers split the same word several different
ways.

Older documents are worse: they were typed in legacy fonts like **FM-Abhaya** or **Damindu**,
so copying them gives you `Y%S ,xld` instead of `ශ්‍රී ලංකා`.

`sinhalanorm` fixes both, with zero dependencies.

## Installation

```bash
pip install sinhalanorm
```

## Quick start

```python
import sinhalanorm

# Kombuva typed before the consonant (visual order) → stored order
sinhalanorm.normalize("ෙකාළඹ")        # 'කොළඹ'

# Lookalike pair → the real independent vowel
sinhalanorm.normalize("අාලය")          # 'ආලය'

# Legacy FM-Abhaya text → Unicode
sinhalanorm.legacy_to_unicode("Y%S ,xld")   # 'ශ්‍රී ලංකා'
sinhalanorm.legacy_to_unicode("úoHdj")      # 'විද්‍යාව'
sinhalanorm.legacy_to_unicode("rdcH ks,OdÍkag")  # 'රාජ්‍ය නිලධාරීන්ට'
sinhalanorm.legacy_to_unicode("mÑmd,k", font="damindu")  # 'පරිපාලන'

sinhalanorm.is_normalized("කොළඹ")      # True
```

### Find problems without changing anything

```python
for issue in sinhalanorm.check("ෙකාළඹ අාලය"):
    print(issue.start, issue.code, repr(issue.text), issue.fixable)
# 0 kombuva_order 'ෙක' True
# 6 vowel_composition 'අා' True
```

`check()` reports positions in *your* string, so you can highlight them in an
editor or a data-quality report. Some problems (such as a vowel sign with no
consonant before it) are reported as `fixable=False`, because the right fix is
ambiguous.

### Command line

```bash
sinhalanorm normalize corpus.txt > clean.txt
sinhalanorm legacy old_document.txt > unicode.txt
sinhalanorm legacy --font damindu circular.txt > unicode.txt
sinhalanorm check article.txt      # exits 1 if any problems are found
```

All three commands read from stdin when no file is given.

## What `normalize()` fixes

Rules run in this order. Disable any of them with
`normalize(text, skip=["rule_code"])`.

| Code | Fixes | Example |
|---|---|---|
| `invisible` | BOMs and soft hyphens; zero-width spaces / non-joiners touching Sinhala | `සිං​හල` → `සිංහල` |
| `zwj_order` | ZWJ placed before al-lakuna in yansaya, rakaransaya, repaya | `ක‍්ය` → `ක්‍ය` |
| `zwj_repeat` | Repeated ZWJs | `ක්‍‍ය` → `ක්‍ය` |
| `zwj_stray` | ZWJs next to Sinhala that don't join al-lakuna to a consonant | `ක‍ම` → `කම` |
| `double_kombuva` | Two kombuvas instead of kombu deka | `ෙෙ` → `ෛ` |
| `subjoined_order` | Vowel sign typed before a yansaya / rakaransaya | `ති්‍ර` → `ත්‍රි` |
| `kombuva_order` | Kombuva typed before its consonant | `ෙකාළඹ` → `කොළඹ` |
| `sign_order` | Anusvara / visarga typed before a vowel sign | `කංා` → `කාං` |
| `repeated_sign` | A vowel sign or al-lakuna typed twice | `කාා` → `කා` |
| *(NFC)* | Two-part vowels stored as separate code points | `ක ෙ ා` → `කො` |
| `vowel_composition` | Lookalike pairs instead of independent vowels | `අා` → `ආ`, `එ්` → `ඒ`, `ඔ්` → `ඕ` |

The output is always NFC. Non-Sinhala text passes through unchanged,
including ZWJs in emoji sequences.

## Legacy fonts

`legacy_to_unicode()` supports two legacy encodings:

| `font=` | Fonts | Typical sources |
|---|---|---|
| `"fm-abhaya"` (default) | FMAbhaya, FMAbhaya x, FMAbabld (bold) | Gazettes, NIE and school textbooks, 2000s-2010s |
| `"damindu"` (experimental) | Damindu (Wijayananda Jayaweera) | Government circulars, 1990s to early 2000s |

Both fonts use the Wijesekara typewriter layout for ASCII, so `l` is ක in
either. Their precomposed glyphs are different, though. The same bytes
`mÑmd,k` read පරිපාලන in Damindu but පචිපාලන in FM-Abhaya, so **pick the
font the document was set in**. In a PDF, the font name is on each text span
(PyMuPDF: `page.get_text("dict")`). Embedded fonts often have generated names
like `MSTT31c40b`; if words with accented letters come out wrong under one
encoding, try the other.

The converter maps each glyph to Unicode, moves each kombuva from its visual
position to its stored position, and then runs `normalize()`. It reproduces
what the font draws, including the author's typos. Damindu glyphs with too
little evidence to identify are left unchanged rather than guessed, so they
stay visible.

**Accuracy on real documents** (share of converted words found in Sinhala
Wikipedia; see the [evaluation](study/README.md)):

| Encoding | Words tested | In vocabulary | Malformed output |
|---|---:|---:|---:|
| FM-Abhaya | 150,580 (6 PDFs) | **98.2%** | 0.02% |
| Damindu | 1,774 (5 circulars) | **95.5%** | 0% |

A manual review found nearly all of the remaining words to be correct words
that Wikipedia lacks, or typos in the source. For comparison, an existing
FM-Abhaya converter produces malformed Unicode in 5% of tokens. The Damindu
figure comes from far less text, all of which was also used to build the
table, so Damindu support is **experimental**. If you have Damindu documents,
please share them in an issue.

Pass it only the text that was set in the legacy font. Every Latin letter is
treated as a Sinhala glyph, so English words get converted too. If a word
converts wrongly, please
[open an issue](https://github.com/RavinduPabasara/sinhalanorm/issues) with
the input, the font and the expected output.

## API reference

| Function / object | Description |
|---|---|
| `normalize(text, *, skip=()) -> str` | Return normalized NFC text |
| `is_normalized(text) -> bool` | `normalize(text) == text` |
| `check(text) -> list[Issue]` | Report problems with positions; does not modify |
| `legacy_to_unicode(text, font="fm-abhaya") -> str` | Convert legacy-font text (`"fm-abhaya"` or `"damindu"`) |
| `Issue` | Frozen dataclass: `code`, `start`, `end`, `text`, `message`, `fixable` |
| `ALL_RULES`, `RULE_CODES` | The rule table and the valid `skip` codes |
| `FONTS` | Supported legacy font encodings |

The package ships type hints (`py.typed`).

## Development

```bash
git clone https://github.com/RavinduPabasara/sinhalanorm
cd sinhalanorm
make install-dev
make test
```

## License

MIT. See [LICENSE](LICENSE).

## Author

**Ravindu Pabasara Karunarathna**, also the author of
[sinhaladate](https://pypi.org/project/sinhaladate/),
[slnic](https://pypi.org/project/slnic/) and
[tokscope](https://pypi.org/project/tokscope/).
