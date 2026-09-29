# -*- coding: utf-8 -*-
"""Валидатор памяти: проверка требований reference/MEMORY-HEALTH.md.

Назначение — запускать до и после внедрения/обновления памяти (см.
memory-design/migration.md), чтобы поймать полу-мигрированное состояние:
frontmatter и версии, короткие и битые ссылки, скиллы вне папки скиллов,
служебные файлы не в служебной папке, лишние папки верхнего уровня, форма
манифеста, индексы и форма записи.

Запуск:
    python tools/validate_memory.py --memory "$env:MEMORY_DIR" [--style] [--max-lines N]

Возврат: 0 — нарушения не найдены; 1 — есть нарушения.

Исключения (общие для всего скрипта):
  * пути с компонентом на `_` (`_examples`, `_template.json`, `_good`/`_bad`,
    служебные папки) — образцы формы и служебное, не данные памяти;
  * `skills/<name>/SKILL.md` — у скиллов свой frontmatter (`name`, `description`,
    `version`) и своя версия, память-версия к ним не применяется;
  * `memory-design/deltas/*`, любые `journal.md` и `tasks.md` — файлы-хроники
    (даты и ход работ уместны, version не требуется);
  * примеры ссылок вида `[[path]]` в обратных кавычках и код-блоках — не ссылки.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

TOP_OK = {"system", "reference", "lessons", "project", "memory-design", "skills"}
ROOT_FILES_OK = {"profile.png", ".gitignore", ".gitattributes"}
SKIP_COMPONENTS = {".git", "state"}
ALLOWED_KEYS = {"description", "read_only", "limit"}

VER_RE = re.compile(r"version:\s*([0-9][0-9.]*)")
LINK_RE = re.compile(r"\[\[([^\]|]+)\]\]")
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:")
DATE_RE = re.compile(r"\(\d{2}\.\d{2}\.\d{4}")
ATTR_RE = re.compile(r"по (?:команде|просьбе|указанию|поручению)\s+(?:Сергея|пользователя|владельца)")
NUM_RE = re.compile(r"^\s*\d+[.)]\s")
BUL_RE = re.compile(r"^\s*[-*]\s")
CODE_RE = re.compile(r"```.*?```|`[^`\n]*`", re.S)

CATEGORY_ORDER = ("Папки верхнего уровня", "Слои", "Frontmatter", "Версии", "Ссылки",
                  "Проект", "Манифест", "Индексы", "Форма", "Сигналы")


def is_skipped(part: str) -> bool:
    """Служебное и образцы формы: `.git`, `state`, всё с ведущим `_`."""
    return part in SKIP_COMPONENTS or part.startswith("_")


def strip_code(text: str) -> str:
    """Убрать код-блоки и inline-код: примеры `[[path]]` — не ссылки."""
    return CODE_RE.sub(" ", text)


def is_chronicle(rel: str) -> bool:
    return (rel.endswith("journal.md") or rel.endswith("tasks.md")
            or rel.startswith("memory-design/deltas/"))


def is_skill(rel: str) -> bool:
    return rel.startswith("skills/") and rel.endswith("SKILL.md")


def collect_md(mem: Path):
    out = []
    for p in mem.rglob("*.md"):
        parts = p.relative_to(mem).parts
        if any(is_skipped(part) for part in parts):
            continue
        out.append(p)
    return sorted(out)


def parse_frontmatter(text: str):
    """Вернёт (ошибки, keys, version)."""
    errors = []
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ["нет открывающего ---"], [], None
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return ["нет закрывающего ---"], [], None
    block = lines[1:end]
    keys = [m.group(1) for line in block if (m := KEY_RE.match(line))]
    version = None
    vm = VER_RE.search("\n".join(block))
    if vm:
        version = vm.group(1)
    if "description" not in keys:
        errors.append("нет ключа description")
    extra = [k for k in keys if k not in ALLOWED_KEYS]
    if extra:
        errors.append("лишние ключи: " + ", ".join(extra))
    desc_line = next((l for l in block if l.strip().startswith("description:")), "")
    if desc_line and not desc_line.split(":", 1)[1].strip():
        errors.append("description пустой")
    return errors, keys, version


def resolve(mem: Path, target: str):
    cand = mem / target
    if cand.exists():
        return cand
    if not target.endswith(".md") and (mem / (target + ".md")).exists():
        return mem / (target + ".md")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--memory", default=os.environ.get("MEMORY_DIR", ""))
    ap.add_argument("--style", action="store_true")
    ap.add_argument("--max-lines", type=int, default=150)
    args = ap.parse_args()
    if not args.memory:
        sys.exit("нет MEMORY_DIR")
    mem = Path(args.memory)

    report = {}

    def add(cat, msg):
        report.setdefault(cat, []).append(msg)

    files = collect_md(mem)

    # 1-2. Frontmatter и версии
    manifest = {}
    mpath = mem / "memory-design" / "manifest.json"
    if mpath.exists():
        try:
            manifest = json.loads(mpath.read_text(encoding="utf-8"))
        except Exception as exc:
            add("Манифест", f"manifest.json не парсится: {exc}")
    mem_ver = manifest.get("memory_version")
    versions = {}
    for p in files:
        rel = p.relative_to(mem).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        skill = is_skill(rel)
        errs, keys, ver = parse_frontmatter(text)
        if skill:
            errs, ver = [], None  # у скиллов свой формат frontmatter и своя версия
        for e in errs:
            add("Frontmatter", f"{rel}: {e}")
        if ver:
            versions.setdefault(ver, []).append(rel)
        elif not skill and not is_chronicle(rel):
            add("Версии", f"{rel}: нет version в description")
    if mem_ver:
        for ver, paths in versions.items():
            if ver != mem_ver:
                add("Версии", f"version {ver} != memory_version {mem_ver}: " + ", ".join(paths))

    # 3. Ссылки
    for p in files:
        rel = p.relative_to(mem).as_posix()
        text = strip_code(p.read_text(encoding="utf-8", errors="replace"))
        for link in LINK_RE.findall(text):
            if "/" not in link:
                add("Ссылки", f"{rel}: короткая [[{link}]]")
            elif resolve(mem, link) is None:
                add("Ссылки", f"{rel}: битая [[{link}]]")

    # 4. Папки верхнего уровня
    for item in sorted(mem.iterdir()):
        name = item.name
        if is_skipped(name):
            continue
        if item.is_dir():
            if name not in TOP_OK:
                add("Папки верхнего уровня", f"лишняя папка: {name}/")
        elif name not in ROOT_FILES_OK:
            add("Папки верхнего уровня", f"файл в корне: {name}")

    # 5. Слои
    project_dir = mem / "project"
    if project_dir.exists():
        for item in sorted(project_dir.iterdir()):
            if item.is_file() and not is_skipped(item.name):
                add("Слои", f"файл прямо в project/: {item.name} (служебное — в reference/)")
    skills_dir = mem / "skills"
    if skills_dir.exists():
        for item in sorted(skills_dir.iterdir()):
            if item.is_dir() and not (item / "SKILL.md").exists():
                add("Слои", f"skills/{item.name}/ без SKILL.md")

    # 6. Проекты
    if project_dir.exists():
        for item in sorted(project_dir.iterdir()):
            if not item.is_dir() or is_skipped(item.name):
                continue
            for need in ("config.md", "notes.md", "tasks.md"):
                if not (item / need).exists():
                    add("Проект", f"project/{item.name}/: нет {need}")

    # 7. Манифест
    for key in ("canon", "local"):
        for entry in manifest.get(key, []):
            if entry.startswith(".") or "<" in entry:
                continue
            if resolve(mem, entry.rstrip("/")) is None:
                add("Манифест", f"{key}: {entry} — нет в памяти")

    # 8. Индексы
    lessons_md = mem / "reference" / "lessons.md"
    lesson_files = sorted(p.relative_to(mem).as_posix()
                          for p in (mem / "lessons").rglob("*.md")) if (mem / "lessons").exists() else []
    if lessons_md.exists():
        text = strip_code(lessons_md.read_text(encoding="utf-8", errors="replace"))
        listed = [l for l in LINK_RE.findall(text) if l.startswith("lessons/")]
        for f in lesson_files:
            if f not in listed:
                add("Индексы", f"lessons.md не перечисляет {f}")
        for l in listed:
            if l not in lesson_files:
                add("Индексы", f"lessons.md ссылается на отсутствующий {l}")
    index_json = mem / "reference" / "index.json"
    if index_json.exists():
        try:
            json.loads(index_json.read_text(encoding="utf-8"))
        except Exception as exc:
            add("Индексы", f"index.json не парсится: {exc}")
    index_md = mem / "reference" / "index.md"
    if index_md.exists():
        text = strip_code(index_md.read_text(encoding="utf-8", errors="replace"))
        listed = LINK_RE.findall(text)
        for l in listed:
            if resolve(mem, l) is None:
                add("Индексы", f"index.md: битая [[{l}]]")
        actual = sorted(p.relative_to(mem).as_posix()
                        for p in (mem / "project").rglob("*.md")
                        if not any(is_skipped(part) for part in p.relative_to(mem).parts)) if project_dir.exists() else []
        for a in actual:
            if a not in listed:
                add("Индексы", f"index.md не перечисляет {a}")
        for l in listed:
            if l.startswith("project/") and l not in actual:
                add("Индексы", f"index.md перечисляет отсутствующий {l}")

    # 9. Форма записи и сигналы
    if args.style:
        for p in files:
            rel = p.relative_to(mem).as_posix()
            text = p.read_text(encoding="utf-8", errors="replace")
            lines = text.splitlines()
            if is_chronicle(rel) or is_skill(rel):
                continue
            if DATE_RE.search(text):
                add("Форма", f"{rel}: дата вида (дд.мм.гггг)")
            for i, line in enumerate(lines, 1):
                if "не знание" in line or line.lstrip().startswith(("Пример", "**Пример")):
                    continue
                if ATTR_RE.search(line):
                    add("Форма", f"{rel}:{i}: атрибуция авторства")
                    break
            if len(lines) > args.max_lines:
                add("Форма", f"{rel}: {len(lines)} строк (> {args.max_lines})")
            if "## " not in text and len(lines) > 20:
                add("Форма", f"{rel}: нет разделов (## ) при длине {len(lines)}")
            nums = sum(1 for l in lines if NUM_RE.match(l))
            buls = sum(1 for l in lines if BUL_RE.match(l))
            if nums > 1 and buls > 1:
                add("Сигналы", f"{rel}: нумерация ({nums}) и буллеты ({buls}) — "
                               "проверить, что нумерация только в шагах процедур")

    total = 0
    for cat in CATEGORY_ORDER:
        items = report.get(cat)
        if not items:
            continue
        total += len(items)
        print(f"\n=== {cat} ({len(items)}) ===")
        for msg in items:
            print("  - " + msg)
    signals = len(report.get("Сигналы", []))
    hard = total - signals
    print(f"\nфайлов: {len(files)}, нарушений: {hard}, сигналов: {signals}")
    return 1 if hard else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
