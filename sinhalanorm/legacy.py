"""Convert text typed in legacy (non-Unicode) Sinhala fonts to Unicode.

Before Unicode Sinhala was widely supported, Sinhala was typed as Latin
characters and *displayed* with a font whose glyphs are Sinhala letters. Copy
the text out of a PDF or old web page and you get strings like ``Y%S ,xld``
instead of ශ්\u200dරී ලංකා.

Conversion is: map each glyph (longest match first) to its Unicode fragment,
move every kombuva from its visual position to after its consonant, then run
:func:`sinhalanorm.normalize`, which composes the two-part vowels.
"""

from typing import Dict

from ._chars import AL_LAKUNA, ZWJ
from .normalize import _move_all_prebase, fix_subjoined, normalize

_J = AL_LAKUNA + ZWJ  # joins the next consonant: ක + _J + ෂ = ක්\u200dෂ
_YANSAYA = _J + "ය"
_RAKARANSAYA = _J + "ර"

# Wijesekara typewriter layout: the ASCII keys shared by FM-Abhaya, Damindu
# and other legacy fonts of the same era.
_WIJESEKARA: Dict[str, str] = {
    # Multi-character glyph sequences (matched before single characters)
    "ff": "ෛ",
    "ft": "ඓ",
    "re": "රු",  # ර takes a special u-sign shape
    "rE": "රූ",
    "CO": "ඣ",
    "a?": _RAKARANSAYA + "ෑ",  # al-lakuna + the රෑ glyph (*a?kala = Frank)
    "A?": _RAKARANSAYA + "ෑ",
    # Consonants
    "l": "ක",
    "L": "ඛ",
    ".": "ග",
    ">": "ඝ",
    "X": "ඞ",
    "p": "ච",
    "P": "ඡ",
    "c": "ජ",
    "[": "ඤ",
    "{": "ඥ",
    "g": "ට",
    "G": "ඨ",
    "v": "ඩ",
    "V": "ඪ",
    "K": "ණ",
    ";": "ත",
    ":": "ථ",
    "o": "ද",
    "O": "ධ",
    "k": "න",
    "m": "ප",
    "M": "ඵ",
    "n": "බ",
    "N": "භ",
    "u": "ම",
    "h": "ය",
    "r": "ර",
    ",": "ල",
    "j": "ව",
    "Y": "ශ",
    "I": "ෂ",
    "i": "ස",
    "y": "හ",
    "<": "ළ",
    "*": "ෆ",
    "U": "ඹ",
    "|": "ඳ",
    "~": "ඬ",
    # Independent vowels (අා, එ් etc. are composed later by normalize())
    "w": "අ",
    "b": "ඉ",
    "B": "ඊ",
    "W": "උ",
    "R": "ඍ",
    "t": "එ",
    "T": "ඔ",
    # Vowel signs and other signs
    "d": "ා",
    "e": "ැ",
    "E": "ෑ",
    "s": "ි",
    "S": "ී",
    "q": "ු",
    "=": "ු",
    "Q": "ූ",
    "+": "ූ",
    "D": "ෘ",
    "!": "ෟ",
    "f": "ෙ",
    "a": AL_LAKUNA,
    "A": AL_LAKUNA,
    "x": "ං",
    "#": "ඃ",
    # Joining forms
    "H": _YANSAYA,
    "%": _RAKARANSAYA,
    "C": "ක" + _J,
    "F": "ත" + _J,
    "J": "න" + _J,
    # Precomposed glyphs
    "?": "රෑ",
    "/": "රැ",
    # Punctuation (the ASCII punctuation keys are taken by letters)
    "'": ".",
    '"': ",",
    "(": ":",
    "^": "(",
    "&": ")",
    "]": "%",
    "$": "/",
    "@": "?",
    "}": "=",
}

