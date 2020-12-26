from telegram.ext import ConversationHandler


class BotConfig:
    START_STATE = 0
    END_STATE = ConversationHandler.END
    TRAINING_STATE = 1

    START_BUTTON_CAPTION = 'Поехали!'


class GlobalConfig:
    MAIN_LOG_PATH = 'bot.log'

    DB_NAME = 'gifty'
    DB_HOST = '127.0.0.1'
    DB_PORT = 27017
