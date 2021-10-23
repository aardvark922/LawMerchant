from otree.api import *


doc = """
Quiz with explanation. Re-display the previous page's form as read-only, with answers/explanation.
"""


class Constants(BaseConstants):
    name_in_url = 'comprehenstion_test_c'
    players_per_group = None
    num_rounds = 1
    form_template = __name__ + '/form.html'
    true_false_choices = [(1, 'True'), (0, 'False')]
    observer_payoff = cu(18)
    quiz_payoff=cu(25)


def get_quiz1_data():
    return [
        dict(
            name='quiz1',
            solution=False,
            explanation="Your role as the observer or an active participant will be "
                        "randomly assigned in each cycle and is independent of your role in a previous cycle",
        ),
        dict(
            name='quiz2',
            solution=2,
            explanation="You earn 5 points and your match earns 30 poitns.",
        ),
        dict(
            name='quiz3',
            solution=False,
            explanation="There is a 90% chance that at the end of a round the cycle will continue. Hence, you wouldn't "
                        "know the length of each cycle in advance.",
        ),
        dict(
            name='quiz4',
            solution=True,
            explanation="The answer is True.",
        ),
        dict(
            name='quiz5',
            solution=True,
            explanation="The answer is True.",
        ),
    ]

def get_quiz_data():
    return [
        dict(
            name='quiz1',
            solution=False,
            explanation="Your role as the observer or an active participant will be "
                        "randomly assigned in each cycle and is independent of your role in a previous cycle",
        ),
        dict(
            name='quiz2',
            solution=2,
            explanation="You earn 5 points and your match earns 30 poitns.",
        ),
        dict(
            name='quiz3',
            solution=False,
            explanation="There is a 90% chance that at the end of a round the cycle will continue. Hence, you wouldn't "
                        "know the length of each cycle in advance.",
        ),
        dict(
            name='quiz4',
            solution=True,
            explanation="The answer is True.",
        ),
        dict(
            name='quiz5',
            solution=True,
            explanation="The answer is True.",
        ),
    ]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    quiz_earning=models.CurrencyField()
    # TODO comprehenstion test questions for two treatments
    quiz1 = models.BooleanField(
        label='1. If you are the observer in current cycle, '
              'you will be an active participant in the next cycle for sure.',
        choices=Constants.true_false_choices)
    quiz2 = models.IntegerField(
        label='2.  If you are an active player in current cycle, '
              'when you choose Y and your partner chooses Z. What is your payoff?',
        choices=[(1, "25"), (2, "5"), (3, "10"), (4, "30")],
        widget=widgets.RadioSelect)
    quiz3 = models.BooleanField(
        label="3. The lengths of each cycle are the same.",
        choices=Constants.true_false_choices
    )
    quiz4 = models.BooleanField(
        label="4. You might will be assigned to the set with someone you have been assigned in a previous cycle.",
        choices=Constants.true_false_choices
    )
    quiz5 = models.BooleanField(
        label="5. If you are an active participant, you will not know the identity of your matches.",
        choices=Constants.true_false_choices
    )

def get_quiz_results(player: Player):
    fields = get_quiz_data()
    correct_answers=0
    for d in fields:
        if getattr(player, d['name']) == d['solution']:
            correct_answers = correct_answers + 1
    player.payoff = correct_answers*Constants.quiz_payoff
    player.participant.quiz_earning=player.payoff
    results = dict(correct_answers=correct_answers, quiz_earning=player.payoff)
    return results

class Questions(Page):
    form_model = 'player'
    form_fields = ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5']


    @staticmethod
    def vars_for_template(player: Player):
        fields = get_quiz_data()
        return dict(fields=fields, show_solutions=False)


class Results(Page):
    form_model = 'player'
    form_fields = ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5']

    @staticmethod
    def vars_for_template(player: Player):
        results=get_quiz_results(player)
        fields = get_quiz_data()
        # we add an extra key 'is_correct' to each field
        for d in fields:
            d['is_correct'] = getattr(player, d['name']) == d['solution']
        return dict(fields=fields, show_solutions=True,quiz_earning=results['quiz_earning'],
                    correct_answers=results['correct_answers'])

    @staticmethod
    def error_message(player: Player, values):
        for field in values:
            if getattr(player, field) != values[field]:
                return "A field was somehow changed but this page is read-only."

class Instructions1(Page):
    pass

page_sequence = [Instructions1, Questions, Results]