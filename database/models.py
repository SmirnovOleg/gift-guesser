from typing import Mapping

from mongoengine import Document, StringField, ListField, DictField


class Question(Document):
    text = StringField(required=True)
    options = ListField(StringField(), required=True)


class Gift(Document):
    name = StringField(required=True)
    link = StringField()
    history = DictField(required=True)

    @property
    def marginal_probability(self) -> float:
        return 1.0 / Gift.objects.count()

    def likelihood(self, session: Mapping) -> float:
        questions_likelihood = 1
        for question, answer in session.items():
            questions_likelihood *= self.history[question][answer] / sum(self.history[question].values())
        return self.marginal_probability * questions_likelihood