# FM-Abhaya, checked against the glyphs of the FMAbhaya x font and against
# usage in real FM-Abhaya documents (see study/README.md).
FM_ABHAYA: Dict[str, str] = {
    **_WIJESEKARA,
    # Keys that differ from Damindu
    "\\": "ඳ",
    "Z": "’",
    "z": "‘",
    ")": "*",
    # Precomposed glyphs and punctuation
    "Õ": "ඟ",
    "×": "ඥ",
    "Ø": "ඤ",
    "®": "ඣ",
    "Ë": "ක" + _J + "ෂ",
    "Ù": "ඕ",
    "´": "ඕ",
    "Ì": "ඏ",
    "Ï": "ඐ",
    "½": "ඃ",
    "›": "ශ" + _RAKARANSAYA + "ී",
    "ø": "ද" + _RAKARANSAYA,
    "…": "ත" + _J + "ව",
    "‡": "න" + _J + "ද",
    "ˆ": "න" + _J + "දා",
    "†": "ත" + _J + "ථ",
    "“": "ර්" + ZWJ + "ණ",
    "œ": "ර්" + ZWJ + "ය",
    "Þ": "දා",
    "±": "දැ",
    "ƒ": "ඳැ",
    "È": "දි",
    "§": "දී",
    "ÿ": "දු",
    "¥": "දූ",
    "µ": "ද" + _YANSAYA,
    "÷": "ඳු",
    "¢": "ඳි",
    "£": "ඳී",
    "ª": "ඳූ",
    "û": "ඤු",
    "ü": "ඤූ",
    "¨": "ලු",
    "Æ": "ලූ",
    "¿": "ළු",
    "¯": "ඣි",
    "ˉ": "ඣි",
    "°": "ඣී",
    "À": "ඨි",
    "Á": "ඨී",
    "Å": "ඛි",
    "Ç": "ඛී",
    "Â": "ඡී",
    "ß": "රි",
    "Í": "රී",
    "Î": "ඪි",
    "Ð": "ඪී",
    "Ñ": "චි",
    "Ö": "චී",
    "Ó": "ථි",
    "Ò": "ථී",
    "ð": "ජි",
    "Ô": "ජී",
    "Ú": "ඵී",
    "Ý": "ඵි",
    "á": "ටි",
    "à": "ටී",
    "ä": "ඩි",
    "ã": "ඩී",
    "ç": "ඬි",
    "é": "ඬී",
    "ê": "ධි",
    "ë": "ධී",
    "ì": "බි",
    "î": "බී",
    "ñ": "මි",
    "ó": "මී",
    "ô": "ඹි",
    "ö": "ඹී",
    "ú": "වි",
    "ù": "වී",
    "‚": "ණි",
    "Œ": "ණී",
    "Ä": "ඛ්",
    "É": "ච්",
    "Ê": "ජ්",
    "þ": "ඡ්",
    "Ü": "ට්",
    "â": "ඩ්",
    "å": "ඬ්",
    "è": "ධ්",
    "í": "බ්",
    "ï": "ම්",
    "ò": "ඹ්",
    "õ": "ව්",
    "¾": "ර්",
    "æ": "!",
    "¦": ";",
    "¤": "–",
    "¡": ".",
    "—": "“",
    "˜": "”",
    "²": "●",
}

