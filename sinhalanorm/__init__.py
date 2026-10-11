"""sinhalanorm — normalize Sinhala text and convert legacy-font Sinhala to Unicode.

Basic usage:

    >>> import sinhalanorm
    >>> sinhalanorm.normalize("අාලය")  # අ + ා typed as two characters
    'ආලය'
    >>> sinhalanorm.legacy_to_unicode("isxy,")
    'සිංහල'
"""

from .check import Issue, check
from .legacy import FONTS, legacy_to_unicode
from .normalize import ALL_RULES, RULE_CODES, Rule, is_normalized, normalize

__version__ = "0.1.0"

__all__ = [
    "normalize",
    "is_normalized",
    "check",
    "legacy_to_unicode",
    "Issue",
    "Rule",
    "ALL_RULES",
    "RULE_CODES",
    "FONTS",
    "__version__",
]
