from otree.api import *
import numpy as np
import time
import random

c = Currency

doc = """
This is an indefinitely repeated Prisoner's Dilemma with random rematching every period.
"""


class Constants(BaseConstants):
    name_in_url = 'MWR_control'
    instructions_template = 'control/instructions.html'
    players_per_group = None
    num_super_games = 5
    delta = 0.90  # discount factor equals to 0.90

    time_limit = 60 * 20
    time_limit_seconds = 60 * 20

    last_rounds = [10, 40, 70]
    last_round = 70

    # generate a list of supergame lengths
<<<<<<< HEAD
    # super_game_duration = list(np.random.geometric(p=(1 - delta), size=num_super_games))
    # super_game_duration = [int(s) for s in super_game_duration]
=======
    #TODO: can I implement the following without using numpy?
    #TODO: how to implement block random termination?
    # super_game_duration = list(np.random.geometric(p=(1 - delta), size=num_super_games))
    # super_game_duration = [int(s) for s in super_game_duration]
    #TODO: seems that delta in the last line could not be recognized by python or otree?
>>>>>>> 76f2fc82ca43c03c43359a205234374fea2549a3

    # List of starting round for each super game
    # super_games_start_round = [1]
    # start_round = 1
    # for s in super_game_duration[:-1]:
    #     # only need to use first four lengths to calculate start round
    #     start_round = start_round + s
    #     # print('start round:',start_round)
    #     super_games_start_round = super_games_start_round + [start_round]
    #     # print('super game start round:',super_games_start_round)
    num_rounds = 100 #  sum(super_game_duration)

    # Nested groups parameters
    super_group_size = 7
    observer_num = 1
    group_size = 2

    # parameters for PD matrix
    # payoff if 1 player defects and the other cooperates""",
    betray_payoff = cu(30)
    betrayed_payoff = cu(5)

    # payoff if both players cooperate or both defect
    both_cooperate_payoff = cu(25)
    both_defect_payoff = cu(10)


class Subsession(BaseSubsession):
    curr_super_game = models.IntegerField(initial=0)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pair_id = models.IntegerField(initial=0)
    decision = models.StringField(
        initial='NA',
        choices=[['Action Y', 'Action Y'], ['Action Z', 'Action Z']],
        label="""This player's decision""",
        widget=widgets.RadioSelect
    )


