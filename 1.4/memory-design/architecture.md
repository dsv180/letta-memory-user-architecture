---
description: "Memory architecture — layers, files, rules. version: 1.4"
---
# Устройство памяти
**version: 1.4**
Карта того, как устроена память. Перед записью в память — сверься с этим файлом.
---
## Слои
### system/ — ядро (всегда в контексте)
- persona.md — личность и главные правила
- human.md — имя и язык собеседника
Только то, что нужно в каждом ходу.
### `reference/` — справочное (по требованию)
- `core-rules.md` — правила поведения агента (критичные + общение + публикация).
- `lessons.md` — точка входа по урокам: как пользоваться, как добавить, оглавление.
- `lessons/` — уроки и справочники по темам. Файлы:
  - уроки: memory, technical, mods, yaml, git-local, git-github,
    project-skills, network;
  - справочники: communication-protocol, github-guide, hardware,
    secrets-guide, system-prompt-updates, versioning, windows-guide,
    word-formatting.
  Оглавление — в `lessons.md`. Перед работой над типовой задачей —
  открыть `lessons.md`, найти тему, прочитать соответствующий файл.
**Правила:**
- Один файл — одна тема.
- Новый урок — в `lessons/`, ссылка в оглавлении `lessons.md`.
- Урок, специфичный для проекта — в `projects/<name>/lessons.md`, не в `reference/`.
- Новый файл в `reference/` — добавь ссылку в `lessons.md` (если это урок)
  или упомяни в этом разделе (если справочник).
### projects/ — проекты
Файлы уровня projects/:
- PROJECTS.md — инструкции
- index.json — данные о проектах
- index.md — [[path]]-связи
- _template.json — шаблон нового проекта
Папка проекта projects/<name>/:
- config.md, notes.md, tasks.md — обязательно
- skills.md, glossary.md, lessons.md — опционально
Внутри проекта — только файлы, без подпапок.
### memory-design/ — конституция
Только architecture.md. Общие принципы, без процедур.
---
## Принципы
- Один файл — одна тема.
- У каждого домена — точка входа (core-rules.md, lessons.md, index.json).
- Файлы содержат version: 1.4 внутри `description` в frontmatter.
Отдельным полем version не хранится — харнес Letta пропускает
только `description`, `read_only`, `limit`.
- MemFS — git-репозиторий, изменения коммитятся.
---
## Соглашения
**CWD и проект.** При переключении на проект CWD диалога = physical_path проекта. Детали — в [[projects/PROJECTS.md]].
**Скиллы.** Agent-scoped — $MEMORY_DIR/skills/. Project-scoped — <physical_path>/.agents/skills/. Global-scoped — ~/.letta/skills/. Детали — в [[projects/PROJECTS.md]].
