from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from logInfo import logger
from telegram.ext import ContextTypes, ConversationHandler
from uuid import uuid4
from enum import Enum


from keyboard import (
    keyboard_welcome,
    keyboard_share_geo,
    keyboard_cancel,
)

from database import (
    db,
    Entry
)

class DataType(Enum):
    BEGIN = 0
    PHOTO = 1
    LOCATION = 2
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info('User name %s, id %s started the conversation', user.first_name, user.id)
    await update.message.reply_text(
        'Привет, начнем?',
        reply_markup = keyboard_welcome,
    )
    return DataType.BEGIN


async def start_sharing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.message.from_user
    logger.info('User name %s, id %s started sharing', user.first_name, user.id)
    await query.message.text(
        'Пришли, пожалуйста, фотографию локации.'
    )
    return DataType.PHOTO



async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    

    context.user_data["info"] = Entry()
    context.user_data["info"].user_id = user.id
    context.user_data["info"].photo_id = str(uuid4()) + '.jpg'

    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive(context.user_data["info"].photo_id)
    logger.info("User %s uploaded the photo", user.id)

    await update.message.reply_text(
        'Спасибо! Теперь я попрошу тебя прислать свои координаты.'
    )
    return DataType.LOCATION


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
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
        'где нужна их помощь.'
    )

    await db.setup()
    await db.insert(context.user_data["info"])
    
    return ConversationHandler.END

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Ето хелп'
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.message.from_user
    logger.info("User %s canceled the conversation", user.id)
    await query.message.text(
        'Приходи, когда будет, что показать...'
    )
    return ConversationHandler.END