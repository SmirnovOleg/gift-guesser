import os

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

from config import BotConfig, GlobalConfig
from db.models import Session
from db.scripts import Question, Gift
from log import logger
from utils import chunks


def start_guessing(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f'User {user.id} ({user.username}) started conversation.')

    reply_keyboard = [[BotConfig.START_CAPTION]]
    update.message.reply_text(
        "Привет! Давай я помогу тебе подобрать подарок!",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard),
    )

    context.user_data['session']: Session = []

    return BotConfig.START_STATE


def cancel_guessing(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f'User {user.id} ({user.username}) cancelled conversation.')

    update.message.reply_text(
        'До встречи!',
        reply_markup=ReplyKeyboardRemove()
    )
    return BotConfig.END_STATE


def next_question_callback(update: Update, context: CallbackContext, next_question=None):
    session = context.user_data['session']
    if not next_question:
        next_question = Question.objects.get_next(session)
    context.user_data['last_question'] = next_question

    reply_keyboard = list(chunks(next_question.options, 2))
    update.message.reply_text(
        f'{next_question.text}',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard)
    )

    return BotConfig.GUESSING_STATE


def update_callback(update: Update, context: CallbackContext):
    chosen_option = update.message.text
    session = context.user_data['session']
    last_question = context.user_data['last_question']

    if chosen_option not in last_question.options:
        update.message.reply_text('Такого варианта ответа нет. Давайте попробуем еще раз!')
        return next_question_callback(update, context, next_question=last_question)

    logger.info(f'User {update.message.from_user.id} chose option {chosen_option} '
                f'for the question {last_question.text}.')
    session.append((last_question, chosen_option))
    most_probable_gift: Gift = max(Gift.objects, key=lambda gift: gift.likelihood(session))

    if most_probable_gift.likelihood(session) > GlobalConfig.CONFIDENCE_LIMIT:
        context.user_data['suggestion'] = most_probable_gift
        reply_keyboard = [[BotConfig.YES_CAPTION, BotConfig.NO_CAPTION]]
        update.message.reply_text(
            f'Я думаю, вам подходит {most_probable_gift.name}. Как считаете?',
            reply_markup=ReplyKeyboardMarkup(reply_keyboard)
        )
        return BotConfig.SUGGESTION_STATE

    return next_question_callback(update, context)


def suggest_callback(update: Update, context: CallbackContext):
    chosen_option = update.message.text
    suggested_gift = context.user_data['suggestion']

    if chosen_option == BotConfig.YES_CAPTION:
        logger.info(f'User {update.message.from_user.id} confirmed gift {suggested_gift.name}.')
        update.message.reply_text(
            'Отлично! Если буду нужен, пишите, я всегда здесь :)',
            reply_markup=ReplyKeyboardRemove()
        )
        session = context.user_data['session']
        for question, option in session:
            update_query = {f'inc__history__{question.text}__{option}': 1}
            Gift.objects(id=suggested_gift.id).update_one(**update_query)  # todo: index questions by id, not text

        return BotConfig.END_STATE
    else:
        logger.info(f'User {update.message.from_user.id} rejected gift {suggested_gift.name}.')
        return next_question_callback(update, context)


def main():
    token = os.getenv('TELEGRAM_TOKEN')
    updater = Updater(token)
    dispatcher = updater.dispatcher

    guessing_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_guessing)],
        states={
            BotConfig.START_STATE: [
                MessageHandler(
                    filters=Filters.regex(f'^({BotConfig.START_CAPTION})$'),
                    callback=next_question_callback
                )
            ],
            BotConfig.GUESSING_STATE: [
                MessageHandler(
                    filters=Filters.text & ~Filters.command,
                    callback=update_callback
                )
            ],
            BotConfig.SUGGESTION_STATE: [
                MessageHandler(
                    filters=Filters.regex(f'^({BotConfig.YES_CAPTION}|{BotConfig.NO_CAPTION})$'),
                    callback=suggest_callback
                )
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_guessing)],
    )

    dispatcher.add_handler(guessing_conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
