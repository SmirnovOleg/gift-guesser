from telegram.ext import ConversationHandler


class BotConfig:
    START_STATE = 0
    END_STATE = ConversationHandler.END
    TRAINING_STATE = 1
    GUESSING_STATE = 2
    SUGGESTION_STATE = 3

    START_CAPTION = 'Поехали!'
    YES_CAPTION = 'Да'
    NO_CAPTION = 'Нет'
    DONT_KNOW_CAPTION = 'Не знаю'


class GlobalConfig:
    MAIN_LOG_PATH = 'bot.log'
    CONFIDENCE_LIMIT = 0.5

    DB_NAME = 'gifty'
    DB_HOST = '127.0.0.1'
    DB_PORT = 27017
