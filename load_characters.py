# Загрузка персонажей Star Wars из API в базу данных


import asyncio
import aiohttp
import aiosqlite

BASE_URL = "https://www.swapi.tech/api/people"
DB_PATH = "starwars.db"
# таймаут в секундах — если API не ответил, не ждём вечно
REQUEST_TIMEOUT = 60
# сколько раз повторить запрос страницы при таймауте
MAX_RETRIES = 3


# Достаём нужные поля из ответа API
def get_character_from_response(data):
    result = data.get("result")
    if result is None:
        return None
    
    props = result.get("properties")
    if props is None:
        return None
    
    # получаем id персонажа
    uid = result.get("uid")
    if uid is None:
        uid = "0"
    character_id = int(uid)
    
    # достаём каждое поле, если нет — пустая строка
    name = props.get("name")
    if name is None:
        name = ""
    
    birth_year = props.get("birth_year")
    if birth_year is None:
        birth_year = ""
    
    eye_color = props.get("eye_color")
    if eye_color is None:
        eye_color = ""
    
    gender = props.get("gender")
    if gender is None:
        gender = ""
    
    hair_color = props.get("hair_color")
    if hair_color is None:
        hair_color = ""
    
    homeworld = props.get("homeworld")
    if homeworld is None:
        homeworld = ""
    
    mass = props.get("mass")
    if mass is None:
        mass = ""
    
    skin_color = props.get("skin_color")
    if skin_color is None:
        skin_color = ""
    
    # собираем словарь как одну запись для базы
    character = {
        "id": character_id,
        "birth_year": birth_year,
        "eye_color": eye_color,
        "gender": gender,
        "hair_color": hair_color,
        "homeworld": homeworld,
        "mass": mass,
        "name": name,
        "skin_color": skin_color,
    }
    return character


# Скачиваем данные одного персонажа по ссылке
async def fetch_one_person(session, url):
    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with session.get(url, timeout=timeout) as response:
            if response.status == 200:
                data = await response.json()
                return get_character_from_response(data)
    except Exception:
        pass
    return None


# Получаем список всех персонажей (по страницам)
async def get_all_people_urls(session):
    people_list = []
    url = BASE_URL
    page = 1
    
    while url is not None:
        print("  Запрос страницы", page, "...")
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        data = None
        for attempt in range(MAX_RETRIES):
            try:
                async with session.get(url, timeout=timeout) as response:
                    if response.status != 200:
                        print("  Ошибка: сервер вернул код", response.status)
                        break
                    data = await response.json()
                break
            except asyncio.TimeoutError:
                if attempt < MAX_RETRIES - 1:
                    print("  Таймаут, повтор через 5 сек... (попытка", attempt + 2, "из", MAX_RETRIES, ")")
                    await asyncio.sleep(5)
                else:
                    print("  Не удалось загрузить страницу после", MAX_RETRIES, "попыток.")
                    return people_list
        
        if data is None:
            break
        
        results = data.get("results", [])
        for person in results:
            people_list.append(person)
        print("  Получено записей на странице:", len(results))
        
        url = data.get("next")
        page = page + 1
    
    return people_list


# Загружаем данные всех персонажей асинхронно
async def load_all_characters(session, people_list):
    # создаём задачи для каждого персонажа
    tasks = []
    for person in people_list:
        person_url = person["url"]
        task = fetch_one_person(session, person_url)
        tasks.append(task)
    
    # ждём, пока все запросы выполнятся
    results = await asyncio.gather(*tasks)
    
    # собираем только тех, кого удалось загрузить
    characters = []
    for one_result in results:
        if one_result is not None:
            characters.append(one_result)
    
    return characters


# Сохраняем персонажей в базу данных
async def save_to_db(characters):
    db = await aiosqlite.connect(DB_PATH)
    
    # очищаем таблицу перед загрузкой
    await db.execute("DELETE FROM characters")
    await db.commit()
    
    # вставляем каждого персонажа
    for char in characters:
        await db.execute(
            """INSERT INTO characters 
            (id, birth_year, eye_color, gender, hair_color, homeworld, mass, name, skin_color) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                char["id"],
                char["birth_year"],
                char["eye_color"],
                char["gender"],
                char["hair_color"],
                char["homeworld"],
                char["mass"],
                char["name"],
                char["skin_color"],
            ),
        )
    
    await db.commit()
    await db.close()
    
    print("В базу загружено персонажей:", len(characters))


async def main():
    print("Загрузка списка персонажей...")
    
    try:
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # сначала получаем список всех персонажей
            people_list = await get_all_people_urls(session)
            print("Найдено записей в API:", len(people_list))
            
            if len(people_list) == 0:
                print("Не удалось получить список. Проверьте интернет и попробуйте снова.")
                return
            
            # потом загружаем детали по каждому
            print("Загрузка деталей каждого персонажа...")
            characters = await load_all_characters(session, people_list)
            print("Успешно загружено:", len(characters))
        
        # сохраняем в базу
        await save_to_db(characters)
        print("Готово.")
    except asyncio.TimeoutError:
        print("Ошибка: таймаут. Сервер не ответил за", REQUEST_TIMEOUT, "сек. Проверьте интернет.")
    except aiohttp.ClientError as e:
        print("Ошибка сети:", e)


if __name__ == "__main__":
    asyncio.run(main())
