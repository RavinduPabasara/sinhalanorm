"""Rule-based normalization of Unicode Sinhala text.

Pipeline: decompose → apply rules in order → NFC → compose independent vowels.
Each rule is a named regex rewrite, so the same table drives both
:func:`normalize` (fix) and :func:`sinhalanorm.check` (report).
"""

import re
import unicodedata
from dataclasses import dataclass
from typing import Callable, Iterable, List, Pattern, Tuple, Union

from ._chars import (
    AL_LAKUNA,
    ANUSVARA,
    BOM,
    CLUSTER,
    CONSONANTS,
    DEPENDENT_VOWELS,
    KOMBU_DEKA,
    KOMBUVA,
    RAYANNA,
    SINHALA,
    SOFT_HYPHEN,
    VISARGA,
    VOWEL_COMPOSITIONS,
    YAYANNA,
    ZWJ,
    ZWNJ,
    ZWSP,
)

Replacement = Union[str, Callable[["re.Match[str]"], str]]


@dataclass(frozen=True)
class Rule:
    """One normalization step.

    Attributes:
        code: Stable identifier, usable in ``normalize(skip=...)``.
        description: Human-readable explanation of what the rule fixes.
        pattern: Compiled regex matched against decomposed text.
        replacement: ``re.sub`` replacement (string or function).
    """

    code: str
    description: str
    pattern: Pattern[str]
    replacement: Replacement

    def apply(self, text: str) -> str:
        return self.pattern.sub(self.replacement, text)


def valid_zwj_at(text: str, i: int) -> bool:
    """True if the ZWJ at ``text[i]`` joins al-lakuna to a consonant."""
    prev = text[i - 1] if i > 0 else ""
    nxt = text[i + 1] if i + 1 < len(text) else ""
    return prev == AL_LAKUNA and re.match(f"[{CONSONANTS}]", nxt) is not None


def _fix_stray_zwj(match: "re.Match[str]") -> str:
    # Only ZWJs next to Sinhala reach here, so emoji sequences are untouched.
    return ZWJ if valid_zwj_at(match.string, match.start()) else ""


RULES: Tuple[Rule, ...] = (
    Rule(
        "invisible",
        "Remove BOMs and soft hyphens, and zero-width spaces / non-joiners "
        "touching Sinhala text",
        re.compile(
            f"[{BOM}{SOFT_HYPHEN}]"
            f"|(?<=[{SINHALA}])[{ZWSP}{ZWNJ}]+"
            f"|[{ZWSP}{ZWNJ}]+(?=[{SINHALA}])"
        ),
        "",
    ),
    Rule(
        "zwj_order",
        "Put ZWJ after al-lakuna in yansaya, rakaransaya and repaya "
        "(ක\u200d්ය → ක්\u200dය)",
        re.compile(
            f"(?<=[{CONSONANTS}]){ZWJ}{AL_LAKUNA}(?=[{YAYANNA}{RAYANNA}])"
            f"|(?<={RAYANNA}){ZWJ}{AL_LAKUNA}(?=[{CONSONANTS}])"
        ),
        AL_LAKUNA + ZWJ,
    ),
    Rule(
        "zwj_repeat",
        "Collapse repeated ZWJs into one",
        re.compile(f"{ZWJ}{{2,}}"),
        ZWJ,
    ),
    Rule(
        "zwj_stray",
        "Remove ZWJs next to Sinhala that do not join al-lakuna to a consonant",
        re.compile(f"(?<=[{SINHALA}]){ZWJ}|{ZWJ}(?=[{SINHALA}])"),
        _fix_stray_zwj,
    ),
    Rule(
        "subjoined_order",
        "Put vowel signs after a yansaya / rakaransaya typed after them "
        "(ති්\u200dර → ත්\u200dරි)",
        re.compile(
            f"([{DEPENDENT_VOWELS}]+){AL_LAKUNA}?({AL_LAKUNA}{ZWJ}[{YAYANNA}{RAYANNA}])"
        ),
        r"\2\1",
    ),
    Rule(
        "double_kombuva",
        "Join two kombuvas into kombu deka (ෙ + ෙ → ෛ)",
        re.compile(KOMBUVA * 2),
        KOMBU_DEKA,
    ),
    Rule(
        "kombuva_order",
        "Move a kombuva typed in visual order (before its consonant) to "
        "after it (ෙක → කෙ)",
        re.compile(f"(?<![{CONSONANTS}])([{KOMBUVA}{KOMBU_DEKA}])({CLUSTER})"),
        r"\2\1",
    ),
    Rule(
        "sign_order",
        "Put vowel signs before anusvara / visarga (කංා → කාං)",
        re.compile(f"([{ANUSVARA}{VISARGA}])([{DEPENDENT_VOWELS}]+)"),
        r"\2\1",
    ),
    Rule(
        "repeated_sign",
        "Collapse a vowel sign, al-lakuna, anusvara or visarga typed twice",
        re.compile(f"([{DEPENDENT_VOWELS}{AL_LAKUNA}{ANUSVARA}{VISARGA}])\\1+"),
        r"\1",
    ),
)

