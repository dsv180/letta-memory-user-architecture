#!/usr/bin/env python3
"""Обезличивание слепка памяти перед публикацией.

Два слоя правил:
  tools/anonymize.rules.json — ОБЩИЙ (публикуемый): переменные окружения,
      структурные шаблоны путей, политика projects. Не содержит личных данных.
  tools/anonymize.local.json — ЛОКАЛЬНЫЙ (в .gitignore): имена людей, названия
      организаций, специфичные диски/папки. Образец — anonymize.local.example.json.

Пути этой машины нормализуются к канону Letta (~, $MEMORY_DIR,
$LETTA_LOCAL_BACKEND_DIR, $LETTA_TRANSCRIPT_ROOT), поэтому правила переносимы
между машинами и ОС: на каждой машине пути берутся из её же окружения.

Кроссплатформенно (Windows/Linux/macOS), UTF-8, LF.

Использование:
    python tools/anonymize.py            # применить
    python tools/anonymize.py --dry-run  # показать планируемые изменения
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
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


def load_rules() -> tuple[dict, dict, bool]:
    rules = read_json(RULES_PATH)
    local_present = LOCAL_PATH.is_file()
    local = read_json(LOCAL_PATH)
    return rules, local, local_present


def variants(s: str) -> set[str]:
    """Путь может быть записан с прямыми или обратными слэшами."""
    out = {s}
    if "\\" in s:
        out.add(s.replace("\\", "/"))
    if "/" in s:
        out.add(s.replace("/", "\\"))
    return {v for v in out if v}


def build_path_pairs(rules: dict) -> tuple[list[tuple[str, str]], tuple[str, str] | None]:
    """Карта «реальный путь этой машины -> плейсхолдер Letta» из переменных окружения."""
    pairs: list[tuple[str, str]] = []
    for spec in rules.get("env_paths", []):
        raw = os.environ.get(spec["env"]) or spec.get("default")
        if not raw:
            continue
        real = os.path.normpath(os.path.expanduser(raw))
        pairs.append((real, spec["placeholder"]))
    # Специфичные пути (MEMORY_DIR и т.п.) — раньше общего дома.
    pairs.sort(key=lambda p: len(p[0]), reverse=True)

    home = os.path.expanduser("~")
    home_pair = (home, rules.get("home_placeholder", "~")) if home and home != "~" else None
    return pairs, home_pair


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


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def apply_text(
    path: Path,
    rules: dict,
    local: dict,
    path_pairs: list[tuple[str, str]],
    home_pair: tuple[str, str] | None,
    dry: bool,
) -> list[str]:
    try:
        original = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, IsADirectoryError, OSError):
        return []

    text = original
    changes: list[str] = []

    def literal(needle: str, repl: str) -> None:
        nonlocal text
        total = 0
        for v in variants(needle):
            count = text.count(v)
            if count:
                text = text.replace(v, repl)
                total += count
        if total:
            changes.append(f"{needle!r} -> {repl!r} x{total}")

    # 1. Пути из окружения этой машины -> плейсхолдеры Letta
    for real, placeholder in path_pairs:
        literal(real, placeholder)
    # 2. Домашняя папка пользователя -> ~
    if home_pair:
        literal(home_pair[0], home_pair[1])
    # 3. Локальный слой: имена, организации, специфичные пути
    for src, dst in local.get("text_replacements", []):
        literal(src, dst)
    # 4. Общий слой: текстовые замены (если появятся)
    for src, dst in rules.get("text_replacements", []):
        literal(src, dst)
    # 5. Регулярные выражения: общий + локальный
    for pattern, repl in list(rules.get("regex_replacements", [])) + list(
        local.get("regex_replacements", [])
    ):
        text, count = re.subn(pattern, repl, text)
        if count:
            changes.append(f"regex {pattern!r} -> {repl!r} x{count}")

    if text == original:
        return []
    if not dry:
        path.write_text(text, encoding="utf-8", newline="\n")
    return changes


def process_projects(rules: dict, dry: bool) -> list[str]:
    cfg = rules.get("projects")
    if not cfg:
        return []
    proj = ROOT / cfg["dir"]
    if not proj.is_dir():
        return []
    keep = set(cfg.get("keep_as_examples", []))
    examples = proj / "_examples"
    log = []
    for child in sorted(proj.iterdir()):
        if not child.is_dir() or child.name == "_examples":
            continue
        if child.name in keep:
            dest = examples / child.name
            log.append(f"move   {rel(child)} -> {rel(dest)}")
            if not dry:
                examples.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.move(str(child), str(dest))
        else:
            log.append(f"delete {rel(child)}")
            if not dry:
                shutil.rmtree(child)
    tpl = cfg.get("index_template")
    if tpl:
        src = ROOT / tpl
        dst = proj / "index.json"
        if src.is_file():
            same = False
            if dst.is_file():
                same = src.read_text(encoding="utf-8") == dst.read_text(encoding="utf-8")
            if not same:
                log.append(f"reset  {rel(dst)} <- {tpl}")
                if not dry:
                    shutil.copyfile(src, dst)
    return log


def main() -> int:
    force_utf8()
    parser = argparse.ArgumentParser(description="Обезличить слепок памяти перед публикацией.")
    parser.add_argument("--dry-run", action="store_true", help="только показать изменения")
    args = parser.parse_args()

    rules, local, local_present = load_rules()
    path_pairs, home_pair = build_path_pairs(rules)

    print(f"Корень репо: {ROOT}")
    print(f"Режим: {'DRY-RUN' if args.dry_run else 'ПРИМЕНЕНИЕ'}")
    print("Слой 1 (общий):", RULES_PATH.name)
    if local_present:
        print("Слой 2 (локальный):", LOCAL_PATH.name)
    else:
        print(
            "Слой 2 (локальный): ОТСУТСТВУЕТ — имена и организации не будут вычищены.\n"
            "  Скопируйте tools/anonymize.local.example.json в tools/anonymize.local.json "
            "и впишите свои значения."
        )
    print("Карта путей этой машины:")
    for real, placeholder in path_pairs:
        print(f"  {real} -> {placeholder}")
    if home_pair:
        print(f"  {home_pair[0]} -> {home_pair[1]}")

    files_changed = 0
    subs = 0
    for path in iter_files(rules.get("scan", [])):
        changes = apply_text(path, rules, local, path_pairs, home_pair, args.dry_run)
        if changes:
            files_changed += 1
            subs += sum(int(c.rsplit(" x", 1)[1]) for c in changes)
            print(f"  {rel(path)}: " + "; ".join(changes))

    print("-- projects --")
    for line in process_projects(rules, args.dry_run):
        print("  " + line)

    print(f"Готово. Файлов изменено: {files_changed}, замен: {subs}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