# Damindu (Wijayananda Jayaweera; used in Sri Lankan government documents
# in the 1990s and around 2000). Same ASCII layout as FM except the keys
# below, but entirely different precomposed glyphs. Each entry was read from
# the glyphs of an embedded Damindu font and confirmed by usage in real
# documents; glyphs without enough evidence are deliberately left unmapped.
DAMINDU: Dict[str, str] = {
    **_WIJESEKARA,
    ")": "—",  # form fields: ku() = නම:—
    "\\": '"',
    "`": "!",
    # Precomposed glyphs
    "Ñ": "රි",
    "¯": "රී",
    "à": "ම්",
    "â": "මි",
    "ë": "වි",
    "è": "වී",
    "ï": "ව්",
    "ò": "ධි",
    "†": "දි",
    "°": "දී",
    "¥": "දු",
    "±": "දැ",
    "á": "ඳු",
    "µ": "ද" + _YANSAYA,
    "Ä": "ච්",
    "æ": "බ්",
    "å": "ටි",
    "Æ": "ඩි",
    "ü": "ඹී",
    "‚": "ජි",
    "Õ": "ඟ",
    # Word's smart quotes land on these code points; the font draws them as
    # the full stop and comma that the ' and " keys produce.
    "‘": ".",
    "’": ".",
    "“": ",",
    "”": ",",
    # Symbols
    "‡": "]",
    "ˆ": "'",
    "‹": "×",
    "›": "÷",
    "¸": "÷",
    "Ž": "¾",
    "¤": "+",
    "Â": "+",
    "·": ";",
    "¿": "¼",
    "À": "½",
    "Á": "¾",
    "Ó": "¼",
    "Ô": "½",
    "È": "™",
    "Ê": "©",
    "Ë": "®",
    "Í": "£",
    "Î": "$",
    "Ï": "#",
    "Ò": "!",
    "Ý": "{",
    "Þ": "}",
}

FONTS: Dict[str, Dict[str, str]] = {"fm-abhaya": FM_ABHAYA, "damindu": DAMINDU}

# In FM-Abhaya "`" is a sannaka (nasal) mark typed BEFORE a consonant:
# `o = ඳ, `. = ඟ. (In Damindu the same key is "!".)
_SANNAKA_FONTS = {"fm-abhaya"}
_SANNAKA = {"ද": "ඳ", "ග": "ඟ", "ඩ": "ඬ", "ජ": "ඦ", "ඳ": "ඳ", "ඟ": "ඟ", "ඬ": "ඬ"}


def _decode_c1(text: str) -> str:
    # Text extracted as Latin-1 carries C1 controls (U+0080-U+009F) where the
    # font's cp1252 glyphs (ƒ, …, †, ‡, ˆ, Œ, “, ›) were meant.
    out = []
    for ch in text:
        if "\x80" <= ch <= "\x9f":
            try:
                ch = bytes([ord(ch)]).decode("cp1252")
            except UnicodeDecodeError:
                pass
        out.append(ch)
    return "".join(out)


def legacy_to_unicode(text: str, font: str = "fm-abhaya") -> str:
    """Convert legacy-font Sinhala text to normalized Unicode.

    Pass only the runs that were set in the legacy font: every Latin letter is
    treated as a Sinhala glyph, so English words would be converted too.

    Args:
        text: Text as extracted from a document set in the legacy font.
        font: Legacy font encoding: ``"fm-abhaya"`` (FMAbhaya, FMAbhaya x,
            FMAbabld) or ``"damindu"``. The fonts share the ASCII layout but
            not their precomposed glyphs, so the right choice matters.

    Returns:
        Normalized Unicode Sinhala.

    Raises:
        ValueError: If ``font`` is not supported.

    Example:
        >>> legacy_to_unicode("Y%S ,xld")
        'ශ්\\u200dරී ලංකා'
    """
    font = font.lower()
    try:
        table = FONTS[font]
    except KeyError:
        supported = ", ".join(sorted(FONTS))
        raise ValueError(f"unknown font {font!r}; supported: {supported}") from None

    text = _decode_c1(text)
    # Al-lakuna is often typed before the rakaransaya glyph; move it after so
    # it lands on the joined cluster (ක්\u200dර + ් ...).
    text = text.replace("a%", "%a").replace("A%", "%A")

    max_len = max(len(k) for k in table)
    out = []
    sannaka = False
    i = 0
    while i < len(text):
        if text[i] == "`" and font in _SANNAKA_FONTS:
            sannaka = True
            i += 1
            continue
        for n in range(max_len, 0, -1):
            chunk = text[i : i + n]
            if chunk in table:
                piece = table[chunk]
                i += n
                break
        else:
            piece = text[i]
            i += 1
        if sannaka and piece[:1] in _SANNAKA:
            piece = _SANNAKA[piece[0]] + piece[1:]
        sannaka = False
        out.append(piece)

    return normalize(_move_all_prebase(fix_subjoined("".join(out))))
