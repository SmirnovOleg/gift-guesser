import os
import random

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

from config import BotConfig
from database.db import Question, Gift
from log import logger
from utils import chunks


def start(update: Update, context: CallbackContext):
    reply_keyboard = [[BotConfig.START_BUTTON_CAPTION]]
    update.message.reply_text(
        "Привет! Нам нужна помощь с обучением ML модели для подбора подарков.\n"
        "Я буду давать конкретный подарок и вопрос о нём, а ты отвечать, как считаешь нужным.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard),
    )
    return BotConfig.START_STATE


def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f'User {user.id} canceled the conversation.')
    update.message.reply_text(
        'Спасибо за разметку!',
        reply_markup=ReplyKeyboardRemove()
    )
    return BotConfig.END_STATE


def random_question_callback(update: Update, context: CallbackContext):
    question = random.choice(Question.objects)
    gift = random.choice(Gift.objects)

    context.user_data['last_question'] = question
    context.user_data['last_gift'] = gift

    reply_keyboard = list(chunks(question.options, 2))
    update.message.reply_text(
        f'{gift.name}\n{question.text}',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard)
    )

    return BotConfig.TRAINING_STATE


def next_question_callback(update: Update, context: CallbackContext):
    chosen_option = update.message.text
    last_question = context.user_data['last_question']
    last_gift = context.user_data['last_gift']

    if chosen_option not in last_question.options:
        update.message.reply_text('Такого варианта ответа нет.')
        return random_question_callback(update, context)

    logger.info(f'User {update.message.from_user.id} chose option {chosen_option} '
                f'for the question {last_question.id} and gift {last_gift.id}.')

    update_query = {f'inc__history__{last_question.text}__{chosen_option}': 1}
    Gift.objects(id=last_gift.id).update_one(**update_query)  # todo: index by question.id, not question.text

    return random_question_callback(update, context)


def main():
    token = os.getenv('TELEGRAM_TOKEN')
    updater = Updater(token)
    dispatcher = updater.dispatcher

    training_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BotConfig.START_STATE: [
                MessageHandler(
                    filters=Filters.regex(f'^({BotConfig.START_BUTTON_CAPTION})$'),
                    callback=random_question_callback
                )
            ],
            BotConfig.TRAINING_STATE: [
                MessageHandler(
                    filters=Filters.text & ~Filters.command,  # todo: setup correct filters
                    callback=next_question_callback
                )
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(training_conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
