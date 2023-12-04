
from telegram import Update, User
from telegram import InputMediaPhoto
from logInfo import logger
from telegram.ext import ContextTypes
import numpy as np
from telegram import InlineKeyboardMarkup
from typing import NamedTuple, Optional, Union

from keyboard import (
    button_cancel,
    button_backward, 
    button_forward, 
    button_apply,
    button_delete,
    keyboard_welcome,
    sizes, 
    types,
    InlineKeyboardButton
)

from dataclass import (
    Location
)

async def create_buttons_loc(page) :
    forward=await button_forward(page=page)
    backward=await button_backward(page=page)
    cancel=await button_cancel()
    apply=await button_apply(page=page)
    return forward, backward, cancel, apply
    


async def create_buttons_fav_loc(page):
    forward = await button_forward(page=page)
    backward = await button_backward(page=page)
    cancel = await button_cancel()
    delete = await button_delete(page=page)
    return forward, backward, cancel, delete


async def loc_kbrd(page, num_pages):
    forward, backward, cancel, apply = await create_buttons_loc(
                                                page=page)
    if page == 1:
        if num_pages == 1:
            keyboard_pages = InlineKeyboardMarkup([[apply], [cancel]])
        else:
            keyboard_pages = InlineKeyboardMarkup([[forward], [apply], [cancel]])
    elif page == num_pages:
        keyboard_pages = InlineKeyboardMarkup([[backward], [apply], [cancel]])
    else:
        keyboard_pages = InlineKeyboardMarkup([[forward], [backward], [apply], [cancel]])
    
    return keyboard_pages


async def fav_loc_kbrd(page, num_pages):
    forward, backward, cancel, delete = await create_buttons_fav_loc(
                                                page=page)
    if page == 1:
        if num_pages == 1:
            keyboard_pages = InlineKeyboardMarkup([[delete], [cancel]])
        else:
            keyboard_pages = InlineKeyboardMarkup([[forward], [delete], [cancel]])
    elif page == num_pages:
        keyboard_pages = InlineKeyboardMarkup([[backward], [delete], [cancel]])
    else:
        keyboard_pages = InlineKeyboardMarkup([[forward], [backward], [delete], [cancel]])
    
    return keyboard_pages


async def loc_from_data(data):
    return Location(*data)

async def fill_current_data(locations, keyboard, message, mode, context, distance_info=''):
    context.user_data['current'].all_locations = locations
    context.user_data['current'].keyboard = keyboard
    context.user_data['current'].distance = distance_info
    context.user_data['current'].intro_message = message
    context.user_data['current'].mode = mode

async def send_info(data, keyboard, page,
                    update: Update,
                    context: ContextTypes.DEFAULT_TYPE,
                    distance_info='',
                    query=None):
    loc = data[page-1]
    num_pages = len(data)
    url = f"https://www.google.com/maps?q={loc.latitude},{loc.longitude}"
    text = f"{loc.latitude}, {loc.longitude}"
    location_info = f'<b>Координаты локации: </b>'\
                    f'<a href="{url}"> {text}</a>\n'\
                    f'<b>Примерное расстояние в метрах: </b><i>{f"{distance_info}"}</i>\n'\
                    f'<b>Сколько людей необходимо: </b><i>{sizes[loc.size]}</i>\n\n'\
                    f'<b>Какой мусор предстоит убирать: </b><i> {types[loc.type]}</i>\n\n'\
                    f'<b>Сколько человек присоединилось: </b><i> {loc.num_users}</i>\n\n'\
                    f"{page:>25} / {num_pages}"
    photo_path = 'C:\\Users\\ekove\\YandexDisk\\Kate\\Small Projects\\BelgradeGarbageCollector\\' +\
                    str(loc.photo_id)
    try:
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
    except Exception as e:
        print('Exception in send_info, support_functions.py')
        print(e)
        logger.info(e)

async def end_session(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                      user_id: Optional[int] = None, 
                      query_from_user: Optional[User] = None):
    try:
        if query_from_user is not None:
            await query_from_user.send_message('Ну что, начнем?', reply_markup=keyboard_welcome)
        else: 
            await update.message.reply_text(
                'Приходи ещё!'
            )
            await update.message.reply_text(
                'Ну что, начнем?',
                reply_markup=keyboard_welcome
            )

        logger.info("User %s canceled the conversation", user_id)
    except Exception as e:
        print('Exception in end_sessions, support_functions.py')
        print(e)
        logger.info(e)
    
    # return DataType.BEGIN
        
