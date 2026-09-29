---
description: AITUNNEL — наш LLM-провайдер: base URL, ключ, карта документации. version: 1.7
---
# AITUNNEL — провайдер и его документация
Опорный файл по нашему LLM-провайдеру: что это, как подключён у нас, где и что искать в его документации.

## Что это
- Российский OpenAI-совместимый агрегатор: один ключ к GPT, Claude, Gemini, DeepSeek, Qwen, Kimi и др.; оплата в рублях, VPN не нужен.
- Base URL: `https://api.aitunnel.ru/v1`; зеркало, если провайдер блокирует основной хост (таймаут, Connection reset, Failed to fetch): `https://ru-api.aitunnel.ru/v1`.
- Формат ключа: `sk-aitunnel-…`. Формат запросов: OpenAI Chat Completions API.
- Каталог моделей и цены: https://aitunnel.ru/models

## Как подключён у нас
- Провайдер в Letta: `openai-compatible` → `base_url https://api.aitunnel.ru/v1`; ключ в `~/.letta/lc-local-backend/providers/auth.json` (значение — секрет, здесь не хранится).
- Модель диалогов: `openai-compatible/deepseek-v4.1-flash`.
- Детали, изнанка ЛД и известные проблемы (цикл повторов «Хм») — [[lessons/letta-desktop.md]].

## Карта документации
Источник — https://aitunnel.ru/llms.txt (машиночитаемый индекс для LLM, конвенция llmstxt.org). Слив одним файлом недоступен: `llms-full.txt` отдаёт 404, разделы тянутся по одной ссылке. При изменениях у провайдера карта обновляется перечитыванием llms.txt.

**Основы и работа API**
- [Введение](https://aitunnel.ru/docs.md) — base URL, зеркало, авторизация, первый запрос, примеры, модель auto.
- [Баланс и оплата](https://aitunnel.ru/docs/payments.md) — pay-as-you-go, Invoicebox от 5000 ₽, NOWPayments от 1500 ₽, авто-пополнение, возврат.
- [API-ключи](https://aitunnel.ru/docs/keys.md) — бюджет, автосброс в 00:00 МСК, срок, белый список моделей/IP, PII.
- [Список моделей](https://aitunnel.ru/docs/models.md) — публичный `GET /public/aitunnel/models` без ключа, цены в рублях, `price_tiers`, `usage.cost_rub`.
- [Последняя версия семейства](https://aitunnel.ru/docs/latest-models.md) — `~author/family-latest`.
- [Запасные модели (fallback)](https://aitunnel.ru/docs/fallback.md) — массив `models`, переключение при сбое.
- [Выбор провайдера](https://aitunnel.ru/docs/provider.md) — `provider.sort`: price / throughput / latency.
- [OpenRouter](https://aitunnel.ru/docs/openrouter.md) — доступ ко всему каталогу OpenRouter через ключ AITUNNEL.
- [Защита данных (PII)](https://aitunnel.ru/docs/pii.md) — маскировка/блокировка персональных данных.
- [Пресеты](https://aitunnel.ru/docs/presets.md) — имя вместо модели, failover до 5 моделей, override параметров.
- [Batch запросы](https://aitunnel.ru/docs/batch.md) — `POST /v1/batches`, скидка, ограничения (картинки/файлы только по URL).
- [Оптимизация сообщений](https://aitunnel.ru/docs/transforms.md) — context-compression через plugins.
- [Уровни обслуживания](https://aitunnel.ru/docs/service-tiers.md) — `service_tier`: flex / priority.
- [Кеширование промпта](https://aitunnel.ru/docs/caching.md) — скидка на повторяющийся префикс, `cache_control`, `session_id`.
- [Справочник API](https://aitunnel.ru/docs/api-reference.md) — схема chat/completions, запрос/ответ, usage.
- [Стриминг](https://aitunnel.ru/docs/streaming.md) — SSE-чанки, usage в последнем событии.
- [Лимиты](https://aitunnel.ru/docs/limits.md) — нет RPM со стороны AITUNNEL, 429 — лимит провайдера, файлы до 25 МБ.
- [Параметры](https://aitunnel.ru/docs/parameters.md) — temperature, top_p, max_tokens, tools, reasoning.
- [Ошибки и отладка](https://aitunnel.ru/docs/errors.md) — error.code/message, 401/402/429/504, зеркало.

**Модальности и сервисы**
- [Эмбеддинги](https://aitunnel.ru/docs/embeddings.md), [Модерация](https://aitunnel.ru/docs/moderation.md), [Ранжирование](https://aitunnel.ru/docs/rerank.md), [RAG](https://aitunnel.ru/docs/rag.md).
- [Картинки](https://aitunnel.ru/docs/images.md) (понимание + генерация + edits), [PDF](https://aitunnel.ru/docs/pdf.md), [Видео](https://aitunnel.ru/docs/videos.md) (понимание + генерация).
- [Аудио](https://aitunnel.ru/docs/audio.md), [Озвучка текста](https://aitunnel.ru/docs/text-to-speech.md), [Распознавание речи](https://aitunnel.ru/docs/speech-to-text.md).
- [Вызов инструментов](https://aitunnel.ru/docs/tool-calling.md), [Серверные инструменты](https://aitunnel.ru/docs/server-tools.md) (aitunnel:web_search), [Веб-поиск](https://aitunnel.ru/docs/web-search.md).
- [Структурированный вывод](https://aitunnel.ru/docs/structured-outputs.md), [Токены рассуждений](https://aitunnel.ru/docs/reasoning.md).

**Гайды по подключению агентов/IDE**
- [Claude Code](https://aitunnel.ru/docs/claude-code.md), [Claude Desktop](https://aitunnel.ru/docs/claude-desktop.md), [Codex CLI](https://aitunnel.ru/docs/codex-cli.md).
- [Cursor](https://aitunnel.ru/docs/cursor.md), [VS Code / Cline](https://aitunnel.ru/docs/vscode.md), [Xcode](https://aitunnel.ru/docs/xcode.md).
- [OpenCode](https://aitunnel.ru/docs/opencode.md), [Qwen Code](https://aitunnel.ru/docs/qwen-code.md), [Hermes Agent](https://aitunnel.ru/docs/hermes-agent.md), [OpenClaw](https://aitunnel.ru/docs/openclaw.md), [LangChain](https://aitunnel.ru/docs/langchain.md).

**Собственный API AITUNNEL** (`/v1/aitunnel`)
- [Обзор](https://aitunnel.ru/docs/api.md), [Аккаунт](https://aitunnel.ru/docs/api/me.md), [Баланс](https://aitunnel.ru/docs/api/balance.md), [Ключ](https://aitunnel.ru/docs/api/key.md), [Статистика](https://aitunnel.ru/docs/api/stats.md).

## Ресурсы и поддержка
- Каталог моделей и цены: https://aitunnel.ru/models
- API-ключи: https://aitunnel.ru/panel/keys
- Пополнение баланса: https://aitunnel.ru/panel/purchase
- Почта: support@aitunnel.ru; Telegram: https://t.me/aitunnelru