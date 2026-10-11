# How accurate is the legacy-font converter?

*An evaluation of `sinhalanorm.legacy_to_unicode()` on real documents, October 2026.*

Part 1 covers FM-Abhaya and Part 2 covers Damindu.

# Part 1: FM-Abhaya

## Data

Six public Sri Lankan PDFs typeset in FM-Abhaya, together about 680 pages:
a Ministry of Justice gazette, two National Institute of Education
publications (a biography and a 415-page art history), a Ministry of Education
article, a Grade 9 mathematics textbook, and a job vacancy notice. The URLs are
in [`legacy_eval.py`](legacy_eval.py). Only text set in FM fonts is
evaluated: FMAbhaya, FMAbhaya x, FMAbabld (bold), and small amounts of
FMSamantha and FMEmanee.

There is no Unicode "answer key" for these documents, so the evaluation uses
two proxies:

1. **Vocabulary coverage**: the share of converted words that appear in
   Sinhala Wikipedia (247k word types, each seen at least twice; ZWJ ignored).
2. **Well-formedness**: the share of converted tokens that
   `sinhalanorm.check()` flags as malformed Unicode.

## Results

| Document | Words | In Wikipedia vocabulary |
|---|---:|---:|
| Ministry of Justice gazette | 24,148 | 98.82% |
| NIE: Kannangara biography | 13,057 | 98.61% |
| NIE: art history, part 2 | 93,459 | 98.23% |
| MoE: C.W.W. Kannangara article | 1,672 | 98.62% |
| Grade 9 maths textbook | 17,163 | 97.16% |
| Vacancy notice | 1,081 | 97.50% |
| **Total** | **150,580** | **98.23%** |

The remaining 1.8% are mostly *correct* words that Wikipedia lacks. In a
manual review of 100 randomly sampled unknown word types, 99 were correct
conversions: compounds (අණපනත්වලට), names (කන්නන්ගරයන්ගේ), technical terms
(හාකෝණ), Pali (චක්ඛුමා), or typos and missing spaces in the source
document. The one real error (`ª`, now fixed) led to a mapping fix.

### Compared with an existing converter

