from sinhalanorm import check, normalize

ZWJ = "\u200d"


def codes(text: str) -> list:
    return [i.code for i in check(text)]


def test_clean_text_has_no_issues() -> None:
    assert check("ශ්" + ZWJ + "රී ලංකාව කොළඹ") == []
    assert check("") == []


def test_kombuva_order_reported_with_original_span() -> None:
    (issue,) = check("ෙකාළඹ")
    assert issue.code == "kombuva_order"
    assert (issue.start, issue.end, issue.text) == (0, 2, "ෙක")
    assert issue.fixable


def test_zwj_issues() -> None:
    assert codes("ක" + ZWJ + "්ය") == ["zwj_order"]
    assert codes("ක" + ZWJ + "ම") == ["zwj_stray"]


def test_valid_zwj_not_reported() -> None:
    assert codes("ක්" + ZWJ + "ෂ") == []


def test_vowel_composition() -> None:
    (issue,) = check("අාලය")
    assert issue.code == "vowel_composition"
    assert issue.text == "අා"


def test_not_nfc() -> None:
    assert codes("ක" + "ෙ" + "ා") == ["not_nfc"]


def test_orphan_sign_not_fixable() -> None:
    issues = check("ා ක")
    assert [(i.code, i.fixable) for i in issues] == [("orphan_sign", False)]


def test_positions_after_precomposed_chars() -> None:
    # 'කො' decomposes to 3 code points internally; the reported index must
    # still point into the caller's string.
    text = "කො අාව"
    (issue,) = check(text)
    assert text[issue.start : issue.end] == "අා"


def test_every_fixable_issue_is_fixed() -> None:
    text = "\ufeffෙකාළඹ අාලය ක" + ZWJ + "්ය කංා"
    assert any(i.fixable for i in check(text))
    assert [i for i in check(normalize(text)) if i.fixable] == []
