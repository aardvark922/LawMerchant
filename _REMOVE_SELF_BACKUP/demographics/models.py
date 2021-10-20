from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)


author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'demographics'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):

    def vars_for_admin_report(self):
        labels = []
        payoffs = []
        for p in self.get_players():
            labels.append(p.participant.label)
            payoffs.append(p.participant.vars['payoffs'])

        return dict(labels=labels, payoffs=payoffs)


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    age = models.IntegerField(min=18, max=100, label=r"What is your age in years?")  # age in years
    gender = models.IntegerField(choices=[
        [1, 'Male'],
        [2, 'Female'],
        [3, 'Other/Prefer not to say'],
    ], label="What is your gender?")
    field_of_study = models.IntegerField(choices=[
        [1, 'Management/Business'],
        [2, 'Economics'],
        [3, 'Humanities'],
        [4, 'Liberal Arts'],
        [5, 'Education'],
        [6, 'Engineering'],
        [7, 'Science'],
        [8, 'Social Sciences'],
        [9, 'Agriculture'],
        [10, 'Pharmacy'],
        [11, 'Nursing'],
        [12, 'Other'],
    ], label="What is your main field of study?")
    country = models.StringField(label='What country were you born in? Please enter the country name below.')
    length_in_US = models.IntegerField(choices=[
        [1, 'N/A'],
        [2, 'More than 5 years'],
        [3, '2-5 years'],
        [4, '1-2 years'],
        [5, 'Less than 1 year'],
    ], label="If you were not born in the US, how long have you lived in the US?")
    race = models.IntegerField(choices=[
        [1, 'Asian'],
        [2, 'Black'],
        [3, 'Caucasian'],
        [4, 'Hispanic'],
        [5, 'Other'],
    ], label="What do you consider your primary racial identity?")
    gpa = models.IntegerField(choices=[
        [1, 'Between 3.50 and 4.00'],
        [2, 'Between 3.00 and 3.49'],
        [3, 'Between 2.50 and 2.99'],
        [4, 'Below 2.00'],
        [5, 'N/A as this is my first semester at University'],
    ], label="What is your cumulative GPA at the University?")
    years_at_uni = models.IntegerField(choices=[
        [1, '1st year'],
        [2, '2nd year'],
        [3, '3rd year'],
        [4, '4th year or above'],
        [5, 'Graduate Student'],
    ], label="Are you an undergraduate student (which year?) or a graduate student?")
    num_exper = models.IntegerField(min=0, max=100, label='How many economics experiments have you participated in before this one?')
    
    pay_sig1 = models.IntegerField(min=0, max=100, label='1 signal')
    pay_sig2 = models.IntegerField(min=0, max=100, label='2 signals')
    pay_sig3 = models.IntegerField(min=0, max=100, label='3 signals')
    pay_sig4 = models.IntegerField(min=0, max=100, label='4 signals')
    
    bid_A = models.IntegerField(min=0, max=1400, label='A')
    bid_B = models.IntegerField(min=0, max=1400, label='B')
    bid_C = models.IntegerField(min=0, max=1400, label='C')
    bid_D = models.IntegerField(min=0, max=1400, label='D')
    bid_E = models.IntegerField(min=0, max=1400, label='E')
    
    decision_process = models.LongStringField(blank=True, label = 
                'We are interested in your decision process in the experiment, please share your decision rules if you would like to')
    review = models.LongStringField(blank=True, label = 
                'If you have any comments about this experiment, please enter below.')