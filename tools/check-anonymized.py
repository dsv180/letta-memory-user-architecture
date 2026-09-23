#!/usr/bin/env python3
"""Гейт обезличивания: проверяет, что в слепке нет персональных данных.

Проверяет два слоя паттернов:
  tools/anonymize.rules.json  — общий: структурные шаблоны путей (любой
      C:\\Users\\<кто-то>, /home/<кто-то>), машинно-независимо.
  tools/anonymize.local.json  — локальный (в .gitignore): имена, организации,
      специфичные диски.

Возвращает exit 1 при первом же найденном совпадении с номерами строк.
Рассчитан на запуск перед push (pre-push hook) и как ручная проверка.

Кроссплатформенно, UTF-8.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RULES_PATH = HERE / "anonymize.rules.json"
LOCAL_PATH = HERE / "anonymize.local.json"


def force_utf8() -> None:
    """Чтобы русский текст в консоли не превращался в кракозябры."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def compile_patterns(rules: dict, local: dict) -> list[re.Pattern]:
    """Общий слой + локальный слой -> скомпилированные паттерны."""
    raw = list(rules.get("forbidden_patterns", [])) + list(
        local.get("forbidden_patterns", [])
    )
    return [re.compile(p, re.IGNORECASE) for p in raw]


def iter_files(scan: list[str]):
    for item in scan:
        p = ROOT / item
        if p.is_file():
            yield p
        elif p.is_dir():
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames[:] = [d for d in dirnames if d != ".git"]
                for name in filenames:
                    yield Path(dirpath) / name


def main() -> int:
    force_utf8()
    rules = read_json(RULES_PATH)
    local_present = LOCAL_PATH.is_file()
    local = read_json(LOCAL_PATH)

    compiled = compile_patterns(rules, local)

    if not local_present:
        print(
            "ПРЕДУПРЕЖДЕНИЕ: нет tools/anonymize.local.json — проверяются только "
            "структурные паттерны. Имена и организации этой машины не проверяются."
        )

    hits: list[str] = []
    for path in iter_files(rules.get("scan", [])):
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, IsADirectoryError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for pat in compiled:
                if pat.search(line):
                    try:
                        where = path.relative_to(ROOT)
                    except ValueError:
                        where = path
                    hits.append(f"{where}:{lineno}: {line.strip()[:160]}")

    if hits:
        print("ГЕЙТ НЕ ПРОЙДЕН — найдены персональные данные:")
        for h in hits:
            print("  " + h)
        return 1

    print(f"ГЕЙТ ПРОЙДЕН: проверено {len(compiled)} паттернов, совпадений нет.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
