import aiosqlite
import os
import logging

# Логги
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'db.db')

# Класс
class DataBase:
    # Поля
    DB_PATH = DB_PATH

    async def setup(self):
        try:
            async with aiosqlite.connect(self.DB_PATH) as db:
                logging.info("❔ Loading DataBase")
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS snippets(
                        id INTEGER PRIMARY KEY,
                        snippet TEXT,
                        hashteg TEXT
                                 )""")
                await db.commit()
                logging.info("✅ Sucessfull loading DateBase")
        except Exception as err:
            logging.critical(f"❌ Error loading DataBase, error: {err}")
        

    # Добавление сниппета
    async def add_snippet(self, snippet: str, hashteg: str) -> bool:
        try:
            async with aiosqlite.connect(self.DB_PATH) as db:
                logging.info("❔ Found a hashteg for add new")
                cursor = await db.execute('SELECT snippet FROM snippets WHERE hashteg = ?', (hashteg,))
                if await cursor.fetchone():
                    logging.info("❌ Snippet allready use")
                    return False
                else:
                    logging.info("❔ Create new snippet")
                    await db.execute("INSERT INTO snippets (snippet, hashteg) VALUES (?, ?)", (snippet, hashteg))
                    await db.commit()
                    logging.info("✅ Sucessfull create new snippet")
                    return True
        except Exception as err:
            logging.critical(f"❌ Error create new snippet, error: {err}")
            return False
    
    # Поиск сниппета
    async def search_snippet(self, hashteg: str) -> str:
        try:
            async with aiosqlite.connect(self.DB_PATH) as db:
                logging.info("❔ Search a snippet")
                cursor = await db.execute("SELECT snippet FROM snippets WHERE hashteg = ?", (hashteg,))
                snippet = await cursor.fetchone()
                if snippet:
                    logging.info("✅ Sucessfull search a snippet")
                    return snippet[0]
                else:
                    logging.info("❌ Not found snippet")
                    return "nf"
        except Exception as err:
            logging.critical(f"❌ Error search a snippet, error: {err}")
            return ""
    
    # Удаление сниппета
    async def remove_snippet(self, hashteg: str) -> bool:
        try:
            async with aiosqlite.connect(self.DB_PATH) as db:
                logging.info("❔ Found hashteg for remove")
                cursor = await db.execute("SELECT snippet FROM snippets WHERE hashteg = ?", (hashteg,))
                if await cursor.fetchone():
                    logging.info("❔ Remove snippet")
                    await db.execute("DELETE FROM snippets WHERE hashteg = ?", (hashteg,))
                    await db.commit()
                    logging.info("✅ Sucessfull remove snippet")
                    return True
                else: 
                    logging.info("❌ Error found hashteg")
                    return False
        except Exception as err:
            logging.critical(f"❌ Error remove snippet, error: {err}")
            return False

    # Получить все хештеги
    async def get_all_hashtegs(self):
        try:
            async with aiosqlite.connect(self.DB_PATH) as db:
                logging.info("❔ Get all hashtegs")
                cursor = await db.execute("SELECT hashteg FROM snippets")
                hashtegs = await cursor.fetchall()
                logging.info("✅ Sucessfull get all hashtegs")
                return hashtegs
        except Exception as err:
            logging.critical(f"❌ Error get all hashtegs, error: {err}")
            return [[]]


# Глобальный экземпляр класса 
db = DataBase()

# async def test(): 
#     db = DataBase("db.db")
#     await db.setup()
#     await db.add_snippet("testing", "#test") 
#     await db.add_snippet("testing213123", "#test1") 
#     await db.add_snippet("test11111", "#test2")
#     await db.add_snippet("test11111", "#test24")
#     asd = await db.get_all_hashtegs()
#     print(asd[3][0])
#     t1 = await db.search_snippet("#test1")
#     print(t1)
#     t2 = await db.search_snippet("pisa")
#     print(t2)
#     await db.remove_snippet("#test1")
#     await db.remove_snippet("#asd")
#     t3 = await db.search_snippet("#test1")
#     print(t3)
    

# import asyncio
# if __name__ == "__main__":
#     asyncio.run(test())