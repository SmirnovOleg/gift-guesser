from __future__ import annotations

from math import log
from typing import List, Tuple

from mongoengine import Document, StringField, ListField, DictField, QuerySet

Option = str


class Question(Document):
    text = StringField(required=True)
    options = ListField(StringField(), required=True)

    def get_weighted_entropy(self, session: Session):
        weighted_entropy = 0
        for option in self.options:
            entropy = Gift.objects.get_entropy(session + (self, option))
            weight = 0
            for gift in Gift.objects:
                weight += gift.conditional_probability(self, option) * gift.likelihood(session)
            weighted_entropy += weight * entropy
        return weighted_entropy

    class WeightedEntropyQuerySet(QuerySet):
        def get_next(self, session: Session):
            return min(self, key=lambda question: question.get_weighted_entropy(session))

    meta = {'queryset_class': WeightedEntropyQuerySet}


Session = List[Tuple[Question, Option]]


class Gift(Document):
    name = StringField(required=True)
    link = StringField()
    history = DictField(required=True)

    @property
    def marginal_probability(self) -> float:
        # P ( Gift )
        return 1.0 / Gift.objects.count()

    def conditional_probability(self, question: Question, option: Option) -> float:
        # P ( Question -> Option | Gift )
        return self.history[question][option] / sum(self.history[question].values())

    def likelihood(self, session: Session) -> float:
        # P (Gift | Question_1 -> Option_1, Question_2 -> Option_2, ... )
        questions_likelihood = 1
        for question, option in session:
            questions_likelihood *= self.conditional_probability(question, option)
        return self.marginal_probability * questions_likelihood

    class EntropyQuerySet(QuerySet):
        def get_entropy(self, session: Session):
            entropy = 0
            for gift in self:
                p = gift.likelihood(session)
                entropy -= p * log(p)
            return entropy

    meta = {'queryset_class': EntropyQuerySet}
