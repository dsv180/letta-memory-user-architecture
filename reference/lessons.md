---
description: "Lessons entry point — instructions and index. version: 1.6"
---
# Уроки
Уроки — правила поведения и техническое знание, извлечённое из опыта.
Применяются, чтобы не повторять ошибок.

## Как пользоваться уроками
Перед работой над типовой задачей — открой этот файл, найди тему
в оглавлении, прочитай соответствующий файл в `lessons/`.
Не читай всю папку сразу.

## Как добавить новый урок
1. Определи тему.
2. Если тема уже есть в оглавлении — допиши в соответствующий файл.
3. Если темы ещё нет — создай файл `lessons/<тема>.md`
   с frontmatter: description в кавычках, version внутри description:
   `description: "Урок: <тема>. version: 1.6"`, и заголовком `# Урок: <тема>`.
4. Добавь `[[path]]`-ссылку в оглавление ниже.
5. Если урок специфичен для проекта — пиши в `project/<name>/project-rules/`,
   а не в `lessons/`.
Критерий: если урок повторится в другом проекте — он общий. Если только
здесь — проектный.

**Уроки — живой слой** (позиция пользователя, 26.09.2026): их положено переписывать
и совершенствовать. Существующий урок дополнять и уточнять, а не обходить
стороной; новые факты и источник — прямо в него.

## Уроки
- [[lessons/memory.md]] — память и агенты
- [[lessons/technical.md]] — технические специфические случаи
- [[lessons/yaml.md]] — YAML frontmatter
- [[lessons/git-local.md]] — локальный git, filter-repo, переименование папок, LF/CRLF, сверка с облачной историей
- [[lessons/project-skills.md]] — проектные скиллы
- [[lessons/project-work.md]] — работа с проектом: создание, проектная папка, копии и бэкапы
- [[lessons/network.md]] — сеть, DNS, сетевая безопасность
- [[lessons/letta-code-issues.md]] — оформление issues в letta-ai/letta-code

## Справочники
- [[lessons/communication-protocol.md]] — протокол общения, разбор длинных сообщений
- [[lessons/github-guide.md]] — gh CLI, авторизация, trade controls
- [[lessons/hardware.md]] — железо
- [[lessons/secrets-guide.md]] — работа с секретами
- [[lessons/system-prompt-updates.md]] — обновление system prompt после апдейта ЛД
- [[lessons/letta-desktop.md]] — изнанка ЛД: папка диалога, Desktop-проекты, граф памяти
- [[lessons/versioning.md]] — версионирование Letta
- [[lessons/windows-guide.md]] — команды Windows/PowerShell
- [[lessons/word-formatting.md]] — оформление Word
