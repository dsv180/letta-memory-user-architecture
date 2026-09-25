---
description: "Environment Compass — конфигурация: пути, git, техдетали. version: 1.5"
---

# Конфигурация: Environment Compass

## Пути
- **physical_path:** `<диск пользователя>\Git-projects\environment-compass`
- **MemFS:** `projects/environment-compass/`

## Репозиторий
- **GitHub:** https://github.com/<логин GitHub>/environment-compass
- **Версия:** v0.1.1 (релиз 02.09.2026)
- **Локальный git:** да (origin → GitHub)

## Структура на диске
```
physical_path/
├── project/           ← код мода (index.ts и файлы мода)
├── .temp/
├── output/
└── input/
```

## Технические детали
- **Происхождение:** community-мод из Letta Mod Challenge, адаптирован под Windows
- **Безопасность:** read-only, нет сетевых вызовов, нет записи на диск
- **Совместимость:** Desktop macOS, Desktop Windows
- **Установка:** `letta install .` → `/reload`

## Патч v0.1.1
- `resolveMemoryDir` — проверяет локальный и облачный пути MemFS
- `execFile` .cmd/.bat — на Windows обёртывает через `cmd /c`
