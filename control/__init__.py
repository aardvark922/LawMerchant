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
    summary_template ='control/summary.html'
    players_per_group = None
    num_super_games = 5
    delta = 0.90  # discount factor equals to 0.90

    time_limit = 60 * 20
    time_limit_seconds = 60 * 20

    last_rounds = [10, 40, 70]
    last_round = 70

    # generate a list of supergame lengths

    # super_game_duration = list(np.random.geometric(p=(1 - delta), size=num_super_games))
    # super_game_duration = [int(s) for s in super_game_duration]

    #TODO: can I implement the following without using numpy?
    #TODO: how to implement block random termination?
    # super_game_duration = list(np.random.geometric(p=(1 - delta), size=num_super_games))
    # super_game_duration = [int(s) for s in super_game_duration]
    #TODO: seems that delta in the last line could not be recognized by python or otree?


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
    cycle_round_number = models.IntegerField(initial=1)

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

        num_rounds_tot = sum(super_games_duration)
        if num_rounds_tot > const.num_rounds:
            raise ValueError('Oooops, super games are longer than the num_rounds in Constants')

    curr_round = subsession.round_number
    for i, start in enumerate(subsession.session.vars['super_games_start_rounds']):
        if curr_round == start:
            subsession.curr_super_game = i + 1
            break
        else:
            print(curr_round)
            subsession.curr_super_game = subsession.in_round(curr_round-1).curr_super_game

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

# Get opponent player id
def get_supergroup_previous_others(player: Player):
    supergame_first_round = player.session.vars['super_games_start_rounds'][player.subsession.curr_super_game - 1]
    return [other.in_rounds(supergame_first_round, player.round_number) for other in player.get_others_in_group()]


def get_supergroup_round_results(player: Player):
    others = player.get_others_in_group()
    round_results = []
    for o in others:
        partner = other_player(o)
        result = dict(id=o.id_in_group, decision=o.decision, payoff=o.payoff, partner_id=partner.id_in_group,
                      partner_decision=partner.decision, partner_payoff=partner.payoff)
        round_results.append(result)
    return round_results

def get_previous_others(player: Player):
    supergame_first_round = player.session.vars['super_games_start_rounds'][player.subsession.curr_super_game - 1]
    previous_mes= player.in_rounds(supergame_first_round, player.round_number-1)
    summary_history = []
    for m in previous_mes:
        partner = other_player(m)
        #TODO: not sure the following line
        m.cycle_round_number = m.round_number -m.session.vars['super_games_start_rounds'][m.subsession.curr_super_game - 1]+1
        summary = dict(round_number=m.cycle_round_number ,
                       decision=m.decision,
                       partner_decision=partner.decision)
        summary_history.append(summary)
    return summary_history

def get_cycle_earning(player:Player):
    supergame_first_round = player.session.vars['super_games_start_rounds'][player.subsession.curr_super_game - 1]
    previous_mes = player.in_rounds(supergame_first_round, player.round_number - 1)
    earning=[]
    for m in previous_mes:
        payoff = m.payoff
        earning.append(payoff)
    cycle_earning = sum(earning)
    return cycle_earning


#Get opponent player id
def other_player(player: Player):
    if player.pair_id !=0:
        return [p for p in player.get_others_in_group() if p.pair_id == player.pair_id][0]


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



class Instructions1(Page):
    #instruction will be shown to players before they start the game
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1



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

class AssignRole(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.session.vars['super_games_start_rounds'][player.subsession.curr_super_game - 1]

class Decision(Page):
    form_model = 'player'
    form_fields = ['decision']

    @staticmethod
    #The decision page will not be displayed to observer
    def is_displayed(player: Player):
        return player.pair_id != 0

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id != 0:
            return dict(past_players= get_previous_others(player))
                        # cycle_round_number = player.cycle_round_number)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


# Show observer what active players did in the last round
class ObserverResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id == 0:
            # print(get_supergroup_round_results(player))
            return dict(active_players_round_results=get_supergroup_round_results(player),
                        cycle_round_number = player.round_number -player.session.vars['super_games_start_rounds'][player.subsession.curr_super_game - 1]+1)

# Show observer the history of decisions all 6 active players have chosen
class ObserverHistory(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id == 0:
            return dict(active_players_in_all_rounds=get_supergroup_previous_others(player),
                        cycle_round_number = player.round_number -player.session.vars['super_games_start_rounds'][player.subsession.curr_super_game - 1]+1,
                        start_round=player.session.vars['super_games_start_rounds'][player.subsession.curr_super_game - 1])


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
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id != 0:
            continuation_chance = int(round(Constants.delta * 100))
            if player.subsession.round_number in player.session.vars['super_games_end_rounds']:
                dieroll = random.randint(continuation_chance + 1, 100)
            else:
                dieroll = random.randint(1, continuation_chance)
            return dict(dieroll=dieroll, continuation_chance=continuation_chance,
                        die_threshold_plus_one=continuation_chance + 1, )
            # print(get_supergroup_round_results(player))

class EndCycle(Page):
    @staticmethod
    def is_displayed(player:Player):
        return player.round_number == player.session.vars['super_games_end_rounds'][player.subsession.curr_super_game - 1]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(earning_cycle=get_cycle_earning(player))



class End(Page):
    @staticmethod
    def is_displayed(player:Player):
        return player.session.vars['alive'] is False or player.subsession.round_number == Constants.last_round


page_sequence = [
    # Introduction,
    Instructions1,
    Instructions2,
    Instructions3,
    # Quiz,
    AssignRole,
    Decision,
    ResultsWaitPage,
    Results,
    ObserverResults,
    ObserverHistory,
    EndRound,
    EndCycle,
    # End
]