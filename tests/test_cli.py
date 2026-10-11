import io
from pathlib import Path

import pytest

from sinhalanorm.cli import main


def run(
    argv: list,
    stdin: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> tuple:
    monkeypatch.setattr("sys.stdin", io.StringIO(stdin))
    code = main(argv)
    return code, capsys.readouterr().out


def test_normalize(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    assert run(["normalize"], "ෙකාළඹ\n", monkeypatch, capsys) == (0, "කොළඹ\n")


def test_legacy(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture) -> None:
    assert run(["legacy"], "isxy,", monkeypatch, capsys) == (0, "සිංහල")


def test_legacy_damindu(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    assert run(["legacy", "--font", "damindu"], "mÑmd,k", monkeypatch, capsys) == (
        0,
        "පරිපාලන",
    )


def test_check_exit_status(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    code, out = run(["check"], "හරි\nෙකාළඹ", monkeypatch, capsys)
    assert code == 1
    assert out.startswith("2:1: kombuva_order:")
    assert run(["check"], "කොළඹ", monkeypatch, capsys) == (0, "")


def test_file_argument(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    f = tmp_path / "in.txt"
    f.write_text("අාලය", encoding="utf-8")
    assert main(["normalize", str(f)]) == 0
    assert capsys.readouterr().out == "ආලය"


def test_unknown_skip_rule(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("x"))
    with pytest.raises(SystemExit) as exc:
        main(["normalize", "--skip", "nope"])
    assert exc.value.code == 2
