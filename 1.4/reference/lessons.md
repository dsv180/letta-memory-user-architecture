---
description: "Lessons entry point — instructions and index. version: 1.4"
---
# Уроки
Уроки — правила поведения и техническое знание, извлечённое из опыта.
Применяются, чтобы не повторять ошибок.

## Как пользоваться уроками
Перед работой над типовой задачей — открой этот файл, найди тему
в оглавлении, прочитай соответствующий файл в `reference/lessons/`.
Не читай всю папку сразу.

## Как добавить новый урок
1. Определи тему.
2. Если тема уже есть в оглавлении — допиши в соответствующий файл.
3. Если темы ещё нет — создай файл `reference/lessons/<тема>.md`
   с frontmatter: description в кавычках, version внутри description:
   `description: "Урок: <тема>. version: 1.4"`, и заголовком `# Урок: <тема>`.
4. Добавь `[[path]]`-ссылку в оглавление ниже.
5. Если урок специфичен для проекта — пиши в `projects/<name>/lessons.md`,
   а не в `reference/lessons/`.
Критерий: если урок повторится в другом проекте — он общий. Если только
здесь — проектный.

## Уроки
- [[reference/lessons/memory.md]] — память и агенты
- [[reference/lessons/technical.md]] — технические специфические случаи
- [[reference/lessons/mods.md]] — моды и инструменты
- [[reference/lessons/yaml.md]] — YAML frontmatter
- [[reference/lessons/git-local.md]] — локальный git, filter-repo, LF/CRLF, сверка с облачной историей
- [[reference/lessons/git-github.md]] — облачный GitHub, клонирование
- [[reference/lessons/project-skills.md]] — проектные скиллы
- [[reference/lessons/network.md]] — сеть, DNS, сетевая безопасность

## Справочники
- [[reference/lessons/communication-protocol.md]] — протокол общения, разбор длинных сообщений
- [[reference/lessons/github-guide.md]] — gh CLI, авторизация, trade controls
- [[reference/lessons/hardware.md]] — железо
- [[reference/lessons/secrets-guide.md]] — работа с секретами
- [[reference/lessons/system-prompt-updates.md]] — обновление system prompt после апдейта ЛД
- [[reference/lessons/versioning.md]] — версионирование Letta
- [[reference/lessons/windows-guide.md]] — команды Windows/PowerShell
- [[reference/lessons/word-formatting.md]] — оформление Word
