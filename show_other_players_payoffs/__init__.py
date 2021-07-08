from otree.api import *


class Constants(BaseConstants):
    name_in_url = 'show_other_players_payoffs'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(others=player.get_others_in_group())


page_sequence = [Results]