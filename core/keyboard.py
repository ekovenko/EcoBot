from telegram import InlineKeyboardMarkup, InlineKeyboardButton


button_start_sharing = InlineKeyboardButton(text='Внести запись', callback_data='start_sharing')
button_cancel = InlineKeyboardButton(text='В другой раз', callback_data='cancel')

keyboard_welcome = InlineKeyboardMarkup(
                inline_keyboard = [
                    [button_start_sharing], 
                    [button_cancel]
                ])

