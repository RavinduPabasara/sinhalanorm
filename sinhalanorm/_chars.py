"""Sinhala code points and regex character classes used across the package."""

# Joiners and invisible characters
ZWJ = "\u200d"
ZWNJ = "\u200c"
ZWSP = "\u200b"
BOM = "\ufeff"
SOFT_HYPHEN = "\u00ad"

# Signs
ANUSVARA = "\u0d82"  # ං
VISARGA = "\u0d83"  # ඃ
AL_LAKUNA = "\u0dca"  # ් (virama)

# Pre-base vowel signs: drawn to the LEFT of the consonant, stored AFTER it.
KOMBUVA = "\u0dd9"  # ෙ
KOMBU_DEKA = "\u0ddb"  # ෛ

# Characters that matter for the specific rules below
YAYANNA = "\u0dba"  # ය
RAYANNA = "\u0dbb"  # ර

# Regex classes (use inside [...])
CONSONANTS = "\u0d9a-\u0dc6"
DEPENDENT_VOWELS = "\u0dcf-\u0ddf\u0df2\u0df3"
SINHALA = "\u0d80-\u0dff"

# A consonant optionally joined (al-lakuna + ZWJ) to further consonants, e.g.
# ka, ka + al-lakuna + ZWJ + ya (yansaya), ... + ra (rakaransaya), or a
# conjunct such as ka + al-lakuna + ZWJ + ssa. This is the unit a pre-base
# vowel sign attaches to.
CLUSTER = f"[{CONSONANTS}](?:{AL_LAKUNA}{ZWJ}[{CONSONANTS}])*"

# Independent vowels that are commonly built from a base vowel + sign, because
# they look the same on screen (e.g. අ + ා renders like ආ). Not canonical
# equivalents in Unicode, so NFC does not fix them.
VOWEL_COMPOSITIONS = {
    "\u0d85\u0dcf": "\u0d86",  # අ + ා → ආ
    "\u0d85\u0dd0": "\u0d87",  # අ + ැ → ඇ
    "\u0d85\u0dd1": "\u0d88",  # අ + ෑ → ඈ
    "\u0d8b\u0ddf": "\u0d8c",  # උ + ෟ → ඌ
    "\u0d91\u0dca": "\u0d92",  # එ + ් → ඒ
    "\u0dd9\u0d91": "\u0d93",  # ෙ + එ → ඓ
    "\u0d94\u0dca": "\u0d95",  # ඔ + ් → ඕ
    "\u0d94\u0ddf": "\u0d96",  # ඔ + ෟ → ඖ
}
