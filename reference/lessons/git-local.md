---
description: "Lesson: local git — filter-repo on Windows with Cyrillic. version: 1.5"
---
# Урок: локальный git
## git filter-repo на Windows с кириллицей
Перезапись истории (смена автора во всех коммитах) через `git filter-repo` на Windows имеет несколько подводных камней:
1. **`--commit-callback` в PowerShell ломает кириллицу.** Строка приходит в Python как `????` вместо русского текста. Причина — разная кодировка между PowerShell и Python. Обход: писать отдельный Python-скрипт, в котором имя задано явной последовательностью UTF-8 байт (`b"\xd0\x9a\xd0\xb8..."`), и запускать его через `python script.py`.
2. **`git filter-repo` требует «свежего клона».** На обычном рабочем репозитории отказывается работать с сообщением `Refusing to destructively overwrite repo history since this does not look like a fresh clone`. Обход: флаг `--force`.
3. **Установка.** `pip install git-filter-repo` кладёт `.exe` в `C:\Users\<user>\AppData\Roaming\Python\Python3XX\Scripts`, которого нет в PATH. Обход: запускать через `python -m git_filter_repo` или временно добавить путь в `$env:Path`.
4. **filter-repo удаляет remote `origin`.** Это защита от случайного пуша. После перезаписи — восстановить: `git remote add origin <url>`.
5. **`--force-with-lease` после перезаписи падает со stale info.** Локальные ссылки на удалённую ветку обнулены. Обход: `git fetch origin` перед пушем, затем `--force-with-lease` отработает корректно.
6. **Файл callback лучше держать в пути без кириллицы** — например, в `C:\Users\<user>\`, а не в папке с русскими буквами в имени.
7. **`--replace-text` переписывает и служебные файлы.** Замены применяются ко всем файлам всей истории — включая файлы, где сами паттерны хранятся как данные (например, JSON с правилами обезличивания). Такие файлы «ломают сами себя». Если в репо есть такой служебный файл — перепись текстом не подходит, лучше сброс истории (orphan-коммит + force-push). Детали — в локальном справочнике `memory-design/repo.md` (в публичный слепок не входит).
Пример рабочего callback (Python):
    import git_filter_repo, sys
    name  = "Китаец Вася".encode("utf-8")
    email = b"agent-local-8a9f04e0@example.com"
    cb = f"""NEW_NAME = {name!r}
    NEW_EMAIL = {email!r}
    commit.author_name = NEW_NAME
    commit.author_email = NEW_EMAIL
    commit.committer_name = NEW_NAME
    commit.committer_email = NEW_EMAIL"""
    sys.argv = ["git-filter-repo", "--force", "--commit-callback", cb]
    git_filter_repo.main()

## git add с несуществующим путём не стейджит ничего
Если в `git add` передать хотя бы один несуществующий путь, команда падает с `fatal: pathspec '...' did not match any files` и **не добавляет ни один** файл (в том числе корректные). Коммит после этого может пройти пустым или частичным. Правило: после `git add` + `commit` всегда проверять `git status --short` и `git log --oneline -1`, а не предполагать, что всё застейджилось.

## Переводы строк LF/CRLF на Windows
- В репозитории файлы хранятся с LF (`git ls-files --eol <путь>` → `i/lf`), а рабочая копия на диске — CRLF. Причина — `core.autocrlf=true` (проверить: `git config --get core.autocrlf`). Так было в репо изначально, к правкам агента отношения не имеет.
- Предупреждения `LF will be replaced by CRLF` при `git add`/`commit` — косметика самого коммита: в индекс и в коммит уходит LF. Но сам факт, что рабочая копия живёт в CRLF, **не безобиден**: скрипты, читающие файлы с диска (например, конвейер обезличивания репозитория памяти), видят CRLF и дают ложные срабатывания — «файл изменён», хотя в индексе ничего не менялось.
- Лечится одним файлом `.gitattributes` в корне репо: `* text=auto eol=lf`. Тогда и репо, и рабочая копия живут в LF независимо от машины и от `core.autocrlf`, и предупреждения исчезают. Проверено в репозитории архитектуры памяти.
- Проверка: если у всех файлов `i/lf` — смешения переводов строк в репо нет; CRLF живёт только в рабочей копии.

## Проверка «синхронизация ничего не потеряла»
Перед merge/push в чужую (облачную) историю сверить изменения с её HEAD:
    git -C <repo> diff --name-status <sha-облачного-HEAD> HEAD   # что добавлено/удалено/изменено
    git -C <repo> diff <sha-облачного-HEAD> HEAD -- <файл>       # построчно: только обезличивание?
Удалённые файлы не исчезают: `git cat-file -e <sha>:<path>` подтверждает, что блоб лежит в истории. Пока пользователь не подтвердил, что потерь нет, бэкап-ветку не удалять.