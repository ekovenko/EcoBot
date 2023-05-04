from telegram.ext import (
    Application,
    CommandHandler, 
    MessageHandler,
    filters,
    ConversationHandler,
)


from commands import (
    start,
    cancel,
    photo,
    location,
    DataType
)


BOT_TOKEN = '6020419408:AAGqPVnOV3iZLZi2Ew2xsSUL88v10X2jAbI'


if __name__ == '__main__':
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points = [CommandHandler('start', start)],
        states = { 
                    DataType.PHOTO : [MessageHandler(filters.PHOTO, photo)],
                    DataType.LOCATION: [MessageHandler(filters.LOCATION, location)]
                  },
        fallbacks = [CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    application.run_polling()


