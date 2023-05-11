from telegram.ext import (
    Application,
    CommandHandler, 
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler
)


from commands import (
    start,
    start_sharing,
    cancel,
    photo,
    location,
    help, 
    DataType
)


BOT_TOKEN = '6020419408:AAGqPVnOV3iZLZi2Ew2xsSUL88v10X2jAbI'


if __name__ == '__main__':
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points = [CommandHandler('start', start)],
        states = { 
                    DataType.BEGIN : [
                        CallbackQueryHandler(start_sharing, pattern='start_sharing'),
                        CallbackQueryHandler(cancel, pattern='cancel')
                    ],

                    DataType.PHOTO: [
                        MessageHandler(filters.PHOTO, photo)
                    ],
                    
                    DataType.LOCATION: [
                        MessageHandler(filters.LOCATION, location)
                  ]},
        fallbacks = [CommandHandler('cancel', cancel)]
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help', help))
    application.run_polling()


