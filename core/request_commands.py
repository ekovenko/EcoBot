from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import InputMediaPhoto
from logInfo import logger
from telegram.ext import ContextTypes, ConversationHandler
import json
import numpy as np


from keyboard import (
    keyboard_ok,
    cancel_text,
    keyboard_welcome
)

from support_functions import(
    send_info,
    create_buttons_loc,
    create_buttons_fav_loc,
    loc_kbrd,
    fav_loc_kbrd,
    loc_from_data,
    fill_current_data,
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
    User
)

from new_entry_commands import DataType

async def show_nearby(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.message.from_user
        if update.message.text == cancel_text:
            await end_session(update=update, context=context, user_id=user.id)
            return DataType.BEGIN
        logger.info("User %s requested nearby locations", user.id)

        user_location = update.message.location
        user_lat = user_location.latitude
        user_long = user_location.longitude

        msg = await update.message.reply_text(
                'Показываю, что есть поблизости:',
                reply_markup=ReplyKeyboardRemove()
        )

        data_loc, num_pages = await table_loc.get_nearby(latitude=user_lat,
                                   longitude=user_long)
        
        if data_loc is None:
            await update.message.reply_text(
                'Пока что тут пусто ☁️',
                reply_markup = ReplyKeyboardRemove())
            await update.message.reply_text(
                'Но ты можешь сам(а) добавить новую запись о локации, ' + \
                'либо посмотреть, на какие локации ты уже подписан(а).',
                reply_markup=keyboard_welcome
            )
            return DataType.BEGIN
            
        locations = [await loc_from_data(data_loc[i]) for i in range(num_pages)]  
        
        init_page = 1
        keyboard_pages = await loc_kbrd(page=init_page, num_pages=num_pages)
       
        distance = int(np.sqrt((locations[0].latitude - float(user_lat))**2 +\
                                (locations[0].longitude - float(user_long))**2) * 1e5)
        distance_info = f'<b>{distance}</b>\n'

        await fill_current_data(locations=locations,
                                keyboard=keyboard_pages,
                                distance_info=distance_info,
                                message=msg,
                                context=context,
                                mode='nearby_loc')

        await send_info(
                    data=locations,
                    page=init_page,
                    keyboard=keyboard_pages,
                    update=update,
                    context=context,
                    distance_info=distance_info
                    )
    except Exception as e:
        print('Exception in show_nearby, request_commands.py')
        print(e)
        logger.info(e)



async def show_fav_loc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = context.user_data['current'].user_id
        if update.message.text == cancel_text:
            # await update.message.reply_text('Приходи, когда будет, что показать...',
            #                                 reply_markup=keyboard_ok)
            await end_session(update=update, context=context, user_id=user_id)
            return DataType.BEGIN
        logger.info("User %s requested his/her locations", user_id)
        
        msg = await update.message.reply_text(
                'Показываю, на какие локации ты подписан(а): ',
                reply_markup=ReplyKeyboardRemove()
        )

        user_fav_locs, num_pages = await table_user.get_all_user_locs(user_id=user_id)

        if user_fav_locs is None:
            return None

        locations = [await loc_from_data(user_fav_locs[i]) for i in range(num_pages)]  
        
        init_page = 1
        keyboard_pages = await fav_loc_kbrd(page=init_page, num_pages=num_pages)
        
        await fill_current_data(locations=locations,
                        keyboard=keyboard_pages,
                        message=msg,
                        context=context,
                        mode='fav_loc')
        
        await send_info(
                data=locations,
                page=init_page,
                update=update,
                context=context,
                keyboard=keyboard_pages
                )
        return DataType.SIGNED
        
    except Exception as e:
        print('Exception in show_fav_loc, request_commands.py')
        print(e)
        logger.info(e)
    


async def paginate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        req = json.loads(query.data)
        
        if req['Method'] == 'pagination':  
            
            page = req['CurrentPage'] 
            data = context.user_data['current'].all_locations
            distance = context.user_data['current'].distance
            num_pages = len(data)

            if context.user_data['current'].mode == 'fav_loc':
                keyboard_pages = await fav_loc_kbrd(page=page, num_pages=num_pages)
            elif context.user_data['current'].mode == 'nearby_loc':
                keyboard_pages = await loc_kbrd(page=page, num_pages=num_pages)
                       
            await send_info(
                    data=data,
                    page=page,
                    distance_info=distance,
                    keyboard=keyboard_pages,
                    update=update,
                    context=context,
                    query=query
                    )
            
        elif req['Method'] == 'cancel':
            await query.delete_message() 
            msg = context.user_data['current'].intro_message
            await msg.delete()
            await query.from_user.send_message('Увидимся!', reply_markup=keyboard_ok)
            await end_session(update=update, context=context, 
                              user_id=context.user_data['current'].user_id,
                              query_from_user=query.from_user)
            return DataType.BEGIN

        elif req['Method'] == 'apply':
            await table_user.setup_users()
            page = req['CurrentPage']
            location = context.user_data['current'].all_locations[page-1]
            loc_id = location.id
            user_id = context.user_data['current'].user_id
            await table_loc.add_user(loc_id=loc_id)  
            result = await table_user.add_new_loc(user_id=user_id, loc_id=loc_id) 
            await query.from_user.send_message(result, reply_markup=ReplyKeyboardRemove())
            
        
        elif req['Method'] == 'delete':
            page = req['CurrentPage'] 
            location = context.user_data['current'].all_locations[page-1]
            loc_id = location.id
            user_id = context.user_data['current'].user_id
            await table_loc.delete_user(loc_id=loc_id)
            result = await table_user.delete_location(user_id=user_id, loc_id=loc_id)
            del context.user_data['current'].all_locations[page-1]
            await query.from_user.send_message(result, reply_markup=ReplyKeyboardRemove())
            
            data = context.user_data['current'].all_locations
            num_pages = len(data)
            if num_pages == 0:
                await query.delete_message()
                await query.from_user.send_message(
                    'Пока что тут пусто ☁️',
                    reply_markup = ReplyKeyboardRemove())
                await query.from_user.send_message(
                    'Но ты всегда можешь самостоятельно добавить локацию'+\
                    ' или посмотреть, что есть поблизости',
                    reply_markup=keyboard_welcome
                )
                return DataType.BEGIN
            elif num_pages > 0:
                distance = context.user_data['current'].distance
                keyboard_pages = await fav_loc_kbrd(page=page, num_pages=num_pages-1)
                await send_info(
                        data=data,
                        page=page,
                        distance_info=distance,
                        keyboard=keyboard_pages,
                        update=update,
                        context=context,
                        query=query
                        )


    except Exception as e:
        print('Exception in paginate, request_commands.py')
        print(e)
        logger.info(e)

