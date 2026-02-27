# Домашнее задание: Event loop / Asyncio

Я беру персонажей из публичного API `https://www.swapi.tech/` (Star Wars),
асинхронно забираю данные и складываю их в локальную БД SQLite.

В проекте два основных скрипта:
- `migrate_db.py` — создаёт таблицу `characters` в файле базы `starwars.db`.
- `load_characters.py` — ходит в API, вытаскивает всех персонажей и записывает их в таблицу.

## Какие данные сохраняются

В таблицу `characters` попадают следующие поля:
- `id` — ID персонажа;
- `name` — имя;
- `birth_year` — год рождения;
- `eye_color` — цвет глаз;
- `gender` — пол;
- `hair_color` — цвет волос;
- `skin_color` — цвет кожи;
- `mass` — масса;
- `homeworld` — 
- `films` — фильмы 
- `species` — виды 
- `starships` — корабли 
- `vehicles` — транспорт 

## Как это работает (если по‑простому)

- Я использую `asyncio` и `aiohttp`, чтобы отправлять запросы к API не по одному, а асинхронно.
- Чтобы не завалить API, ввёл ограничение по количеству одновременных запросов через
  `asyncio.Semaphore` (у меня стоит `MAX_CONCURRENT_REQUESTS = 5`).
загрузилось.

## Требования

- Python 3.10+
- Виртуальное окружение 

## Установка зависимостей

python -m venv .venv
source .venv/bin/activate  
pip install -r requirements.txt

## Шаг 1. Подготовить базу

Создаю файл базы и таблицу `characters`:
python migrate_db.py
## Шаг 2. Загрузить персонажей из API
python load_characters.py
