"""Report normalization problems without changing the text."""

import re
from dataclasses import dataclass
from typing import List

from ._chars import (
    AL_LAKUNA,
    ANUSVARA,
    CONSONANTS,
    DEPENDENT_VOWELS,
    KOMBU_DEKA,
    KOMBUVA,
    SINHALA,
    VISARGA,
    ZWJ,
)
from .normalize import ALL_RULES, decompose, valid_zwj_at

# Decomposable two-part vowels that are stored as separate code points in the
# caller's text (NFC would merge them). Matched on the ORIGINAL text.
_NOT_NFC = re.compile("\u0dd9[\u0dca\u0dcf\u0ddf]|\u0ddc\u0dca")

# A vowel sign / al-lakuna / anusvara with nothing to attach to: at the start
# of the text or after a non-Sinhala character. A kombuva followed by a
# consonant is excluded: that is "kombuva_order", which normalize() fixes.
# Matched on decomposed text.
_ORPHAN = re.compile(
    f"(?:^|(?<=[^{SINHALA}{ZWJ}]))"
    f"(?![{KOMBUVA}{KOMBU_DEKA}][{CONSONANTS}])"
    f"[{DEPENDENT_VOWELS}{AL_LAKUNA}{ANUSVARA}{VISARGA}]"
)


@dataclass(frozen=True)
class Issue:
    """A problem found by :func:`check`.

    Attributes:
        code: Rule code (see ``sinhalanorm.RULE_CODES``), ``"not_nfc"``, or
            ``"orphan_sign"`` (reported only; not auto-fixable).
        start: Start index in the checked text.
        end: End index (exclusive) in the checked text.
        text: The offending substring, ``text[start:end]``.
        message: Human-readable description.
        fixable: Whether :func:`sinhalanorm.normalize` fixes it.
    """

    code: str
    start: int
    end: int
    text: str
    message: str
    fixable: bool = True


def check(text: str) -> List[Issue]:
    """List the normalization problems in ``text``, sorted by position.

    Rules are matched against the input in pipeline order; a span already
    reported by an earlier rule is not reported again. Use
    :func:`sinhalanorm.normalize` to fix everything marked ``fixable``.
    """
    decomposed, origin = decompose(text)
    issues: List[Issue] = []

    def add(code: str, start: int, end: int, message: str, fixable: bool) -> None:
        # Map decomposed span back to original indices.
        s = origin[start] if start < len(origin) else len(text)
        e = origin[end - 1] + 1 if end > start else s
        # Rules run in pipeline order; a match inside a span an earlier rule
        # already reported is the same problem seen again.
        if any(i.start <= s and e <= i.end for i in issues):
            return
        issues.append(Issue(code, s, e, text[s:e], message, fixable))

    for rule in ALL_RULES:
        for m in rule.pattern.finditer(decomposed):
            if rule.code == "zwj_stray" and valid_zwj_at(decomposed, m.start()):
                continue
            add(rule.code, m.start(), m.end(), rule.description, True)

    for m in _NOT_NFC.finditer(text):
        issues.append(
            Issue(
                "not_nfc",
                m.start(),
                m.end(),
                m.group(0),
                "Two-part vowel stored as separate code points; NFC merges them",
            )
        )

    for m in _ORPHAN.finditer(decomposed):
        add(
            "orphan_sign",
            m.start(),
            m.end(),
            "Vowel sign or al-lakuna with no consonant to attach to",
            False,
        )

    issues.sort(key=lambda i: (i.start, i.end, i.code))
    return issues
