# tg-lead-collector-bot

Telegram-бот для сбора заявок: имя, телефон и комментарий. Подходит для лендингов,
рекламных кампаний и небольших услуг, где заявки удобно получать прямо в Telegram.

## Возможности

- Пошаговая форма на FSM: имя → телефон → комментарий.
- Валидация и нормализация российских номеров (`+7`, `8`, скобки, дефисы).
- Подтверждение заявки перед отправкой.
- Отправка структурированной заявки в личный чат или группу администратора.
- Команда `/cancel` и кнопка «Пропустить» для комментария.
- Простая защита от флуда на уровне middleware.
- Конфигурация через `.env`, токен хранится в `SecretStr`.

## Стек

- Python 3.11+
- [aiogram 3](https://docs.aiogram.dev/)
- `pydantic-settings`
- `uv` для управления зависимостями
- `ruff`, `mypy`, `pytest` для проверки качества

## Быстрый старт

```bash
git clone https://github.com/paramisdev/tg-lead-collector-bot.git
cd tg-lead-collector-bot
uv sync --locked
```

Создайте файл окружения:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Заполните `BOT_TOKEN` и `ADMIN_CHAT_ID`, затем запустите бота:

```bash
uv run python -m bot
```

## Переменные окружения

| Переменная | Обязательна | Описание |
| --- | --- | --- |
| `BOT_TOKEN` | да | Токен бота, полученный у [@BotFather](https://t.me/BotFather) |
| `ADMIN_CHAT_ID` | да | ID чата или группы для заявок. У групп ID отрицательный |

Чтобы узнать `ADMIN_CHAT_ID`, напишите боту и откройте:

```text
https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
```

Либо используйте @userinfobot. Для группы добавьте бота в чат и возьмите
отрицательный `chat.id` из ответа `getUpdates`.

## Как это работает

1. Пользователь нажимает «Оставить заявку».
2. Бот последовательно запрашивает имя, телефон и комментарий.
3. Номер проверяется и приводится к формату `+79991234567`.
4. Пользователь видит сводку и подтверждает отправку.
5. Заявка уходит администратору, диалог завершается.

## Структура проекта

```text
src/bot/
├── __main__.py      # точка входа: python -m bot
├── main.py          # Bot, Dispatcher, polling
├── config.py        # настройки из .env
├── handlers/        # роутеры и сценарии диалога
├── keyboards/       # inline-клавиатуры
├── callbacks/       # typed CallbackData
├── middlewares/     # throttling
├── services/        # бизнес-логика без aiogram
├── states/          # FSM-состояния
└── utils/           # валидаторы
tests/               # unit-тесты
```

## Проверки качества

```bash
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run mypy src/bot
uv run pytest -q
```

## Лицензия

Проект распространяется по лицензии MIT.
