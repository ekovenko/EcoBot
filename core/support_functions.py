
from telegram import Update
from telegram import InputMediaPhoto
from logInfo import logger
from telegram.ext import ContextTypes
import numpy as np


from keyboard import (
    button_cancel,
    button_info, button_backward, button_forward,
    sizes, types
)


async def create_buttons(page, num_pages):
    info = await button_info(page=page, num_pages=num_pages)
    forward = await button_forward(page=page)
    backward = await button_backward(page=page)
    cancel = await button_cancel()
    return info, forward, backward, cancel


async def send_info(data, user_lat, user_long, keyboard,
                            update: Update,
                            context: ContextTypes.DEFAULT_TYPE,
                            query=None):
    distance = int(np.sqrt((data[0]-float(user_lat))**2+(data[1]-float(user_long))**2)*1e5)
    location_info = f'<b>Примерное расстояние в метрах: </b> <i>{distance}</i>\n\n'\
                    f'<b>Сколько людей необходимо: </b><i>{sizes[data[2]]}</i>\n\n'\
                    f'<b>Какой мусор предстоит убирать: </b><i> {types[data[3]]}</i>'
    
    photo_path = 'C:\\Users\\Boris\\YandexDisk\\Kate\\Small Projects\\BelgradeGarbageCollector\\' +\
                    str(data[4])

    if query:
        photo = InputMediaPhoto(
                            open(photo_path, 'rb'),
                            caption=location_info,
                            parse_mode='HTML')
        msg = context.user_data['current'].first_item
        await msg.edit_media(
                            media=photo, 
                            reply_markup=keyboard)
    else:
        msg = await context.bot.send_photo(
                                    photo=open(photo_path, 'rb'),
                                    caption=location_info,
                                    parse_mode='HTML',
                                    chat_id=context.user_data['current'].chat_id, 
                                    reply_markup=keyboard
                                    )
        context.user_data['current'].first_item = msg
        
