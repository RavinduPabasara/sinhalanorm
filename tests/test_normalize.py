import unicodedata

import pytest

from sinhalanorm import RULE_CODES, is_normalized, normalize

ZWJ = "\u200d"
ZWNJ = "\u200c"
ZWSP = "\u200b"
YANSAYA = "්" + ZWJ + "ය"
RAKARANSAYA = "්" + ZWJ + "ර"


class TestPassThrough:
    @pytest.mark.parametrize(
        "text",
        [
            "",
            "hello world",
            "ශ" + RAKARANSAYA + "ී ලංකා",
            "කොළඹ",
            "විද" + YANSAYA + "ාව",
            "123 ABC ..!",
            "👨" + ZWJ + "👩" + ZWJ + "👧",  # emoji ZWJ sequence untouched
        ],
    )
    def test_already_normal_text_is_unchanged(self, text: str) -> None:
        assert normalize(text) == text
        assert is_normalized(text)

    def test_output_is_nfc(self) -> None:
        out = normalize("ක" + "ෙ" + "ා")
        assert out == unicodedata.normalize("NFC", out) == "කො"


class TestInvisible:
    def test_bom_and_soft_hyphen_removed(self) -> None:
        assert normalize("\ufeffසිං\u00adහල") == "සිංහල"

    def test_zwsp_and_zwnj_inside_sinhala_removed(self) -> None:
        assert normalize("සිං" + ZWSP + "හල") == "සිංහල"
        assert normalize("සිං" + ZWNJ + "හල") == "සිංහල"

    def test_zwsp_between_latin_kept(self) -> None:
        assert normalize("a" + ZWSP + "b") == "a" + ZWSP + "b"


class TestZWJ:
    def test_zwj_before_al_lakuna_in_yansaya(self) -> None:
        assert normalize("ක" + ZWJ + "්ය") == "ක" + YANSAYA

    def test_zwj_before_al_lakuna_in_rakaransaya(self) -> None:
        assert normalize("ප" + ZWJ + "්රශ්නය") == "ප" + RAKARANSAYA + "ශ්නය"

    def test_zwj_before_al_lakuna_in_repaya(self) -> None:
        assert normalize("ධර" + ZWJ + "්මය") == "ධර්" + ZWJ + "මය"

    def test_repeated_zwj_collapsed(self) -> None:
        assert normalize("ක්" + ZWJ * 3 + "ය") == "ක" + YANSAYA

    def test_stray_zwj_removed(self) -> None:
        assert normalize("ක" + ZWJ + "ම") == "කම"
        assert normalize("කා" + ZWJ) == "කා"

    def test_valid_zwj_kept(self) -> None:
        text = "ක්" + ZWJ + "ෂ"
        assert normalize(text) == text


class TestOrder:
    def test_kombuva_typed_before_consonant(self) -> None:
        assert normalize("ෙකාළඹ") == "කොළඹ"

    def test_kombuva_before_joined_cluster(self) -> None:
        assert normalize("ෙක" + YANSAYA) == "ක" + YANSAYA + "ෙ"

    def test_kombuva_with_al_lakuna(self) -> None:
        assert normalize("ෙස්වය") == "සේවය"

    def test_kombuva_after_consonant_not_moved(self) -> None:
        assert normalize("කෙක") == "කෙක"

    def test_kombuva_mid_word_after_vowel_sign(self) -> None:
        assert normalize("කාෙල") == "කාලෙ"

    def test_vowel_sign_before_rakaransaya(self) -> None:
        assert normalize("ති" + RAKARANSAYA + "කෝණ") == "ත" + RAKARANSAYA + "ිකෝණ"
        assert normalize("කෙ" + YANSAYA) == "ක" + YANSAYA + "ෙ"

    def test_double_kombuva(self) -> None:
        assert normalize("වෙෙද" + YANSAYA) == "වෛද" + YANSAYA

    def test_anusvara_before_vowel_sign(self) -> None:
        assert normalize("ලංකා") == "ලංකා"
        assert normalize("කංා") == "කාං"

    def test_repeated_sign(self) -> None:
        assert normalize("කාා") == "කා"
        assert normalize("ක්්") == "ක්"


class TestVowelComposition:
    @pytest.mark.parametrize(
        "pair,single",
        [
            ("අා", "ආ"),
            ("අැ", "ඇ"),
            ("අෑ", "ඈ"),
            ("උෟ", "ඌ"),
            ("එ්", "ඒ"),
            ("ඔ්", "ඕ"),
            ("ඔෟ", "ඖ"),
        ],
    )
    def test_lookalike_pairs(self, pair: str, single: str) -> None:
        assert normalize(pair) == single
        assert normalize(pair + "ලය") == single + "ලය"


class TestSkip:
    def test_skip_rule(self) -> None:
        assert normalize("අාලය", skip=["vowel_composition"]) == "අාලය"
        assert normalize("ෙකාළඹ", skip={"kombuva_order"}) != "කොළඹ"

    def test_unknown_rule_raises(self) -> None:
        with pytest.raises(ValueError, match="nope"):
            normalize("x", skip=["nope"])

    def test_rule_codes(self) -> None:
        assert "kombuva_order" in RULE_CODES
        assert "vowel_composition" in RULE_CODES


def test_idempotent() -> None:
    samples = ["ෙකාළඹ", "ක" + ZWJ + "්ය", "අාලය", "කංා", "\ufeffසිං\u00adහල"]
    for s in samples:
        once = normalize(s)
        assert normalize(once) == once