# FUNCTIONS
def creating_session(subsession: Subsession):
    # Importing modules needed
    from random import randint, shuffle, choices
    # Get Constants attributes once for all
    const = Constants

    # Set pairs IDs to identify who is matched with whom
    pair_ids = [n for n in range(1, const.super_group_size // const.group_size + 1)] * const.group_size
    # print('pair ids:', pair_ids)

    if subsession.round_number == 1:
        from itertools import accumulate

        super_games_duration = list()
        for s in range(const.num_super_games):
            n = 0
            while True:
                n += 1
                next_round = choices([True, False], weights=[const.delta, 1 - const.delta], k=1)[0]
                if not next_round:
                    break
            super_games_duration.append(n)

        subsession.session.vars['super_games_duration'] = super_games_duration
        subsession.session.vars['super_games_end_rounds'] = list(accumulate(super_games_duration))
        subsession.session.vars['super_games_start_rounds'] = [1] + [r + 1 for r in subsession.session.vars['super_games_end_rounds'][1:]]

        subsession.curr_super_game = 1

        num_rounds_tot = sum(super_games_duration)
        if num_rounds_tot > const.num_rounds:
            raise ValueError('Oooops, super games are longer than the num_rounds in Constants')

    else:
        curr_round = subsession.round_number
        for i, end in enumerate(subsession.session.vars['super_games_end_rounds']):
            print('#####################')
            print('current supergame:',i)
            print('current round number:', curr_round )
            print('current supergame ends at round:',end)
            if curr_round > end:
                subsession.curr_super_game = i + 1
                print('current supergame after if loop',subsession.curr_super_game)

    # If the current round is the first round of a super game, then set the supergroups
    if subsession.round_number in subsession.session.vars['super_games_start_rounds']:
        # Get all players in the session and in the current round
        ps = subsession.get_players()
        # Apply in-place permutation
        shuffle(ps)
        # Set list of list, where each sublist is a supergroup
        super_groups = [ps[n:n + const.super_group_size] for n in range(0, len(ps), const.super_group_size)]
        print('current round number:', subsession.round_number)
        # print('super groups:',super_groups)
        # Set group matrix in oTree based on the supergroups
        subsession.set_group_matrix(super_groups)
        # Call the set_pairs function
        set_pairs(subsession, pair_ids, const.observer_num)

    # If the current round is not the first round of a super game, then just set new pairs
    else:
        # Set group matrix in oTree based on the matrix of the previous round
        subsession.group_like_round(subsession.round_number - 1)
        # Call the set_pairs function
        set_pairs(subsession, pair_ids, const.observer_num)


# Within each supergroup, randomly assign a paird ID, excluding the last player who will be an observer
def set_pairs(subsession: Subsession, pair_ids: list, observer_num: int):
    from random import shuffle
    # Get the supergroups for this round
    super_groups = subsession.get_groups()
    for g in super_groups:
        players = g.get_players()
        shuffle(pair_ids)
        for n, p in enumerate(players[:len(players) - observer_num]):
            p.pair_id = pair_ids[n]

# To be used for observer's history table
def get_supergroup_previous_others(player: Player):
    supergame_first_round = player.session.vars['super_games_start_rounds'][player.subsession.curr_super_game - 1]
    return [other.in_rounds(supergame_first_round, player.round_number) for other in player.get_others_in_group()]

<<<<<<< HEAD
# Get opponent player id
=======
def get_supergroup_previous_others(player: Player):
    supergame_first_round = player.session.vars['super_games_start_rounds'][player.subsession.curr_super_game - 1]
    return [other.in_rounds(supergame_first_round, player.round_number) for other in player.get_others_in_group()]


# Record which super game players are currently in
# def get_progress(subsession:Subsession,group:Group):
#     # Get Constants attributes once for all
#     const = Constants
#     if subsession.round_number in const.super_games_start_round:
#         group.current_super_game=group.current_super_game+1

#Get opponent player id
>>>>>>> 76f2fc82ca43c03c43359a205234374fea2549a3
def other_player(player: Player):
    if player.pair_id !=0:
        return [p for p in player.get_others_in_group() if p.pair_id == player.pair_id][0]
    #get opponent player, first find other players in the same group(with pair id 0,1,2,3)
    #then get other player with same pair id
    #pair_id = player.pair_id #get player id for current player
    # print('other players in group:', player.get_others_in_group())
    # get other players with same pair ID in the same supergroup
    #return player.get_others_in_group()[player.pair_id == pair_id]
    #return player.get_others_in_group()[0]

# Set payoffs
def set_payoffs(group: Group):
    for p in group.get_players():
            set_payoff(p)

def set_payoff(player: Player):
    payoff_matrix = {
        'Action Y':
            {
                'Action Y': Constants.both_cooperate_payoff,
                'Action Z': Constants.betrayed_payoff
            },
        'Action Z':
            {
                'Action Y': Constants.betray_payoff,
                'Action Z': Constants.both_defect_payoff
            }
    }
    for p in player.group.get_players():
        if p.pair_id != 0:
            p.payoff = payoff_matrix[p.decision][other_player(p).decision]
        else:
            p.payoff = cu(17.5)



# PAGES
class Introduction(Page):
    timeout_seconds = 100

<<<<<<< HEAD
    # @staticmethod
    # def vars_for_template(player: Player):
    #     if player.pair_id == 0:
    #         others = get_supergroup_previous_others(player)
    #         print(others)
    #     return dict()
=======
    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id == 0:
            others = get_supergroup_previous_others(player)
            print(others)
        return dict()
>>>>>>> 76f2fc82ca43c03c43359a205234374fea2549a3


class Instructions1(Page):
    #instruction will be shown to players before they start the game
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id == 0:
            others = get_supergroup_previous_others(player)
            print(others)
        return dict()


class Instructions2(Page):
    @staticmethod
    def vars_for_template(player:Player):
        continuation_chance = int(round(Constants.delta * 100))
        return dict(continuation_chance=continuation_chance, die_threshold_plus_one=continuation_chance + 1, )

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Instructions3(Page):
    @staticmethod
    def vars_for_template(player:Player):
        continuation_chance = int(round(Constants.delta * 100))
        return dict(continuation_chance=continuation_chance, die_threshold_plus_one=continuation_chance + 1, )

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Decision(Page):
    form_model = 'player'
    form_fields = ['decision']

    @staticmethod
    #The decision page will not be displayed to observer
    def is_displayed(player: Player):
        return player.pair_id != 0


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs

# Show observer what active players did in the last round
class Observer_Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0

    @staticmethod
    def vars_for_template(player: Player):
        pass

# Show observer the history of decisions all 6 active players have chosen
class Observer_History(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id == 0:
            return dict(active_players_in_all_rounds =get_supergroup_previous_others(player))

class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0

    @staticmethod
    def vars_for_template(player: Player):
        me = player
        opponent = other_player(player) #TODO: How do I get the other player
        return {
            'my_decision': me.decision,
            'opponent_decision': opponent.decision,
            'same_choice': me.decision == opponent.decision,
            'both_cooperate': me.decision == "Action Y" and opponent.decision == "Action Y",
            'both_defect': me.decision == "Action Z" and opponent.decision == "Action Z",
            'i_cooperate_he_defects': me.decision == "Action Y" and opponent.decision == "Action Z",
            'i_defect_he_cooperates': me.decision == "Action Z" and opponent.decision == "Action Y",
        }


class EndRound(Page):
    pass

class End(Page):
    @staticmethod
    def is_displayed(player:Player):
        return player.session.vars['alive'] is False or player.subsession.round_number == Constants.last_round


page_sequence = [
    # Introduction,
    Instructions1,
    Instructions2,
    Instructions3,
    Decision,
    ResultsWaitPage,
    Results,
    # Observer_Results,
    Observer_History,
    # EndRound,
    # End
]