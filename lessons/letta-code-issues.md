---
description: "Lesson: filing issues in letta-ai/letta-code — AI policy, required fields, links. version: 1.6"
---
# Урок: issues в letta-ai/letta-code

Letta Code живёт по строгой AI-политике: issue, не соответствующий шаблону, **автоматически закрывают и блокируют**; повторные нарушения → бан.

## Правила (открыть перед filing, не искать заново)
- AI-политика: https://github.com/letta-ai/letta-code/blob/main/AI_POLICY.md
- Contributing: https://github.com/letta-ai/letta-code/blob/main/CONTRIBUTING.md
- Шаблон бага: https://github.com/letta-ai/letta-code/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml

## Куда и что до подачи
- Только `letta-ai/letta-code`. `letta-ai/letta` — старый репозиторий-указатель (README отсылает за кодом в `letta-code`), issues там не ведутся (0 открытых, всё закрыто) — репорты туда бесполезны.
- Поискать существующие: `gh search issues --repo letta-ai/letta-code --state open '<слова>'`.
- Проблема должна воспроизводиться на **текущем релизе**. Для Desktop ориентир — последняя доступная Desktop-сборка (проверяется апдейтером), а не GitHub-релиз: сборка отстаёт от `letta-code` на 1–2 дня. Обновляюсь апдейтером Desktop, не через npm; версия = ProductVersion `Letta.exe` (= версия встроенного харнеса).

## Обязательные поля шаблона bug_report.yml
1. **AI Disclosure** — ровно одна опция: «entirely by a human» ИЛИ «with AI assistance and reviewed and edited by a human»; плюс чекбокс согласия с AI Policy.
2. **AI Tool(s) Used** — перечислить все инструменты (напр. `Letta Code`), либо `None`.
3. **Human Verification** — вставить дословно:
   `I have personally reproduced or verified this issue, reviewed its contents, and take responsibility for its accuracy.`
4. **Describe the bug** — что случилось и что ожидалось.
5. **Letta Code version** — из `letta --version` (в Desktop совпадает с версией сборки `Letta.exe`).
6. **Where did this happen?** — поверхность; мои баги про граф/память Desktop — это **Letta Code Desktop**.
7. **Operating system**.
8. **Steps to reproduce** — минимальное детерминированное воспроизведение.
9. Логи/скриншоты и Additional context — опционально.

## Подача через `gh issue create`
Форма на сайте не обязательна: авто-гвард (`contribution-guard.cjs`) парсит **тело** issue, а не форму. Значит `gh issue create` проходит, если тело содержит:
- ровно одну authorship-опцию из AI Disclosure;
- чекбокс согласия с AI Policy;
- непустую секцию `AI Tool(s) Used`;
- дословную фразу Human Verification.

Тело — ровно как в шаблоне: заголовки секций (`### ...`), строки чекбоксов `- [x] ...`, фраза верификации без правок. От себя ничего не добавлять.
Проверено 26.09.2026: issue, поданный так, остался `OPEN` без меток `invalid`/`spam`. После подачи всегда проверить состояние (`gh issue view <n> --json state,labels,comments`) — если гвард закрыл, переоформить через веб-форму.

## Дух политики
- Человек отвечает за точность: воспроизвести самому, проверить код, доки и существующие issues, убрать спекуляции и заполнитель.
- «Не заставлять мейнтейнеров валидировать сырой вывод модели».
- AI-медиа не принимаются — только текст и код.
- Есть авто-трекер устаревания встроенных скиллов: issue #4065 (в нём `initializing-memory` помечен `needs_human_review`).
