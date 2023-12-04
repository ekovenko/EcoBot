from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, Bot
from logInfo import logger
from telegram.ext import ContextTypes, ConversationHandler
from uuid import uuid4


from keyboard import (
    keyboard_welcome, add_new, cancel_text, nearby, user_loc,
    keyboard_size, size1, size2, size3,
    keyboard_type, type1, type2,
    keyboard_ok, 
    keyboard_yes_no, yes, no,
    keyboard_location,
    keyboard_cancel
)

from support_functions import (
    end_session
)

from loc_table import (
    table_loc
)

from user_table import (
    table_user
)

from dataclass import (
    Location,
    User,
    DataType
)

from request_commands import (
    show_fav_loc,
    show_nearby
)

BOT_TOKEN = '6020419408:AAGqPVnOV3iZLZi2Ew2xsSUL88v10X2jAbI'
bot = Bot(token=BOT_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    await table_loc.setup_locations()
    await table_user.setup_users() 
    user = update.message.from_user
    context.user_data["info"] = Location()

    logger.info('User name %s, id %s started the conversation', user.first_name, user.id)
    await update.message.reply_text(
        'Привет, начнем?',
        reply_markup = keyboard_welcome
    )
    return DataType.BEGIN

async def begin_sharing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user = update.message.from_user
    reply = update.message.text
    context.user_data['current'] = User()
    context.user_data['current'].chat_id = update.message.chat_id
    context.user_data['current'].user_id = update.message.from_user.id

    try:
        if reply == add_new:
            logger.info('User name %s, id %s started sharing', user.first_name, user.id)
            await update.message.reply_text(
                'Пришли, пожалуйста, фотографию локации.',
                reply_markup = keyboard_cancel
            )
            return DataType.PHOTO

        elif reply == nearby:
            await update.message.reply_text(
            'Для этого мне нужно знать, где ты сейчас находишься.',
            reply_markup=keyboard_location
            )
            return DataType.NEARBY
        elif reply == user_loc:
            result = await show_fav_loc(update=update, context=context)
            if result is None:
                await context.bot.send_message(
                chat_id = context.user_data['current'].chat_id,
                text = 'Пока что тут пусто ☁️',
                reply_markup=ReplyKeyboardRemove()
                )
                await context.bot.send_message(
                    chat_id = context.user_data['current'].chat_id,
                    text = 'Но ты всегда можешь самостоятельно добавить локацию'+\
                           'или посмотреть, что есть поблизости',
                    reply_markup=keyboard_welcome
                )
            else:
                return DataType.SIGNED
        else:
            await update.message.reply_text(
            'Я тебя не очень понял. Пожалуйста, выбери из предложенного.',
            reply_markup = keyboard_welcome
    )
    except Exception as e:
        ex = 'Exception in begin_sharing: ' + e
        print(ex)
        logger.info(ex)


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        context.user_data["info"].photo_id = str(uuid4()) + '.jpg'
        print(context.user_data["info"].photo_id)
        photo_file = await update.message.photo[-1].get_file()
        await photo_file.download_to_drive(context.user_data["info"].photo_id)
        logger.info("User %s uploaded the photo", user.id)
        await update.message.reply_text(
            'Как думаешь, сколько людей понадобится?',
            reply_markup=keyboard_size
            )
        return DataType.SIZE
    
    except Exception as e:
        if update.message.text == cancel_text:
            await end_session(update=update, context=context,
                              user_id=user.id)
            return DataType.BEGIN
        else:
            await update.message.reply_text(
                'Я тебя не очень понял. Пришли, пожалуйста, фотографию локации.',
                reply_markup = keyboard_cancel
            )
            ex = 'Exception in photo: ' + e
            print(ex)
            logger.info(ex)
            return DataType.PHOTO



async def approx_size(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        user = update.message.from_user
        reply = update.message.text

        if reply == size1:
            context.user_data["info"].size = 1
        elif reply == size2:
            context.user_data["info"].size = 2
        elif reply == size3:
            context.user_data["info"].size = 3
        elif update.message.text == cancel_text:
            await end_session(update=update, context=context,
                              user_id=user.id)
            return DataType.BEGIN
        else:
            await update.message.reply_text(
            'Я тебя не очень понял. Как думаешь, сколько людей понадобится?',
            reply_markup=keyboard_size
            )
            return DataType.SIZE
        
        logger.info('User name %s, id %s defined the size', user.first_name, user.id)
        await update.message.reply_text(
            'Как думаешь, какого мусора больше -- крупного или мелкого?',
            reply_markup = keyboard_type,
        )
        return DataType.TYPE
    
    except Exception as e:
        ex = 'Exception in approx_size' + e
        print(ex)
        logger.info(ex)


async def garbage_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        reply = update.message.text
        if reply == type1:
            context.user_data["info"].type = 1
        elif reply == type2:
            context.user_data["info"].type = 2
        elif reply == cancel_text:
            await end_session(update=update, context=context,
                              user_id=user.id)
            return DataType.BEGIN
        else:
            await update.message.reply_text(
            'Я тебя не очень понял. Как думаешь, какой там мусор?',
            reply_markup=keyboard_type
            )
            return DataType.TYPE
        
        logger.info('User name %s, id %s defined the type', user.first_name, user.id)
        await update.message.reply_text(
            'Пожалуйста, пришли координаты локации. Если ты находишься от нее далеко,\
             это можно сделать, нажав "прикрепить" -> "поделиться геопозицией".',
            reply_markup=keyboard_location
        )
        return DataType.LOCATION
    
    except Exception as e:
        ex = 'Exception in garbage_type: ' + e
        print(ex)
        logger.info(ex)

async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    try:
        user_location = update.message.location
        context.user_data["info"].latitude = user_location.latitude
        context.user_data["info"].longitude = user_location.longitude

        logger.info(
            "Location of %s: %f / %f", 
            user.id,
            user_location.latitude,
            user_location.longitude
        )
        
        await update.message.reply_text(
            'Принято! Теперь волонтеры будут знать, '
            'где нужна их помощь.',
            reply_markup=keyboard_ok
        )
        await table_loc.insert(context.user_data["info"])
        await end_session(update=update, context=context,
                              user_id=user.id)
        return DataType.BEGIN
    except Exception as e: 
        if update.message.text == cancel_text:
            await end_session(update=update, context=context,
                              user_id=user.id)
            return DataType.BEGIN
        else:
            await update.message.reply_text(
                'Я тебя не очень понял. Пришли, пожалуйста, координаты локации.',
                reply_markup = keyboard_location
            )
            ex = 'Exception in location: ' + e
            print(ex)
            logger.info(ex)
            return DataType.LOCATION


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return DataType.BEGIN