_VOWEL_RULE = Rule(
    "vowel_composition",
    "Use the single independent vowel instead of a lookalike pair (අා → ආ)",
    re.compile("|".join(VOWEL_COMPOSITIONS)),
    lambda m: VOWEL_COMPOSITIONS[m.group(0)],
)

ALL_RULES: Tuple[Rule, ...] = RULES + (_VOWEL_RULE,)
RULE_CODES = frozenset(r.code for r in ALL_RULES)


def decompose(text: str) -> Tuple[str, List[int]]:
    """NFD-decompose ``text`` char by char.

    Returns the decomposed string and, for every position in it, the index of
    the original character it came from (used to report issues against the
    caller's text).
    """
    parts: List[str] = []
    origin: List[int] = []
    for i, ch in enumerate(text):
        d = unicodedata.normalize("NFD", ch)
        parts.append(d)
        origin.extend([i] * len(d))
    return "".join(parts), origin


def normalize(text: str, *, skip: Iterable[str] = ()) -> str:
    """Return a canonical, cleaned-up form of Unicode Sinhala text.

    Fixes invisible-character noise, misplaced ZWJs, vowel signs typed in
    visual order, lookalike vowel pairs, and non-NFC sequences. Non-Sinhala
    text passes through unchanged (apart from BOMs and soft hyphens).

    Args:
        text: Input string.
        skip: Rule codes to disable (see :data:`RULE_CODES`).

    Returns:
        The normalized string, always in NFC.

    Raises:
        ValueError: If ``skip`` contains an unknown rule code.
    """
    skipped = set(skip)
    unknown = skipped - RULE_CODES
    if unknown:
        raise ValueError(f"unknown rule code(s): {', '.join(sorted(unknown))}")

    out, _ = decompose(text)
    for rule in RULES:
        if rule.code not in skipped:
            out = rule.apply(out)
    out = unicodedata.normalize("NFC", out)
    if _VOWEL_RULE.code not in skipped:
        out = _VOWEL_RULE.apply(out)
    return out


def is_normalized(text: str) -> bool:
    """True if :func:`normalize` would leave ``text`` unchanged."""
    return normalize(text) == text


def fix_subjoined(text: str) -> str:
    """Apply the ``repeated_sign`` and ``subjoined_order`` rules only.

    Legacy-font text needs these *before* kombuvas are moved, because a
    doubled al-lakuna or a misplaced vowel sign breaks up the cluster the
    kombuva has to move past.
    """
    for rule in RULES:
        if rule.code in ("repeated_sign", "subjoined_order"):
            text = rule.apply(unicodedata.normalize("NFD", text))
    return text


def _move_all_prebase(text: str) -> str:
    """Move every kombuva / kombu deka after the cluster that follows it.

    Used for legacy-font text, where the pre-base sign is *always* stored in
    visual order, even right after another consonant (e.g. ``lfl`` = කකෙ).
    """
    return re.sub(f"([{KOMBUVA}{KOMBU_DEKA}])({CLUSTER})", r"\2\1", text)
