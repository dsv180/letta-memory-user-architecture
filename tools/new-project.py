#!/usr/bin/env python3
"""Генератор каркаса проекта в MemFS.

Делает механическую часть создания проекта:
  - создаёт projects/<name_en>/ с обязательными файлами из tools/templates/project/;
  - добавляет запись в projects/index.json и обновляет statistics;
  - добавляет [[path]]-ссылки в projects/index.md.

Смысловую часть (название, путь, описание, статус) подставляет тот, кто вызывает.
Физическую папку на диске генератор НЕ создаёт — она вне репозитория, её создаёт
пользователь/агент по physical_path.

Использование:
    python tools/new-project.py --name-en my-proj --title "Мой проект" \
        --path "C:\\Work\\my-proj" --description "Кратко о проекте"
    python tools/new-project.py ... --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TEMPLATES = HERE / "templates" / "project"
PROJECT_FILES = ["config.md", "notes.md", "tasks.md"]
STATUSES = ["proposal", "planning", "active", "paused", "completed", "published", "archived"]
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )


def create_project(
    root: Path,
    *,
    name_en: str,
    title: str,
    physical_path: str,
    description: str = "",
    status: str = "proposal",
    tags: list[str] | None = None,
    dry: bool = False,
) -> list[str]:
    """Возвращает список строк-отчёта. Бросает ValueError на неверных входных данных."""
    if not NAME_RE.match(name_en):
        raise ValueError(f"name_en должен быть латиницей в нижнем регистре: {name_en!r}")
    if status not in STATUSES:
        raise ValueError(f"status должен быть одним из {STATUSES}: {status!r}")
    if not title.strip():
        raise ValueError("title обязателен")
    if not physical_path.strip():
        raise ValueError("physical_path обязателен")

    projects_dir = root / "projects"
    index_path = projects_dir / "index.json"
    index_md = projects_dir / "index.md"
    project_dir = projects_dir / name_en

    if not index_path.is_file():
        raise ValueError(f"нет манифеста: {index_path}")
    index = read_json(index_path)
    if name_en in index.get("projects", {}) or name_en in index.get("archived", {}):
        raise ValueError(f"проект {name_en!r} уже есть в манифесте")
    if project_dir.exists():
        raise ValueError(f"папка уже существует: {project_dir}")

    templates_meta = read_json(projects_dir / "_template.json") if (
        projects_dir / "_template.json"
    ).is_file() else {}
    default_git = (
        templates_meta.get("fields", {}).get("git", {}).get("value")
        or {"local": {"enabled": False}, "remote": {"enabled": False}}
    )

    today = date.today().isoformat()
    entry = {
        "title": title,
        "name_en": name_en,
        "description": description,
        "status": status,
        "created_at": today,
        "project_home": f"projects/{name_en}",
        "physical_path": physical_path,
        "git": default_git,
        "depends_on": [],
        "skills": [],
        "tags": tags or [],
        "version": 1,
        "metadata": {},
    }

    log: list[str] = []
    subs = {
        "{{title}}": title,
        "{{name_en}}": name_en,
        "{{physical_path}}": physical_path,
        "{{description}}": description,
    }

    for name in PROJECT_FILES:
        src = TEMPLATES / name
        text = src.read_text(encoding="utf-8")
        for key, value in subs.items():
            text = text.replace(key, value)
        log.append(f"create {project_dir.relative_to(root) / name}")
        if not dry:
            project_dir.mkdir(parents=True, exist_ok=True)
            (project_dir / name).write_text(text, encoding="utf-8", newline="\n")

    index.setdefault("projects", {})[name_en] = entry
    stats = index.setdefault("statistics", {})
    stats["total"] = len(index.get("projects", {})) + len(index.get("archived", {}))
    stats["active"] = sum(
        1 for p in index.get("projects", {}).values() if p.get("status") == "active"
    )
    stats["archived"] = len(index.get("archived", {}))
    stats["last_updated"] = today
    log.append(f"update {index_path.relative_to(root)} (projects.{name_en}, statistics)")
    if not dry:
        write_json(index_path, index)

    links = "\n".join(f"- [[projects/{name_en}/{name}]]" for name in PROJECT_FILES)
    log.append(f"append {index_md.relative_to(root)} (+{len(PROJECT_FILES)} ссылок)")
    if not dry and index_md.is_file():
        text = index_md.read_text(encoding="utf-8").rstrip("\n")
        index_md.write_text(f"{text}\n{links}\n", encoding="utf-8", newline="\n")

    return log


def main() -> int:
    force_utf8()
    parser = argparse.ArgumentParser(description="Создать каркас проекта в MemFS.")
    parser.add_argument("--name-en", required=True, help="латинский идентификатор (имя папки)")
    parser.add_argument("--title", required=True, help="русское название проекта")
    parser.add_argument("--path", required=True, help="physical_path: папка проекта на диске")
    parser.add_argument("--description", default="", help="краткое описание")
    parser.add_argument("--status", default="proposal", choices=STATUSES)
    parser.add_argument("--tags", default="", help="теги через запятую")
    parser.add_argument("--root", default=str(ROOT), help="корень репозитория (по умолчанию — свой)")
    parser.add_argument("--dry-run", action="store_true", help="только показать план")
    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    try:
        log = create_project(
            Path(args.root),
            name_en=args.name_en,
            title=args.title,
            physical_path=args.path,
            description=args.description,
            status=args.status,
            tags=tags,
            dry=args.dry_run,
        )
    except ValueError as exc:
        print(f"Ошибка: {exc}")
        return 1

    print(f"Режим: {'DRY-RUN' if args.dry_run else 'СОЗДАНИЕ'}")
    for line in log:
        print("  " + line)
    print(
        "\nОсталось вручную:\n"
        f"  1. Создать физическую папку: {args.path}\n"
        "  2. Заполнить notes.md (смысл, специфика) и config.md (инструменты)\n"
        "  3. Если проект использует git — заполнить блок git в index.json"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
