import csv

from mongoengine import connect

from config import GlobalConfig
from db.models import Gift, Question

connect(db=GlobalConfig.DB_NAME, host=GlobalConfig.DB_HOST, port=GlobalConfig.DB_PORT)


def init_db():
    with open('data/questions.csv') as file:
        reader = csv.reader(file, delimiter=',')
        next(reader, None)  # skip header
        for row in reader:
            text, options = row[0], [option.strip() for option in row[1].split('/')]
            options.append('Не знаю')
            Question(text=text, options=options).save()

    with open('data/gifts.csv') as file:
        reader = csv.reader(file, delimiter=',')
        next(reader, None)  # skip header
        for row in reader:
            name, link = row
            history = {}
            for question in Question.objects:
                history[question.text] = {option: 1 for option in question.options}
            Gift(name=name, link=link, history=history).save()


def clear_db():
    Gift.drop_collection()
    Question.drop_collection()


if __name__ == '__main__':
    clear_db()
    init_db()
