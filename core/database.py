import sqlite3
import asyncio
from dataclasses import dataclass


@dataclass
class Entry:
    latitude: float = None
    longitude: float = None
    user_id: int = None
    photo_id: str = None

class db_helper:
    def __init__(self, db_name="locations"):
        self.dbname = db_name
        self.conn = sqlite3.connect(self.dbname)
    
    def setup(self):
        create_table = '''
            CREATE TABLE IF NOT EXISTS locations
                (loc_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                latitude FLOAT,
                longitude FLOAT,
                user_id INT,
                photo_id TEXT
                )
        '''
        self.conn.execute(create_table)
        self.conn.commit()

    def insert(self, data: Entry):
        try:
            ins_data = (data.latitude, data.longitude, data.user_id, data.photo_id)
            ins_command = 'INSERT INTO locations VALUES (NULL, ?, ?, ?, ?)'
            self.conn.execute(ins_command, ins_data)
            self.conn.commit()
            print("Insertion completed correctly")
        except Exception as e:
            print(e)


    async def __async__setup(self):
        return await self.setup()

    async def __async__insert(self, data: Entry):
        return await self.insert(data)

db = db_helper('locations')
