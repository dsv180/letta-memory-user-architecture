# Letta Memory Architecture
Репозиторий описывает архитектуру памяти агентов на Letta Code — структуру, правила, уроки.
## Актуальная версия
**1.4** — актуальная версия архитектуры. Папки старых версий удалены, история сохранена в git.
## Структура 1.4
    1.4/
    ├── memory-design/     — конституция памяти
    ├── projects/          — проекты: инструкции, данные, шаблон
    ├── reference/         — правила поведения, уроки, справочники
    ├── system/            — ядро: persona.md, human.md
    └── system-prompt/     — компактный system prompt
## Что внутри
**memory-design/architecture.md** — устройство памяти: слои, файлы, правила, соглашения.
**reference/core-rules.md** — правила поведения агента.
**reference/lessons.md** — точка входа по урокам. Сами уроки и справочники — в reference/lessons/.
**projects/** — инструкции (PROJECTS.md), данные (index.json), связи (index.md), шаблон нового проекта (_template.json). Внутри каждого проекта — фиксированный набор файлов. Примеры проектов — в **projects/_examples/** (заглушка example-project и публичный environment-compass).
**system/persona.md** — личность агента. **system/human.md** — данные пользователя.
**system-prompt/system-prompt.txt** — компактный system prompt, применяется к агенту через update-agent-settings.ts.
## Принципы
- Один файл — одна тема.
- Файлы памяти содержат frontmatter: description обязателен, version — внутри description.
- Проекты — изолированные контексты, свои инструкции, свои скиллы.
## Инструменты (tools/)
Конвейер обезличивания слепка перед публикацией. Правила — двухслойные:

| Слой | Файл | Что содержит | В git |
|---|---|---|---|
| Общий | `tools/anonymize.rules.json` | переменные окружения, структурные шаблоны путей, политика `projects/` | да |
| Локальный | `tools/anonymize.local.json` | имена, организации, специфичные диски | нет (`.gitignore`) |

Образец локального слоя — `tools/anonymize.local.example.json`.

| Инструмент | Назначение |
|---|---|
| `tools/anonymize.py` | обезличивает слепок: пути этой машины → канон Letta (`~`, `$MEMORY_DIR`, `$LETTA_LOCAL_BACKEND_DIR`, `$LETTA_TRANSCRIPT_ROOT`), затем локальные замены. `--dry-run` показывает план |
| `tools/check-anonymized.py` | гейт: `exit 1`, если найден персональный паттерн |
| `tools/selftest.py` | самотест конвейера, включая переносимость на другую машину |
| `tools/new-project.py` | генератор каркаса проекта из `tools/templates/project/` |
| `tools/hooks/pre-push` | гейт перед push (включается: `git config core.hooksPath tools/hooks`) |

Пути в правилах не зашиты: они берутся из окружения машины. Поэтому конвейер работает и на Windows, и на Linux, и на другой машине — достаточно заполнить свой `anonymize.local.json`.

## Применение
Как применить версию к своей памяти, не потеряв свои проекты — см. [MIGRATION.md](MIGRATION.md).
