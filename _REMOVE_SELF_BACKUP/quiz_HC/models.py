from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)


author = 'Junya Zhou'
doc = """
Comprehension quiz for the persuasion experiment
"""


class Constants(BaseConstants):
    name_in_url = 'quiz_HC'
    players_per_group = None
    num_rounds = 1
    cost = c(4)


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    Q1_choice = models.IntegerField(
    choices=[
        [1, 'True'],
        [2, 'False'],
    ],
    label='1. True or False. If the receiver chooses "Not Observe" in Stage 2, Common Communication Plan is shown but Hidden Communication Plan is not shown.',
    widget=widgets.RadioSelect,
)

    Q2_choice = models.IntegerField(
    choices=[
        [1, 'True'],
        [2, 'False'],
    ],
    label='2. True or False. When the message is Blue, the drawn ball is definitely Blue. When the message is Red, the higher the probability the Sender chose to send message Red when the drawn ball is Blue, the lower the probability that the drawn ball is Blue.',
    widget=widgets.RadioSelect,
)


    Q3_choice = models.IntegerField(
    choices=[
        [1, 'Send message Red 100% of the time and Blue 0% of the time'],
        [2, 'Send message Red 34% of the time and Blue 66% of the time'],
        [3, 'Send message Red 65% of the time and Blue 35% of the time'],
        [4, 'Unsure of the probabilities']
    ],
    widget=widgets.RadioSelect
)

    Q4_choice = models.IntegerField(
        choices = [
            [1, 'Red'],
            [2, 'Blue']
        ],
    widget=widgets.RadioSelect
    )

    Q5_choice = models.IntegerField(
    choices=[
        [1, 'Sender 15, Receiver 11'],
        [2, 'Sender 5, Receiver 11'],
        [3, 'Sender 15, Receiver 1'],
        [4, 'Sender 5, Receiver 1'],
    ],
    widget=widgets.RadioSelect
)

    correct = models.IntegerField()
    correct_1 = models.IntegerField()
    correct_2 = models.IntegerField()
    correct_3 = models.IntegerField()
    correct_4 = models.IntegerField()
    correct_5 = models.IntegerField()


    def num_correct(self):
        if self.Q1_choice == 1:
            self.correct_1 = 1
        else:
            self.correct_1 = 0
        if self.Q2_choice == 1:
            self.correct_2 = 1
        else:
            self.correct_2 = 0
        if self.Q3_choice == 2:
            self.correct_3 = 1
        else:
            self.correct_3 = 0
        if self.Q4_choice == 2:
            self.correct_4 = 1
        else:
            self.correct_4 = 0
        if self.Q5_choice == 2:
            self.correct_5 = 1
        else:
            self.correct_5 = 0
        self.correct = self.correct_1 + self.correct_2 + self.correct_3 + self.correct_4 + self.correct_5
        return self.correct


