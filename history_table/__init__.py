from otree.api import *

doc = """History table"""

class Constants(BaseConstants):
    name_in_url = 'history_table'
    players_per_group = None
    num_rounds = 10


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    number = models.IntegerField(label="Enter a number")


class MyPage(Page):
    form_model = 'player'
    form_fields = ['number']


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        print(dict(me_in_all_rounds=player.in_all_rounds()))
        return dict(me_in_all_rounds=player.in_all_rounds())



page_sequence = [MyPage, Results]