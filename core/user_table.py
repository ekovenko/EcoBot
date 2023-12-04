import sqlite3
import json
from logInfo import logger

from dataclass import (
    Location
)


class user_helper:
    def __init__(self):#, db_name='walle_db'):
        self.table_name = 'user'
        # self.conn = sqlite3.connect(db_name)
        # self.cur = self.conn.cursor()
    
    async def setup_users(self, db_name='walle_db'):
        create_table = f'''
            CREATE TABLE IF NOT EXISTS {self.table_name}
                (id INTEGER PRIMARY KEY, 
                 user_id INT,
                 loc_id INT
                )
        '''
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        cur.execute(create_table)
        conn.commit()
        conn.close()
        logger.info(f'''Table {self.table_name} was created''')

    async def add_new_loc(self, user_id, loc_id, db_name='walle_db'):
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        try:
            ins_command = f'''INSERT INTO {self.table_name} VALUES (NULL, ?, ?)'''
            cur.execute(ins_command, (user_id, loc_id))
            conn.commit()
            conn.close()
            logger.info("Insertion of a new loc" + str(loc_id) \
                                + "for User "+ str(user_id)\
                                + " completed correctly")
            return('Записали! Теперь эта локация появится в списке твоих локаций 💫')
        except Exception as e:
            conn.close()
            print('Exception in add_new_loc, user_table.py')
            print(e)
            logger.info('Exception in add_new_loc, user_table.py ' + e)
            return('Что-то пошло не так, уже разбираемся! 🚒')

    async def get_all_user_locs(self, user_id, db_name='walle_db'):
            get_locs = f'''WITH t AS (
                SELECT loc_id
                FROM {self.table_name}
                WHERE user_id == {user_id}
            )
            '''
            is_empty = f'''
            SELECT EXISTS(
                SELECT 1
                FROM t
            ) 
            '''
            count_lines = f'''
                SELECT COUNT(loc_id)
                FROM t
            '''
            conn = sqlite3.connect(db_name)
            cur = conn.cursor()
            try:
                empty = cur.execute(get_locs+is_empty).fetchone()[0]
                if empty == 0:
                    conn.close()
                    logger.info('No favourite locations found')
                    return None, None
                elif empty == 1:
                    get_locs_info = f'''
                        SELECT  locations.loc_id, 
                                latitude, 
                                longitude, 
                                size, 
                                type, 
                                photo_id, 
                                num_users
                        FROM locations
                        INNER JOIN t
                        ON locations.loc_id==t.loc_id
                    '''
                    locs = cur.execute(get_locs+get_locs_info).fetchall()
                    num_pages = cur.execute(get_locs+count_lines).fetchone()[0]
                    conn.close()
                    return locs, num_pages
            except Exception as e:
                conn.close()
                print('Exception in get_all_user_locs, user_table.py')
                print(e)
                logger.info('Exception in get_all_user_locs, user_table.py ' + e)

    async def delete_location(self, user_id, loc_id, db_name='walle_db'):
        delete = f'''
            DELETE FROM {self.table_name}
            WHERE loc_id=={loc_id} AND
                  user_id=={user_id}
        '''
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        try:
            cur.execute(delete)
            conn.commit()
            conn.close()
            logger.info(f'User {user_id} deleted location {loc_id} from his/her favs')
            return('Этой локации больше не будет в списке твоих локаций 💫')
        except Exception as e:
            conn.close()
            print('Exception in delete, user_table.py')
            print(e)
            logger.info('Exception in delete, user_table.py ' + e)
            return('Что-то пошло не так, уже разбираемся! 🚒')



table_user = user_helper()
