from telegram.ext import (
    Application,
    CommandHandler, 
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
    ExtBot
)
import json
from new_entry_commands import (
    start,
    begin_sharing,
    photo,
    location,
    approx_size,
    garbage_type,
    end_session,
    show_fav_loc
)
from dataclass import (
    DataType
)
from request_commands import (
    show_nearby,
    paginate
)
from keyboard import (
    welcome_buttons, 
    size_buttons,
    type_buttons,
    cancel_text
)
from loc_table import (
    table_loc
)
from user_table import (
    table_user
)

with open('config.json', 'r') as cfg:
  data = json.load(cfg) 

BOT_TOKEN = data['bot_token']



if __name__ == '__main__':
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points = [CommandHandler('start', start)],
        states = { 
                    DataType.BEGIN : [
                        MessageHandler(filters.ALL, begin_sharing)
                    ],

                    DataType.PHOTO: [
                        MessageHandler(filters.ALL, photo)
                    ],
                    
                    DataType.SIZE: [
                        MessageHandler(filters.ALL, approx_size)
                    ],

                    DataType.TYPE: [
                        MessageHandler(filters.ALL, garbage_type)
                    ],
                    
                    DataType.LOCATION: [
                        MessageHandler(filters.ALL, location)
                    ],

                    DataType.NEARBY: [
                        MessageHandler(filters.LOCATION|filters.Text(cancel_text), show_nearby),
                        CallbackQueryHandler(paginate)
                    ],

                    DataType.SIGNED: [
                        CallbackQueryHandler(paginate)
                    ],
                    DataType.END: [
                        MessageHandler(filters.ALL & (~filters.COMMAND), end_session)
                    ]
                  },
        fallbacks = [MessageHandler(~filters.COMMAND,  end_session)]

    )
    
    application.add_handler(conv_handler)
    # application.add_handler(CommandHandler('help', help))
    application.run_polling()


