import sqlite3
from dataclasses import dataclass
from logInfo import logger

@dataclass
class Location:
    latitude: float = None
    longitude: float = None
    size: int = None #1 - на 3-4 человека, 2 - на 5-6 человек, 3 - на 7-8 человек
    type: int = None #1 - преимущественно малогабарит, 2 - преимущественно крупногабарит
    user_id: int = None
    photo_id: str = None
    num_users: int = 0

@dataclass
class User:
    latitude: float = None
    longitude: float = None
    chat_id: int = None
    message_id: int = None

class loc_helper:
    def __init__(self, db_name="locations"):
        self.dbname = db_name
        self.conn = sqlite3.connect(self.dbname)
        self.cur = self.conn.cursor()
    
    async def setup(self):
        create_table = '''
            CREATE TABLE IF NOT EXISTS locations
                (loc_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                latitude FLOAT,
                longitude FLOAT,
                size INT,
                type INT,
                user_id INT,
                photo_id TEXT
                )
        '''
        self.conn.execute(create_table)
        self.conn.commit()

    
    async def insert(self, data:Location):
        radius = 0.00005**2
        latitude = data.latitude
        longitude = data.longitude
        condition = f'''
            (POWER(({latitude}-latitude),2) +
            POWER(({longitude}-longitude),2)) <=  
            {radius}
        '''

        find_similar_loc = f'''
            WITH t AS (
                SELECT  loc_id, 
                        latitude,
                        longitude,
                        size,
                        type,
                        user_id,
                        photo_id
                FROM locations
                WHERE {condition}
                LIMIT 1
            )
        '''
        is_empty = f'''
            SELECT EXISTS(
                SELECT 1
                FROM t
            ) 
        '''

        try:
            empty = self.cur.execute(find_similar_loc+is_empty).fetchone()[0]

            if empty == 0:
                ins_data = (data.latitude, data.longitude, data.size, data.type, data.user_id, data.photo_id)
                ins_command = 'INSERT INTO locations VALUES (NULL, ?, ?, ?, ?, ?, ?)'
                self.conn.execute(ins_command, ins_data)
                self.conn.commit()
                logger.info("Insertion of a new loc completed correctly")
            elif empty == 1:
                lat = str(data.latitude)
                long = str(data.longitude)
                replace = f'''
                    REPLACE INTO locations(
                        loc_id, 
                        latitude, 
                        longitude, 
                        size, 
                        type, 
                        user_id, 
                        photo_id)
                    SELECT 
                        loc_id, 
                        (latitude+{lat})*0.5, 
                        (longitude+{long})*0.5, 
                        size, 
                        type, 
                        user_id, 
                        photo_id
                    FROM t
                '''
                self.conn.execute(find_similar_loc+replace)
                self.conn.commit()
                logger.info("Locations were merged")
        except Exception as e:
            print('Exception in insert')
            print(e)


    async def get_nearby(self, latitude, longitude, page, skip_lines):
        radius = 0.01
        lat_max, lat_min = str(latitude+radius), str(latitude-radius)
        long_max, long_min = str(longitude+radius), str(longitude-radius)
        rows_to_skip = str((page - 1) * skip_lines)
        
        condition = f'''
            WHERE latitude >= {lat_min} 
                    AND latitude <= {lat_max} 
                    AND longitude >= {long_min} 
                    AND longitude <= {long_max}
            '''
        
        find_locations = f'''
            SELECT latitude, longitude, size, type, photo_id
            FROM locations
            {condition}
            ORDER BY size DESC
            LIMIT {rows_to_skip}, {skip_lines}
        '''

        count_lines = f'''
            SELECT COUNT(loc_id)
            FROM locations
            {condition}
        '''
        try:
            loc = self.cur.execute(find_locations).fetchall()
            num_pages = self.cur.execute(count_lines).fetchone()[0]
            return loc, num_pages
        except Exception as e:
            print('Exception in get_nearby')
            print(e)



db_loc = loc_helper('locations')
