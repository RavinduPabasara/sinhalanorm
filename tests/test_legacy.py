import pytest

from sinhalanorm import FONTS, is_normalized, legacy_to_unicode

ZWJ = "\u200d"
YANSAYA = "්" + ZWJ + "ය"
RAKARANSAYA = "්" + ZWJ + "ර"


@pytest.mark.parametrize(
    "legacy,unicode",
    [
        ("Y%S ,xld", "ශ" + RAKARANSAYA + "ී ලංකා"),
        ("isxy,", "සිංහල"),
        ("wïud", "අම්මා"),
        ("Tn", "ඔබ"),
        ("uy;a", "මහත්"),
        ("fokjd", "දෙනවා"),
        ("fjkqfjka", "වෙනුවෙන්"),
        ("fmd;", "පොත"),
        ("fld<U", "කොළඹ"),
        ("fiaj", "සේව"),
        ("ffjoH", "වෛද" + YANSAYA),
        ("úoHdj", "විද" + YANSAYA + "ාව"),
        ("fYa%Ksh", "ශ" + RAKARANSAYA + "ේණිය"),
        ("fYa%Ksh".replace("a%", "%a"), "ශ" + RAKARANSAYA + "ේණිය"),
        ("wdKavqj", "ආණ්ඩුව"),
        ("ta", "ඒ"),
        ("lfl", "කකෙ"),
        ("rel", "රුක"),
        ("CIK", "ක" + "්" + ZWJ + "ෂණ"),
        ("›", "ශ" + RAKARANSAYA + "ී"),
        ("fm!", "පෞ"),
    ],
)
def test_words(legacy: str, unicode: str) -> None:
    assert legacy_to_unicode(legacy) == unicode


# Cases found by converting real FM-Abhaya documents (government gazettes,
# NIE publications, a Grade 9 maths textbook); each one was a bug before.
@pytest.mark.parametrize(
    "legacy,unicode",
    [
        ("úµd,h", "විද" + YANSAYA + "ාලය"),  # µ = ද්\u200dය
        ("fjf<`om<", "වෙළෙඳපළ"),  # ` = sannaka prefix
        ("f.dvke`.Su", "ගොඩනැඟීම"),
        ("È<s`ÿlu", "දිළිඳුකම"),  # sannaka on a precomposed glyph
        (";s%fldaK", "ත" + RAKARANSAYA + "ිකෝණ"),  # vowel sign before %
        ("flaïì%Ê", "කේම්බ" + RAKARANSAYA + "ිජ්"),
        ("fí%,a", "බ" + RAKARANSAYA + "ෙල්"),  # glyph with ් followed by %
        ("nyd¨ï", "බහාලුම්"),  # ¨ = ලු
        ("Æ;¾jd§ka", "ලූතර්වාදීන්"),  # Æ = ලූ
        ("¥IKh", "දූෂණය"),  # ¥ = දූ
        ("y\\qkajd", "හඳුන්වා"),  # \ = ඳ
        ("*a?kala", "ෆ" + RAKARANSAYA + "ෑන්ක්"),  # a? = ්\u200dරෑ
        ("ã'iS'", "ඩී.සී."),  # ã = ඩී
        ("ksYaÑ;", "නිශ්චිත"),  # Ñ = චි
        ("h:djd§", "යථාවාදී"),
        ("RcqfldaK", "ඍජුකෝණ"),  # R = ඍ
    ],
)
def test_real_document_cases(legacy: str, unicode: str) -> None:
    assert legacy_to_unicode(legacy) == unicode


# Damindu cases from real Sri Lankan government circulars (1990s-2001).
@pytest.mark.parametrize(
    "legacy,unicode",
    [
        ("mÑmd,k", "පරිපාලන"),  # Ñ = රි (චි in FM)
        ("f,alà", "ලේකම්"),  # à = ම් (ටී in FM)
        ("ls¯fà°", "කිරීමේදී"),
        ("Wiiaèà", "උසස්වීම්"),
        ("ëòëOdk", "විධිවිධාන"),
        ("wh¥àm;%h", "අයදුම්පත" + RAKARANSAYA + "ය"),
        ("±Æ", "දැඩි"),
        ("isåk", "සිටින"),
        ("lrâ$fkdlrâ", "කරමි/නොකරමි"),
        ("bx‚fkare", "ඉංජිනේරු"),
        ("yákdf.k", "හඳුනාගෙන"),
        ("ëµd,", "විද" + YANSAYA + "ාල"),
        ("†kh", "දිනය"),
        ("t<üug", "එළඹීමට"),
        ("tlÕ;ajh", "එකඟත්වය"),
        ("mÑÄfPAofha", "පරිච්ඡේදයේ"),
        ("ku()", "නම:—"),  # ) is a long dash, not *
    ],
)
def test_damindu(legacy: str, unicode: str) -> None:
    assert legacy_to_unicode(legacy, font="damindu") == unicode


def test_damindu_smart_quotes_are_punctuation() -> None:
    # Word turned the ' and " keys into smart quotes; Damindu draws them as
    # the full stop and comma.
    assert legacy_to_unicode(",efæ\x92", font="damindu") == "ලැබේ."
    assert legacy_to_unicode("kà\x94", font="damindu") == "නම්,"


def test_damindu_has_no_sannaka_prefix() -> None:
    assert legacy_to_unicode("`", font="damindu") == "!"
    assert legacy_to_unicode("`o", font="damindu") == "!ද"


def test_damindu_unmapped_glyph_passes_through() -> None:
    # Glyphs without enough evidence stay visible instead of being guessed.
    assert legacy_to_unicode("Å", font="damindu") == "Å"


def test_same_text_differs_between_fonts() -> None:
    assert legacy_to_unicode("mÑmd,k", font="damindu") == "පරිපාලන"
    assert legacy_to_unicode("mÑmd,k", font="fm-abhaya") == "පචිපාලන"


def test_real_sentence() -> None:
    raw = "rdcH ks,OdÍkag uqla;sh ysñ jk mßÈ"
    expected = "රාජ" + YANSAYA + " නිලධාරීන්ට මුක්තිය හිමි වන පරිදි"
    assert legacy_to_unicode(raw) == expected


def test_sentence_with_punctuation() -> None:
    assert legacy_to_unicode("Tn fokjd' wïud\"") == "ඔබ දෙනවා. අම්මා,"


def test_digits_and_whitespace_pass_through() -> None:
    assert legacy_to_unicode("2024 \n isxy,") == "2024 \n සිංහල"


def test_c1_control_decoded_as_cp1252() -> None:
    # '\x9b' is how '›' (ශ්\u200dරී) arrives when cp1252 text is decoded as Latin-1.
    assert legacy_to_unicode("\x9b") == legacy_to_unicode("›")


def test_output_is_normalized() -> None:
    for text in ["Y%S ,xld", "ffjoH", "fYa%Ksh", "wdKavqj"]:
        assert is_normalized(legacy_to_unicode(text))


def test_font_name_case_insensitive() -> None:
    assert legacy_to_unicode("isxy,", font="FM-Abhaya") == "සිංහල"


def test_unknown_font() -> None:
    with pytest.raises(ValueError, match="damindu, fm-abhaya"):
        legacy_to_unicode("x", font="dl-manel")


def test_fonts_registry() -> None:
    assert set(FONTS) == {"fm-abhaya", "damindu"}
