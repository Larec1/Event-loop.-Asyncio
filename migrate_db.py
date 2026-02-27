# Скрипт миграции базы данных
# Создаёт таблицу для персонажей Star Wars

import asyncio
import aiosqlite

# путь к файлу базы данных
DB_PATH = "starwars.db"


async def migrate():
    # подключаемся к базе
    db = await aiosqlite.connect(DB_PATH)
    
    # создаём таблицу с нужными полями
    await db.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY,
            birth_year TEXT,
            eye_color TEXT,
            gender TEXT,
            hair_color TEXT,
            homeworld TEXT,
            mass TEXT,
            name TEXT NOT NULL,
            skin_color TEXT,
            films TEXT,
            species TEXT,
            starships TEXT,
            vehicles TEXT
        )
    """)
    
    await db.commit()
    await db.close()
    
    print("Миграция выполнена: таблица characters создана.")


if __name__ == "__main__":
    asyncio.run(migrate())
