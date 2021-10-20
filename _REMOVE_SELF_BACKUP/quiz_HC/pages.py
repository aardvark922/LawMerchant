from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


"""class quiz_Page(Page):

    form_model = "player"
    form_fields = ["Q1_choice", "Q2_choice", "Q3_choice", "Q4_choice","Q5_choice"]"""

class Recap(Page):
    pass


class Q1_Page(Page):

    form_model = "player"
    form_fields = ["Q1_choice"]

class Results_1(Page):
    pass

class Q2_Page(Page):

    form_model = "player"
    form_fields = ["Q2_choice"]

class Results_2(Page):
    pass


class Q3_Page(Page):

    form_model = "player"
    form_fields = ["Q3_choice"]

class Results_3(Page):
    pass


class Q4_Page(Page):

    form_model = "player"
    form_fields = ["Q4_choice","Q5_choice"]


class Results_4(Page):
    pass


class Results(Page):
    def vars_for_template(self):
        self.player.correct = self.player.num_correct()
        self.player.payoff = self.player.correct*0.5
        self.participant.payoff = self.player.payoff
        correct = self.player.correct
        return{'correct': correct}

page_sequence = [Recap, Q1_Page, Results_1, Q2_Page, Results_2, Q3_Page, Results_3,Q4_Page, Results_4, Results]
