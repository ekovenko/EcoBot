import sqlite3
from logInfo import logger

from dataclass import (
    Location
)

class loc_helper:
    def __init__(self):#, db_name="walle_db"):
        self.table_name = 'locations'
        # self.conn = sqlite3.connect(db_name)
        # self.cur = self.conn.cursor()
    
    async def setup_locations(self, db_name="walle_db"):
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        table_name = 'locations'
        create_table = f'''
            CREATE TABLE IF NOT EXISTS {table_name}
                (loc_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                latitude FLOAT,
                longitude FLOAT,
                size INT,
                type INT,
                num_users INT,
                photo_id TEXT
                )
        '''
        cur.execute(create_table)
        conn.commit()
        conn.close()

    
    async def insert(self, data:Location, db_name="walle_db"):
        radius = 0.00005**2
        latitude = data.latitude
        longitude = data.longitude

        condition = f'''
            (POWER(({latitude}-latitude),2) +
            POWER(({longitude}-longitude),2)) <=  
            {radius}
        '''

        find_similar_loc = f'''
                SELECT  loc_id, 
                        latitude,
                        longitude,
                        size,
                        type,
                        num_users,
                        photo_id
                FROM {self.table_name}
                WHERE {condition}
                LIMIT 1
        '''
        is_empty = f'''WITH t AS 
            ({find_similar_loc})
            SELECT EXISTS(
                SELECT 1
                FROM t
            ) 
        '''
        
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        try:
            empty = cur.execute(is_empty).fetchone()[0]
            if empty == 0:
                ins_data = (data.latitude, data.longitude, data.size, data.type, data.num_users, data.photo_id)
                ins_command = f'''INSERT INTO {self.table_name} VALUES (NULL, ?, ?, ?, ?, ?, ?)'''
                cur.execute(ins_command, ins_data)
                conn.commit()
                conn.close()
                logger.info("Insertion of a new loc completed correctly")
            elif empty == 1:
                lat = str(data.latitude)
                long = str(data.longitude)
                replace = f'''WITH t AS 
                    ({find_similar_loc}) 
                    REPLACE INTO {self.table_name}(
                        loc_id, 
                        latitude, 
                        longitude, 
                        size, 
                        type, 
                        num_users, 
                        photo_id)
                    SELECT 
                        loc_id, 
                        (latitude+{lat})*0.5, 
                        (longitude+{long})*0.5, 
                        size, 
                        type, 
                        num_users, 
                        photo_id
                    FROM t
                '''
                cur.execute(replace)
                conn.commit()
                conn.close()
                logger.info("Locations were merged")
        except Exception as e:
            conn.close()
            print('Exception in insert, loc_table.py')
            print(e)
            logger.info('Exception in insert, loc_table.py ' + e)


    async def get_nearby(self, latitude, longitude, db_name='walle_db'):
        radius = 0.01
        lat_max, lat_min = str(latitude+radius), str(latitude-radius)
        long_max, long_min = str(longitude+radius), str(longitude-radius)
        
        condition = f'''
            WHERE latitude >= {lat_min} 
                AND latitude <= {lat_max} 
                AND longitude >= {long_min} 
                AND longitude <= {long_max}
            '''
        
        find_locations = f'''
            SELECT loc_id, 
                latitude, 
                longitude, 
                size, 
                type, 
                photo_id, 
                num_users
            FROM {self.table_name}
            {condition}
            ORDER BY size DESC
        '''

        is_empty = f'''WITH t AS
            ({find_locations})
            SELECT EXISTS(
                SELECT 1
                FROM t
            ) 
        '''

        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        try:
            empty = cur.execute(is_empty).fetchone()[0]
            if empty == 1:
                loc = cur.execute(find_locations).fetchall()
                conn.close()
                num_pages = len(loc)
                return loc, num_pages
            elif empty == 0:
                conn.close()
                logger.info('No favourite locations found')
                return None, None
        except Exception as e:
            conn.close()
            print('Exception in get_nearby, loc_table.py')
            print(e)
            logger.info('Exception in get_nearby, loc_table.py ' + e)

    async def add_user(self, loc_id, db_name='walle_db'):
        condition = f'''
            loc_id == {loc_id}
        '''
        find_loc = f'''
                SELECT  loc_id, 
                        latitude,
                        longitude,
                        size,
                        type,
                        num_users,
                        photo_id
                FROM {self.table_name}
                WHERE {condition}
                LIMIT 1
        '''       
        replace = f'''WITH t AS
                    ({find_loc})
                    REPLACE INTO {self.table_name}(
                        loc_id, 
                        latitude, 
                        longitude, 
                        size, 
                        type, 
                        num_users, 
                        photo_id)
                    SELECT 
                        loc_id, 
                        latitude, 
                        longitude, 
                        size, 
                        type, 
                        num_users+{1}, 
                        photo_id
                    FROM t
                '''

        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        try:
            cur.execute(replace)
            conn.commit()
            conn.close()
            logger.info("User applied for " + str(loc_id))
        except Exception as e:
            conn.close()
            print('Exception in add_user, loc_table.py')
            print(e)
            logger.info('Exception in add_user, loc_table.py ' + e)

    async def delete_user(self, loc_id, db_name='walle_db'):
        condition = f'''
            loc_id == {loc_id}
        '''
        find_loc = f'''
                SELECT  loc_id, 
                        latitude,
                        longitude,
                        size,
                        type,
                        num_users,
                        photo_id
                FROM {self.table_name}
                WHERE {condition}
                LIMIT 1
        '''       
        replace = f'''WITH t AS
                    ({find_loc})
                    REPLACE INTO {self.table_name}(
                        loc_id, 
                        latitude, 
                        longitude, 
                        size, 
                        type, 
                        num_users, 
                        photo_id)
                    SELECT 
                        loc_id, 
                        latitude, 
                        longitude, 
                        size, 
                        type, 
                        num_users-{1}, 
                        photo_id
                    FROM t
                '''
        
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()

        try:
            cur.execute(replace)
            conn.commit()
            conn.close()
            logger.info("User unsubscribed for location " + str(loc_id))
        except Exception as e:
            self.conn.close()
            print('Exception in delete_user, loc_table.py')
            print(e)
            logger.info('Exception in delete_user, loc_table.py ' + e)



table_loc = loc_helper()
