"""Command-line interface: ``sinhalanorm {normalize,check,legacy} [FILE]``."""

import argparse
import sys
from typing import List, Optional

from . import __version__
from .check import check
from .legacy import FONTS, legacy_to_unicode
from .normalize import normalize


def _read(path: Optional[str]) -> str:
    if path is None or path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as f:
        return f.read()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sinhalanorm",
        description="Normalize Sinhala text and convert legacy-font Sinhala.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_norm = sub.add_parser("normalize", help="print the normalized text")
    p_norm.add_argument("file", nargs="?", help="input file (default: stdin)")
    p_norm.add_argument(
        "--skip", action="append", default=[], metavar="RULE", help="rule code to skip"
    )

    p_check = sub.add_parser(
        "check", help="list problems; exit status 1 if any are found"
    )
    p_check.add_argument("file", nargs="?", help="input file (default: stdin)")

    p_legacy = sub.add_parser("legacy", help="convert legacy-font text to Unicode")
    p_legacy.add_argument("file", nargs="?", help="input file (default: stdin)")
    p_legacy.add_argument(
        "--font", default="fm-abhaya", choices=sorted(FONTS), help="legacy font"
    )

    args = parser.parse_args(argv)
    text = _read(args.file)

    if args.command == "normalize":
        try:
            sys.stdout.write(normalize(text, skip=args.skip))
        except ValueError as e:
            parser.error(str(e))
        return 0

    if args.command == "legacy":
        sys.stdout.write(legacy_to_unicode(text, font=args.font))
        return 0

    issues = check(text)
    for issue in issues:
        line = text.count("\n", 0, issue.start) + 1
        col = issue.start - (text.rfind("\n", 0, issue.start) + 1) + 1
        fix = "" if issue.fixable else " (not auto-fixable)"
        print(f"{line}:{col}: {issue.code}: {issue.text!r}: {issue.message}{fix}")
    return 1 if issues else 0
