from otree.api import *



author = 'Your name here'
doc = """
demographics
"""


class Constants(BaseConstants):
    name_in_url = 'demographics'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField(min=16, max=100, label=r"What is your age in years? Please enter a number between 16 and 100.")  # age in years
    gender = models.IntegerField(
        choices=[
            [1, 'Male'],
            [2, 'Female'],
            [3, 'Other/Prefer not to say'],
        ],
        label="What is your gender?",
    )
    field_of_study = models.IntegerField(
        choices=[
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
        ],
        label="What is your main field of study?",
    )
    country = models.StringField(
        label='What country were you born in? Please enter the country name below.'
    )
    length_in_US = models.IntegerField(
        choices=[
            [1, 'N/A'],
            [2, 'More than 5 years'],
            [3, '2-5 years'],
            [4, '1-2 years'],
            [5, 'Less than 1 year'],
        ],
        label="If you were not born in the US, how long have you lived in the US?",
    )
    race = models.IntegerField(
        choices=[
            [1, 'Asian'],
            [2, 'African American'],
            [3, 'Caucasian'],
            [4, 'Hispanic or Latino'],
            [5, 'Other'],
        ],
        label="What do you consider your primary racial identity?",
    )
    gpa = models.IntegerField(
        choices=[
            [1, 'Between 3.50 and 4.00'],
            [2, 'Between 3.00 and 3.49'],
            [3, 'Between 2.50 and 2.99'],
            [4, 'Below 2.00'],
            [5, 'N/A as this is my first semester at University'],
        ],
        label="What is your cumulative GPA at the University?",
    )
    years_at_uni = models.IntegerField(
        choices=[
            [1, '1st year'],
            [2, '2nd year'],
            [3, '3rd year'],
            [4, '4th year or above'],
            [5, 'Graduate Student'],
        ],
        label="Are you an undergraduate student (which year?) or a graduate student?",
    )
    num_exper = models.IntegerField(
        min=0,
        max=100,
        label='How many economics experiments have you participated in before this one? Please enter a number.',
    )

    decision_process_ob = models.LongStringField(
        blank=True,
        label='We are interested in your decision process in the experiment, please share your decision rules when you are the observer if you would like to:',
    )

    decision_process_ac = models.LongStringField(
        blank=True,
        label='Please share your decision rules when you are an active participant if you would like to:',
    )
    review = models.LongStringField(
        blank=True,
        label='If you have any comments about this experiment, please enter below.'
    )


# FUNCTIONS
def vars_for_admin_report(subsession: Subsession):
    labels = []
    payoffs = []
    for p in subsession.get_players():
        labels.append(p.participant.label)
        payoffs.append(p.participant.payoff)
    return dict(labels=labels, payoffs=payoffs)


# PAGES
class Demographics(Page):
    form_model = 'player'
    form_fields = [
        'age',
        'gender',
        'field_of_study',
        'country',
        'length_in_US',
        'race',
        'gpa',
        'years_at_uni',
        'num_exper',
        'decision_process_ob',
        'decision_process_ac',
        'review',
    ]
    ## this doesn't work...
    # def length_in_US_choices(self):
    #     if self.player.country == 1:
    #         choices = [[1, "N/A"]]
    #     else:
    #         choices = [[2, 'More than 5 years'],
    #             [3, '2-5 years'],
    #             [4, '1-2 years'],
    #             [5, 'Less than 1 year'],]
    #     return choices
    # def error_message(self, values):
    # print('values is', values)
    # if values["country"] == 1 and values['length_in_US'] != 1:
    # return 'If you were born in the US, you must answer \'N/A\' for the question: \'If you were not born in the US, how long have you lived in the US?\''
    # if values["country"] != 1 and values['length_in_US'] == 1:
    # return 'If you were not born in the US, you cannot answer \'N/A\' for the question: \'If you were not born in the US, how long have you lived in the US?\''

class Final(Page):
    pass


page_sequence = [
    Demographics,
    Final,
]
