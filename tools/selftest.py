#!/usr/bin/env python3
"""Самотест конвейера обезличивания: python tools/selftest.py

Проверяет главное свойство — переносимость на другую машину:
пути берутся из окружения, структурные шаблоны ловят любого пользователя
на Windows, Linux и macOS, а плейсхолдеры (<username>, <...>) не считаются грязью.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAILED: list[str] = []


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(condition: bool, label: str, detail: str = "") -> None:
    mark = "OK  " if condition else "FAIL"
    print(f"  [{mark}] {label}" + (f" — {detail}" if detail and not condition else ""))
    if not condition:
        FAILED.append(label)


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    anon = load_module("anon", "anonymize.py")
    gate = load_module("gate", "check-anonymized.py")

    rules = anon.read_json(HERE / "anonymize.rules.json")
    local = {
        "text_replacements": [["Иван Петрович", "пользователь"]],
        "regex_replacements": [],
        "forbidden_patterns": ["Иван"],
    }

    print("Тест 1: другая машина (другой пользователь, другой путь к памяти)")
    old_memory = os.environ.get("MEMORY_DIR")
    os.environ["MEMORY_DIR"] = "/srv/letta/memfs/agent-x/memory"
    try:
        pairs, home_pair = anon.build_path_pairs(rules)
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "sample.md"
            target.write_text(
                "Память: /srv/letta/memfs/agent-x/memory/system/persona.md\n"
                "Windows: C:\\Users\\ivan\\Documents\\report.docx\n"
                "Linux: /home/ivan/work/proj/file.txt\n"
                "macOS: /Users/ivan/Library/notes.md\n"
                "Автор: Иван Петрович\n",
                encoding="utf-8",
            )
            anon.apply_text(target, rules, local, pairs, home_pair, dry=False)
            got = target.read_text(encoding="utf-8")
    finally:
        if old_memory is None:
            os.environ.pop("MEMORY_DIR", None)
        else:
            os.environ["MEMORY_DIR"] = old_memory

    check("$MEMORY_DIR/system/persona.md" in got, "путь памяти из окружения -> $MEMORY_DIR", got)
    check("C:\\Users\\<username>\\Documents" in got, "Windows-логин -> <username>", got)
    check("/home/<username>/work/proj/file.txt" in got, "Linux-логин -> <username>", got)
    check("/Users/<username>/Library/notes.md" in got, "macOS-логин -> <username>", got)
    check("пользователь" in got and "Иван" not in got, "локальный слой вычистил имя", got)

    print("Тест 2: гейт различает грязь и плейсхолдеры")
    patterns = gate.compile_patterns(rules, local)

    def hits(text: str) -> bool:
        return any(p.search(text) for p in patterns)

    check(hits("C:\\Users\\ivan\\Documents"), "гейт ловит Windows-логин")
    check(hits("/home/ivan/work"), "гейт ловит Linux-логин")
    check(hits("/Users/ivan/Library"), "гейт ловит macOS-логин")
    check(hits("Иван Петрович"), "гейт ловит имя из локального слоя")
    check(not hits("C:\\Users\\<username>\\Documents"), "гейт пропускает <username>")
    check(not hits("C:\\Users\\<user>\\AppData"), "гейт пропускает любой <...> плейсхолдер")
    check(not hits("~/projects/file.txt"), "гейт пропускает ~")
    check(not hits("$MEMORY_DIR/system/persona.md"), "гейт пропускает $MEMORY_DIR")

    print("Тест 3: локальный слой не обязателен, но о его отсутствии сообщается")
    check(isinstance(anon.read_json(HERE / "нет-такого.json"), dict), "read_json устойчив к отсутствию файла")

    print("Тест 4: генератор каркаса проекта")
    gen = load_module("gen", "new-project.py")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        proj = root / "projects"
        proj.mkdir(parents=True)
        (proj / "index.json").write_text(
            json.dumps(
                {
                    "_note": "temp",
                    "projects": {},
                    "archived": {},
                    "statistics": {"total": 0, "active": 0, "archived": 0, "last_updated": ""},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (proj / "_template.json").write_text(
            json.dumps(
                {"fields": {"git": {"value": {"local": {"enabled": False}, "remote": {"enabled": False}}}}},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (proj / "index.md").write_text(
            "---\ndescription: x\n---\n# Связи\n## [[path]] links to all projects\n", encoding="utf-8"
        )

        gen.create_project(
            root,
            name_en="demo-proj",
            title="Демо",
            physical_path="C:\\Work\\demo",
            description="Описание",
            status="active",
            tags=["t1"],
            dry=False,
        )
        cfg = (proj / "demo-proj" / "config.md").read_text(encoding="utf-8")
        check("Демо" in cfg and "C:\\Work\\demo" in cfg, "шаблон подставил title и path", cfg)
        index = json.loads((proj / "index.json").read_text(encoding="utf-8"))
        check(index["projects"]["demo-proj"]["status"] == "active", "манифест: проект добавлен")
        check(
            index["statistics"]["total"] == 1 and index["statistics"]["active"] == 1,
            "statistics пересчитан",
        )
        md = (proj / "index.md").read_text(encoding="utf-8")
        check("[[projects/demo-proj/notes.md]]" in md, "index.md: добавлены ссылки")

        try:
            gen.create_project(root, name_en="demo-proj", title="Демо", physical_path="C:\\Work\\demo")
            check(False, "повторное создание отклонено")
        except ValueError:
            check(True, "повторное создание отклонено")
        try:
            gen.create_project(root, name_en="Плохой", title="x", physical_path="C:\\x")
            check(False, "нелатинский name_en отклонён")
        except ValueError:
            check(True, "нелатинский name_en отклонён")

    print("Тест 5: локальные файлы не попадают в слепок")
    rules_lf = dict(rules)
    rules_lf["local_files"] = ["reference/lessons/local-only.md"]
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        local_file = root / "reference" / "lessons" / "local-only.md"
        local_file.parent.mkdir(parents=True)
        local_file.write_text("локальный справочник", encoding="utf-8")
        keep_file = root / "reference" / "lessons.md"
        keep_file.write_text("индекс", encoding="utf-8")
        old_root = anon.ROOT
        anon.ROOT = root
        try:
            log = anon.process_local_files(rules_lf, dry=False)
        finally:
            anon.ROOT = old_root
        check(not local_file.exists(), "локальный файл удалён из слепка", str(log))
        check(keep_file.exists(), "остальные файлы не тронуты")

    if FAILED:
        print(f"\nПРОВАЛЕНО: {len(FAILED)} проверок -> {', '.join(FAILED)}")
        return 1
    print("\nВСЕ ПРОВЕРКИ ПРОЙДЕНЫ.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
