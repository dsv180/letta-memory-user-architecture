---
description: "Lesson: local git — filter-repo on Windows with Cyrillic. version: 1.4"
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