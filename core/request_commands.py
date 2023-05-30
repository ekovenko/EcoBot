from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import InputMediaPhoto
from logInfo import logger
from telegram.ext import ContextTypes, ConversationHandler
import json
import numpy as np


from keyboard import (
    keyboard_ok,
    cancel_text
)

from support_functions import(
    send_info,
    create_buttons
)

from database import (
    db_loc,
    Location,
    User
)

from new_entry_commands import DataType


async def paginate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        req = json.loads(query.data)

        if req['Method'] == 'pagination':
            page = req['CurrentPage']
            entry_per_page = 1

            user_lat = context.user_data['current'].latitude
            user_long = context.user_data['current'].longitude

            data, num_pages = await db_loc.get_nearby(latitude=user_lat,
                                    longitude=user_long,
                                    page=page,
                                    skip_lines=entry_per_page)
            
            info, forward, backward, cancel = await create_buttons(
                                                page=page,
                                                num_pages=num_pages)

            if page == 1:
                keyboard_pages = InlineKeyboardMarkup([[info], [forward], [cancel]])
            elif page == num_pages:
                keyboard_pages = InlineKeyboardMarkup([[info], [backward], [cancel]])
            else:
                keyboard_pages = InlineKeyboardMarkup([[info], [forward], [backward], [cancel]])
            
            await send_info(
                    data=data[0], 
                    user_lat=user_lat,
                    user_long=user_long,
                    update=update,
                    context=context,
                    keyboard=keyboard_pages,
                    query=query
                    )
            
        elif req['Method'] == 'cancel':
            await query.delete_message() 
            msg = context.user_data['current'].intro_message
            await msg.delete()
            await query.from_user.send_message('Увидимся!', reply_markup=keyboard_ok)
            return DataType.END            

    except Exception as e:
        print('Exception in paginate')
        print(e)
        logger.info(e)


async def show_nearby(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        if update.message.text == cancel_text:
            await update.message.reply_text('Приходи, когда будет, что показать...',
                                            reply_markup=keyboard_ok)
            return DataType.END
        logger.info("User %s requested nearby locations", user.id)
        
        user_location = update.message.location
               
        context.user_data['current'] = User()
        context.user_data['current'].latitude = user_location.latitude
        context.user_data['current'].longitude = user_location.longitude
        context.user_data['current'].chat_id = update.message.chat_id
        
        msg = await update.message.reply_text(
                'Показываю, что есть поблизости:',
                reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['current'].intro_message = msg
        
        init_page = 1
        entry_per_page = 1

        data, num_pages = await db_loc.get_nearby(latitude=user_location.latitude,
                                   longitude=user_location.longitude,
                                   page=init_page,
                                   skip_lines=entry_per_page)

        info, forward, _, cancel = await create_buttons(
                                        page=init_page,
                                        num_pages=num_pages
                                        )

        keyboard_pages = InlineKeyboardMarkup([[info], [forward], [cancel]])
        
        await send_info(
                    data=data[0], 
                    user_lat=user_location.latitude,
                    user_long=user_location.longitude,
                    keyboard=keyboard_pages,
                    update=update,
                    context=context
                    )
    except Exception as e:
        print('Exception in show_nearby')
        print(e)
        logger.info(e)

