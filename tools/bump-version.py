#!/usr/bin/env python3
"""Поднять версию архитектуры памяти в `description` каждого файла.

Версия хранится внутри `description` во frontmatter — `... version: 1.4`.
Отдельного поля `version` нет (см. reference/lessons/yaml.md). Версия
проставляется во всех файлах слоёв памяти, поэтому подъём версии —
механическая операция, а не ручная правка по файлам.

Использование:
    python tools/bump-version.py 1.4 1.5                      # корень репо (слепок)
    python tools/bump-version.py 1.4 1.5 --root "$env:MEMORY_DIR"
    python tools/bump-version.py 1.4 1.5 --dry-run

Кроссплатформенно, UTF-8, LF. Пропускает `.git`, `__pycache__`, `.temp`.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", ".temp", "node_modules"}
SKIP_FILES = {"CHANGELOG.md"}


def force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def target_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for path in sorted(root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_FILES:
            continue
        out.append(path)
    return out


def main() -> int:
    force_utf8()
    parser = argparse.ArgumentParser(description="Поднять версию архитектуры в description файлов.")
    parser.add_argument("old", help="текущая версия, например 1.4")
    parser.add_argument("new", help="новая версия, например 1.5")
    parser.add_argument("--root", default=None, help="корень обхода (по умолчанию — корень репозитория)")
    parser.add_argument("--dry-run", action="store_true", help="только показать изменения")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve() if args.root else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"Нет такой папки: {root}")
        return 2

    pattern = re.compile(r"(version:\s*)" + re.escape(args.old) + r"\b")
    print(f"Корень: {root}")
    print(f"Версия: {args.old} -> {args.new}")
    print(f"Режим: {'DRY-RUN' if args.dry_run else 'ПРИМЕНЕНИЕ'}")

    changed = 0
    total = 0
    for path in target_files(root):
        try:
            original = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        text, count = pattern.subn(lambda m: m.group(1) + args.new, original)
        if not count:
            continue
        changed += 1
        total += count
        rel = path.relative_to(root)
        print(f"  {rel}: x{count}")
        if not args.dry_run:
            path.write_text(text, encoding="utf-8", newline="\n")

    print(f"Готово. Файлов: {changed}, замен: {total}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
