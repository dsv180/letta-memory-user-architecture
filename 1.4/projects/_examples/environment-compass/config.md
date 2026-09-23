---
description: "Environment Compass — конфигурация: пути, git, техдетали. version: 1.4"
---
# Конфигурация: Environment Compass

Публичный проект-пример: он показывает, как выглядит описание реального проекта.

## Пути
- **physical_path:** `C:\Git-projects\environment-compass`
- **MemFS:** `projects/_examples/environment-compass/`

## Репозиторий
- **GitHub:** https://github.com/dsv180/environment-compass
- **Версия:** v0.1.1
- **Локальный git:** да (origin → GitHub)

## Технические детали
- **Происхождение:** community-мод из Letta Mod Challenge, адаптирован под Windows
- **Безопасность:** read-only, нет сетевых вызовов, нет записи на диск
- **Совместимость:** Desktop macOS, Desktop Windows
- **Установка:** `letta install .` → `/reload`

## Патч v0.1.1
- `resolveMemoryDir` — проверяет локальный и облачный пути MemFS
- `execFile` .cmd/.bat — на Windows обёртывает через `cmd /c`
