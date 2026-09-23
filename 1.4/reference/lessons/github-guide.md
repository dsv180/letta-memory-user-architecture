---
description: "GitHub CLI — install, auth, trade controls, releases, attribution. version: 1.4"
---
# GitHub-гайд

Справочный файл. Читай, когда нужно работать с GitHub: клонировать, пушить, создавать релизы, публиковать проекты.

## Установка gh CLI

Установлен 02.09.2026: `C:\Program Files\GitHub CLI\gh.exe`

Установка через winget (требует права администратора, UAC-запрос):
```powershell
winget install --id GitHub.cli --silent --accept-package-agreements --accept-source-agreements
```

## Авторизация

Авторизация через браузер (вход через Google SSO — аккаунт пользователя):
```powershell
gh auth login --web
```
После ввода одноразового кода — браузер откроет страницу входа через Google.

## git config

Конфиг локального git настраивается через `gh auth setup-git`.
Проверить: `git config --local --get user.name`, `git config --local --get user.email`.

## Ограничения

**Trade controls restriction** (02.09.2026) — аккаунт пользователя не может создавать репозитории через API или `gh repo create`. Только через веб-интерфейс: `github.com/new`.

Публиковать можно только публичные репозитории (приватные заблокированы региональной политикой).

## Работа с прокси

`gh` написан на Go и использует `ALL_PROXY`, а не `http_proxy`/`https_proxy`. При проблемах с подключением:
```powershell
$env:ALL_PROXY="http://proxy:port"
```

## Релизы

Для публикации новой версии:
```powershell
git tag v<version>
git push origin v<version>
gh release create v<version> --title "v<version>" --notes "..."

## Атрибуция публичных проектов

При публикации на GitHub обязательно указывать происхождение кода (ссылку на оригинал, автора, лицензию). Без атрибуции — серьёзный зашквар.

Весь публичный контент (README, описания) — только на русском, если пользователь не сказал иначе.
