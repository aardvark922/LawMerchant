from otree.api import *


doc = """
Quiz with explanation. Re-display the previous page's form as read-only, with answers/explanation.
"""


class Constants(BaseConstants):
    name_in_url = 'comprehenstion_test'
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
        dict(
            name='quiz6',
            solution=False,
            explanation="Only when you queried the record of your match can you have the opportunity to report him/her later.",
        ),
        dict(
            name='quiz7',
            solution=True,
            explanation="The answer is True.",
        ),
        dict(
            name='quiz8',
            solution=False,
            explanation="Under this scenario, you match will be given a false statement about your record saying that"
                        " you have a Bad record. However, this false statement doesn't affect your actual record.",
        ),
        dict(
            name='quiz9',
            solution=False,
            explanation="You can also earn points by requesting points from active participants.",
        ),
        dict(
            name='quiz10',
            solution=False,
            explanation="You don't update record for an active participant if he/she choose to pay the fine to his/her match.",
        ),
    ]

def get_quiz0_data():
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
        ),       dict(
            name='quiz6',
            solution=False,
            explanation="Only when you queried the record of your match can you have the opportunity to report him/her later.",
        ),
        dict(
            name='quiz7',
            solution=True,
            explanation="The answer is True.",
        ),
        dict(
            name='quiz8H',
            solution=False,
            explanation="It can also be that your match accepted to pay a fine of 20 points to his/her previous match "
                        "when he/she was reported",
        ),
        dict(
            name='quiz9H',
            solution=False,
            explanation="The statement to send to each pair is generated according to the actual record",
        ),
        dict(
            name='quiz10',
            solution=False,
            explanation="You don't update record for an active participant if he/she choose to pay the fine to his/her match.",
        ),
    ]


class Subsession(BaseSubsession):
    dishonesty = models.BooleanField()


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
        label='2.  If you are an active player, '
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
    quiz6 = models.BooleanField(
        label="6. If you are an active participant, "
              "you can report to the observer even if you didn’t ask for a statement about your match.",
        choices=Constants.true_false_choices
    )
    quiz7 = models.BooleanField(
        label="7. If you are an active participant and reject to pay a fine, "
              "your record will become Bad for the remainder of this cycle.",
        choices=Constants.true_false_choices
    )
    quiz8H = models.BooleanField(
        label="8. If you are an active participant "
              "and receive the statement “Your match’s record is Good”, "
              "it only means that your match has never been reported by his/her previous match.",
        choices=Constants.true_false_choices
    )
    quiz8 = models.BooleanField(
        label="8. If you are an active participant "
              "and reject to give the requested number of points to the observer, your record will become Bad.",
        choices=Constants.true_false_choices
    )
    quiz9H = models.BooleanField(
        label="9. If you are the observer, "
              "you are free to choose what statement to send when you receive a query from an active participant.",
        choices=Constants.true_false_choices
    )
    quiz9 = models.BooleanField(
        label=f"9. If you are the observer, "
              f"your sources of earning in each round are only a flat rate of {Constants.observer_payoff} and the payment from queries.",
        choices=Constants.true_false_choices
    )
    quiz10 = models.BooleanField(
        label="10. If you are the observer, "
              "and if an active participant accepts to pay the fine, you will change his/her record to “Bad”.",
        choices=Constants.true_false_choices
    )

def get_quiz_results(player: Player):
    if player.subsession.dishonesty is True:
        fields = get_quiz1_data()
    else:
        fields = get_quiz0_data()
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

    @staticmethod
    def get_form_fields(player):
        player.subsession.dishonesty = player.subsession.session.config['dishonesty']
        if player.subsession.dishonesty is True:
            # comprehentions test for dishonest treatment
            return ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5', 'quiz6', 'quiz7', 'quiz8', 'quiz9', 'quiz10']
        else:
            return ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5', 'quiz6', 'quiz7', 'quiz8H', 'quiz9H', 'quiz10']

    @staticmethod
    def vars_for_template(player: Player):
        if player.subsession.dishonesty is True:
            fields = get_quiz1_data()
        else:
            fields = get_quiz0_data()
        return dict(fields=fields, show_solutions=False)


class Results(Page):
    form_model = 'player'
    @staticmethod
    def get_form_fields(player):
        player.subsession.dishonesty=player.subsession.session.config['dishonesty']
        if player.subsession.dishonesty is True:
            #comprehentions test for dishonest treatment
            return ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5','quiz6','quiz7','quiz8','quiz9','quiz10']
        else:
            return ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5', 'quiz6', 'quiz7', 'quiz8H', 'quiz9H', 'quiz10']

    @staticmethod
    def vars_for_template(player: Player):
        results=get_quiz_results(player)
        if player.subsession.dishonesty is True:
            fields = get_quiz1_data()
        else:
            fields = get_quiz0_data()
        # we add an extra key 'is_correct' to each field
        for d in fields:
            d['is_correct'] = getattr(player, d['name']) == d['solution']
        return dict(fields=fields, show_solutions=True,quiz_earning=results['quiz_earning'],
                    correct_answers=results['correct_answers'])

    @staticmethod
    def error_message(player: Player, values):
        for field in values:
            if getattr(player, field) != values[field]:
                return "Error message: You are not supposed to change your selection of choice at result page. The change of selection" \
                       " won't change your earning from comprehension test. If you see this error message, please raise your hand." \
                       " An experimenter will come to assist you."

class Instructions1(Page):
    pass

page_sequence = [Instructions1, Questions, Results]