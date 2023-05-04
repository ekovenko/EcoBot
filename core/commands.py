from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from logInfo import logger
from telegram.ext import ContextTypes, ConversationHandler
from uuid import uuid4
from enum import Enum
import asyncio

from database import (
    db,
    Entry
)

class DataType(Enum):
    PHOTO = 1
    LOCATION = 2
    SAVEDATA = 3

    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info('User name %s, id %s', user.first_name, user.id)
    await update.message.reply_text(
        'Привет! Пришли, пожалуйста, фотографию локации.',
        reply_markup = ReplyKeyboardRemove(),
    )
    return DataType.PHOTO

#reply keyboard remove убирает насовсем боковое меню с кнопочками команд

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("User %s canceled the conversation", user.id)
    await update.message.reply_text(
        'Приходи, когда будет, что показать...',
        reply_markup = ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    key = str(uuid4())
    context.user_data[key] = Entry()
    context.user_data[key].user_id = user.id
    photo_name = key + ".jpg"
    context.user_data[key].photo_id = photo_name
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive(photo_name)
    logger.info("User %s uploaded the photo", user.id)

    await update.message.reply_text(
        'Спасибо! Теперь я попрошу тебя прислать свои координаты.\n'
    )
    return DataType.LOCATION
    #а тут надо понять, что делать, если пользователь не в том месте,
    #где мусор, и просто хочет указать на карте


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_location = update.message.location

    key = list(context.user_data.keys())[0]
    context.user_data[key].latitude = user_location.latitude
    context.user_data[key].longitude = user_location.longitude

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
    print(context.user_data[key])

    db.setup()
    db.insert(context.user_data[key])
    
    return ConversationHandler.END

