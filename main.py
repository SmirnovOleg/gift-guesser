import random
from dataclasses import dataclass
from functools import reduce
from itertools import product
from typing import List, Mapping

Option = str


@dataclass()
class Question:
    text: str
    options: List[Option]

    def __hash__(self):
        return hash(self.text) + 31 * reduce(lambda x, y: hash(x) * 31 + hash(y), self.options)


@dataclass
class Gift:
    name: str
    answers_history: Mapping[Question, Mapping[Option, int]]

    def __init__(self, name):
        self.name = name
        self.answers_history = {q: {o: 1.0 / len(q.options) for o in q.options} for q in questions}

    def __repr__(self):
        return self.name

    @property
    def marginal_probability(self) -> float:
        return 1.0 / len(gifts)

    def likelihood(self, answers: Mapping[Question, Option]) -> float:
        questions_likelihood = 1
        for q, o in answers.items():
            questions_likelihood *= self.answers_history[q][o] / sum(self.answers_history[q].values())
        return self.marginal_probability * questions_likelihood


questions = [
    Question(text='Is it for female?', options=['y', 'n']),
    Question(text='Is it a summer gift?', options=['y', 'n'])
]

gifts = [
    Gift('Bicycle'),
    Gift('Ski'),
    Gift('Dress'),
    Gift('Christmas toy')
]


def read_option(question: Question) -> Option:
    print('Your answer: ', end='')
    option = input()
    while option not in question.options:
        print('Your answer: ', end='')
        option = input()
    return option


def train():
    for gift, question in product(gifts, questions):
        print(gift)
        print(question)
        option = read_option(question)
        gift.answers_history[question][option] += 1


def guess():
    session = gifts.copy()
    answers = {}
    while True:
        question = random.choice(questions)
        print(question)
        option = read_option(question)
        answers[question] = option
        for gift in session:
            gift.answers_history[question][option] += 1
            print(gift)
            print(gift.likelihood(answers))


if __name__ == "__main__":
    print('Train:')
    train()
    print('Play:')
    guess()
