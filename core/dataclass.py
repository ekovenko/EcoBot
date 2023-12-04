from dataclasses import dataclass
from enum import Enum

class DataType(Enum):
    BEGIN = 0
    TYPE = 1
    PHOTO = 2
    LOCATION = 3
    SIZE = 4
    END = 5
    NEARBY = 6
    SIGNED = 7


@dataclass
class Location:
    id: int = None
    latitude: float = None
    longitude: float = None
    size: int = None #1 - на 3-4 человека, 2 - на 5-6 человек, 3 - на 7-8 человек
    type: int = None #1 - преимущественно малогабарит, 2 - преимущественно крупногабарит
    photo_id: str = None
    num_users: int = 0

@dataclass
class User:
    latitude: float = None
    longitude: float = None
    chat_id: int = None
    message_id: int = None
    user_id: int = None
    cur_page: int = 1
    locations: tuple = None
    mode: str = None

    # async def fill(self, locations. keyboard, distance_info, message, mode):
    #     self.all_locations = locations
    #     self.keyboard = keyboard
    #     self.distance = distance_info
    #     self.intro_message = message
    #     self.mode = mode