The same tokens were run through the FM-Abaya converter in
[Open-SL/sinhala-unicode-converter](https://github.com/Open-SL/sinhala-unicode-converter)
(UCSC LTRL code):

| Converter | In vocabulary | Malformed output tokens |
|---|---:|---:|
| **sinhalanorm** | **98.23%** | **0.02%** (24 of 158,972) |
| Open-SL / UCSC | 97.78% | 4.97% (7,902) |

Most of the reference converter's malformed output is stray ZWJs
(`ශ‍්‍රී` instead of `ශ්‍රී`). These render correctly but are different bytes,
so search, deduplication and tokenization treat the word as something
else. sinhalanorm's 24 flagged tokens are all problems in the source text,
such as footnote numbers inside words or words split across lines.

## What the evaluation fixed

The first version of the glyph table came from an existing converter and was
wrong in several places. Each fix below was confirmed both by rendering the
glyph from the FMAbhaya x font file and by usage in these documents:

| Glyph | Was | Is | Evidence |
|---|---|---|---|
| `µ` | (unmapped) | ද්‍ය | `úµd,h` = විද්‍යාලය |
| `` ` `` | (unmapped) | sannaka prefix | `fjf<`om<` = වෙළෙඳපළ |
| `¨` | ලූ | ලු | `nyd¨ï` = බහාලුම් |
| `¥` | (unmapped) | දූ | `¥IKh` = දූෂණය |
| `\` | (unmapped) | ඳ | `y\qkajd` = හඳුන්වා |
| `?` | (unmapped) | රෑ | `*a?kala` = ෆ්‍රෑන්ක් |
| `ã` | ඞී | ඩී | `ã'iS'` = ඩී.සී. |

It also exposed an ordering problem: a vowel sign typed before the
rakaransaya glyph (`;s%` gave ති්‍ර, but should be ත්‍රි). That is now the
`subjoined_order` rule in `normalize()`, so it also fixes Unicode text with the
same mistake.

# Part 2: Damindu

## Finding Damindu text

Damindu (© Wijayananda Jayaweera) turned up while looking for FM-Abhaya
documents. Sinhala circulars on pubad.gov.lk from around 2000 looked like FM
text, but only about 75% of their words converted correctly with the FM
table. Rendering the font embedded in one of them showed a copyright glyph:
*"Damindu © Wijayananda Jayaweera, Regd. No. 2758"*. Damindu uses the same
Wijesekara ASCII layout as FM, but its precomposed glyphs are entirely
different.

Embedded fonts usually have generated names such as `MSTT31c40b`, so
Damindu text was identified in two ways:

1. **Glyph widths**: a font's per-glyph advance widths survive subsetting.
   Compared up to a scale factor, these singled out Damindu fonts among 203
   archived circulars from 1970 to 2012.
2. **Content**: a draft table using only the confirmed glyphs had to convert
   a font's text far better than the FM table, and the font had to almost
   never use code points that are symbols or empty in Damindu.

Together they identified six Damindu fonts with real text, in five
circulars from 2000-2001: about 1,900 tokens. (The width method also flagged
two circulars with almost no Damindu text, and the content method caught a
font embedded under the name `Damindu*A`.) That is small. Many other circulars from the same era use
further encodings (`Mi_Damidu2000` and others) that are *not* Damindu despite
the similar name. These aren't supported.

## Building the table

Each extended glyph was mapped only when two independent sources agreed:

- **The glyph**: rendered from the font embedded in the PDFs, which in the
  first document includes all 226 glyphs.
- **Usage**: what the word must be in context. For example, `f,alà` =
  ලේකම් ("secretary") gives `à` = ම්, `isåk` = සිටින gives `å` = ටි, and
  `bx‚fkare` = ඉංජිනේරු ("engineer") gives `‚` = ජි. For the last one the
  glyph alone was ambiguous between ජි and ජී.

Seven rare glyphs (10 occurrences in total) had too little evidence and are
left unmapped. A brute-force search, which tried every syllable for each glyph
and kept the one producing the most dictionary words, was useful only as a
hint. Unconstrained, it "found" mappings that delete the glyph so that the
fragments match short words. Every mapping in the table was checked by hand.

Word's smart quotes deserve a note. Typing `'` or `"` in Word produced the
code points of ‘ ’ “ ”, and Damindu draws those as the full stop and comma,
so they are mapped to punctuation.

## Results

| Circular | Words | In Wikipedia vocabulary |
|---|---:|---:|
| 07/2000 | 488 | 98.36% |
| 12/2000 | 495 | 94.55% |
| 18/2000 | 120 | 95.83% |
| 04/2001 | 240 | 96.25% |
| 20/2001 | 431 | 92.81% |
| **Total** | **1,774** | **95.49%** |

The FM table on the same text gives 75.3%. No output token is malformed
Unicode.

All 41 unknown word types were reviewed by hand:

- 34 are correct words missing from Wikipedia, such as අභ්‍යාසලාභීන් and
  හැත්තෑපහ.
- 5 faithfully reproduce typos in the source. For example, the circular
  prints සියඍම: the author typed `R`, which Damindu draws as ඍ.
- 2 contain the unmapped glyph `ö`.
- 1 is uncertain.

**Caveat:** the same documents were used to build the table and to measure
it, so 95.5% is not an independent test. More Damindu text would make it one.

# Other findings

- **Unicode extracted from PDFs is often in visual order.** Text extracted
  from Iskoola Pota PDFs (Parliament Hansards) puts the kombuva after the
  *previous* consonant (වශෙයන් for වශයෙන්) and drops ZWJs. Fixing this
  safely is a separate problem.

## Reproduce

```bash
pip install pymupdf
curl -LO https://dumps.wikimedia.org/siwiki/latest/siwiki-latest-pages-articles.xml.bz2
python study/legacy_eval.py --wiki-dump siwiki-latest-pages-articles.xml.bz2
```
