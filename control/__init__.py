from otree.api import *
import time
import random

c = Currency

doc = """
This is an indefinitely repeated Prisoner's Dilemma with random rematching every period.
"""


class Constants(BaseConstants):
    name_in_url = 'LM_0'
    # instructions_template = 'control/instructions.html'
    summary_template = 'control/summary.html'
    players_per_group = None
    num_super_games = 5
    delta = 0.90  # discount factor equals to 0.90

    time_limit = 60 * 20
    time_limit_seconds = 60 * 20

    supergame_duration = [10, 3, 21, 10, 12]
    #for app building
    # supergame_duration = [1,2]

    num_rounds = sum(supergame_duration)
    last_round = sum(supergame_duration)  # sum(super_game_duration)

    # Nested groups parameters
    super_group_size = 5
    observer_num = 1
    group_size = 2

    # parameters for PD matrix
    # payoff if 1 player defects and the other cooperates""",
    betray_payoff = cu(30)
    betrayed_payoff = cu(5)

    # payoff if both players cooperate or both defect
    both_cooperate_payoff = cu(25)
    both_defect_payoff = cu(10)

    # payoff for observer
    observer_payoff = cu(18)

    true_false_choices = [(1, 'True'), (0, 'False')]


class Subsession(BaseSubsession):
    curr_super_game = models.IntegerField(initial=0)
    last_round = models.IntegerField()


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
    quiz1 = models.BooleanField(
        label='1. If you are the observer in current cycle, '
              'you will be an active participant in the next cycle for sure.',
        choices=Constants.true_false_choices)
    quiz2 = models.IntegerField(label='2.  If you are an active player in current cycle, '
                                     'when you choose Y and your partner chooses Z. What is your payoff?',
                                choices=[(1,"25"),(2,"5"),(3,"10"),(4,"30")],
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
    dieroll = models.IntegerField(min=1, max=100)

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
        ## generate supergame duration when creating session
        # super_games_duration = list()
        # for s in range(const.num_super_games):
        #     n = 0
        #     while True:
        #         n += 1
        #         next_round = choices([True, False], weights=[const.delta, 1 - const.delta], k=1)[0]
        #         if not next_round:
        #             break
        #     super_games_duration.append(n)
        #
        # subsession.session.vars['super_games_duration'] = super_games_duration
        # print('supergame duration:',super_games_duration)
        # # subsession.session.vars['super_games_end_rounds'] = list(accumulate(super_games_duration))
        # subsession.session.vars['super_games_end_rounds'] = [sum(super_games_duration[:i + 1]) for i in range(len(super_games_duration))]
        # print('supergames end at rounds:',subsession.session.vars['super_games_end_rounds'])
        # # subsession.session.vars['super_games_start_rounds'] = [1] + [r + 1 for r in
        # #                                                              subsession.session.vars['super_games_end_rounds'][
        # #                                                              1:]]
        # subsession.session.vars['super_games_start_rounds'] = [sum(([1] + super_games_duration)[:i + 1]) for i in range(len(super_games_duration))]
        # print('supergames start at rounds:',subsession.session.vars['super_games_start_rounds'])
        #
        # num_rounds_tot = sum(super_games_duration)
        # if num_rounds_tot > const.num_rounds:
        #     raise ValueError('Oooops, super games are longer than the num_rounds in Constants')
        ###Use supergame durantion drawn in advance, so that every session has the same supergame details
    super_games_duration = Constants.supergame_duration.copy()

    subsession.session.vars['super_games_duration'] = super_games_duration
    print('supergame duration:', super_games_duration)

    subsession.session.vars['super_games_end_rounds'] = [sum(super_games_duration[:i + 1]) for i in
                                                             range(len(super_games_duration))]

    subsession.session.vars['last_round'] = subsession.session.vars['super_games_end_rounds'][
            const.num_super_games - 1]
    subsession.last_round = Constants.last_round
    print('supergames end at rounds:', subsession.session.vars['super_games_end_rounds'])
    print('the last round of the experiment is:', subsession.session.vars['last_round'])

    subsession.session.vars['super_games_start_rounds'] = [sum(([1] + super_games_duration)[:i + 1]) for i in
                                                               range(len(super_games_duration))]
    print('supergames start at rounds:', subsession.session.vars['super_games_start_rounds'])

    curr_round = subsession.round_number
    for i, start in enumerate(subsession.session.vars['super_games_start_rounds']):
        if curr_round == start:
            subsession.curr_super_game = i + 1
            break
        else:
            # print(curr_round)
            subsession.curr_super_game = subsession.in_round(curr_round - 1).curr_super_game

    # If the current round is the first round of a super game, then set the supergroups
    if subsession.round_number in subsession.session.vars['super_games_start_rounds']:
        # Get all players in the session and in the current round
        ps = subsession.get_players()
        # Apply in-place permutation
        shuffle(ps)
        # Set list of list, where each sublist is a supergroup
        super_groups = [ps[n:n + const.super_group_size] for n in range(0, len(ps), const.super_group_size)]
        # print('current round number:', subsession.round_number)
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
    others = player.get_others_in_group()
    group_history=[]
    for o in others:
        other_history = []
        previous_others = o.in_rounds(supergame_first_round, player.round_number)
        for p in previous_others:
            p.cycle_round_number = p.round_number - p.session.vars['super_games_start_rounds'][
                p.subsession.curr_super_game - 1] + 1
            history = dict(round_number=p.cycle_round_number,
                           decision=p.decision, id=p.id_in_group)
            other_history.append(history)
        group_history.append(other_history)
    return group_history
    # return [other.in_rounds(supergame_first_round, player.round_number) for other in player.get_others_in_group()]


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
    previous_mes = player.in_rounds(supergame_first_round, player.round_number - 1)
    summary_history = []
    for m in previous_mes:
        partner = other_player(m)
        # TODO: not sure the following line
        m.cycle_round_number = m.round_number - m.session.vars['super_games_start_rounds'][
            m.subsession.curr_super_game - 1] + 1
        summary = dict(round_number=m.cycle_round_number,
                       decision=m.decision,
                       partner_decision=partner.decision)
        summary_history.append(summary)
    return summary_history


def get_cycle_earning(player: Player):
    supergame_first_round = player.session.vars['super_games_start_rounds'][player.subsession.curr_super_game - 1]
    if player.round_number != supergame_first_round:
        # To prevent the case when a cycle only lasts for one period
        previous_mes = player.in_rounds(supergame_first_round, player.round_number)
        earning = []
        for m in previous_mes:
            payoff = m.payoff
            earning.append(payoff)
        cycle_earning = sum(earning)
    else:
        cycle_earning=player.payoff
    return cycle_earning

def cycle_earning_list(player:Player):

    cycle_earning_list=[]
    cycle_num=1
    for c in range ( Constants.num_super_games):
        supergame_first_round = player.session.vars['super_games_start_rounds'][c]
        supergame_last_round = player.session.vars['super_games_end_rounds'][c]
        if supergame_last_round != supergame_first_round:
            # To prevent the case when a cycle only lasts for one period
            previous_mes = player.in_rounds(supergame_first_round, supergame_last_round)
            earning = []
            for m in previous_mes:
                payoff = m.payoff
                earning.append(payoff)
            cycle_tot = sum(earning)
        else:
            cycle_tot = player.in_round(supergame_first_round).payoff

        cycle_earning_summary= dict(cycle_number=cycle_num,cycle_earning= cycle_tot)
        cycle_earning_list.append(cycle_earning_summary)
        cycle_num = cycle_num+1
    return cycle_earning_list

# Get opponent player id
def other_player(player: Player):
    if player.pair_id != 0:
        return [p for p in player.get_others_in_group() if p.pair_id == player.pair_id][0]


# Set payoffs
def set_payoffs(group: Group):
    for p in group.get_players():
        set_payoff(p)
#roll a die for the whole group
def roll_die(group:Group):
    continuation_chance = int(round(Constants.delta * 100))
    dieroll_continue = random.randint(1, continuation_chance)
    dieroll_end = random.randint(continuation_chance + 1, 100)
    for p in group.get_players():
        if p.subsession.round_number in p.session.vars['super_games_end_rounds']:
            p.dieroll=dieroll_end
        else:
            p.dieroll = dieroll_continue
#call two functions at one time
def round_payoff_and_roll_die(group:Group):
    roll_die(group)
    set_payoffs(group)


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
            p.payoff = Constants.observer_payoff


# PAGES
class Introduction(Page):
    timeout_seconds = 100


class Instructions0(Page):
    # instruction will be shown to players before they start the game
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        continuation_chance = int(round(Constants.delta * 100))
        return dict(continuation_chance=continuation_chance, end_chance=100 - continuation_chance)


class ComprehensionTest(Page):
    form_model = 'player'
    form_fields = ['quiz1', 'quiz2', 'quiz3', 'quiz4','quiz5']
    # instruction will be shown to players before they start the game
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def error_message(player: Player, values):
        # alternatively, you could make quiz1_error_message, quiz2_error_message, etc.
        # but if you have many similar fields, this is more efficient.
        solutions = dict(quiz1=0, quiz2=2, quiz3=0, quiz4=1, quiz5=1)

        errors = {f: 'Wrong Answer. You may refer to Instructions.' for f in solutions if values[f] != solutions[f]}
        if errors:
            return errors


class AssignRole(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.session.vars['super_games_start_rounds'][
            player.subsession.curr_super_game - 1]


class Decision(Page):
    form_model = 'player'
    form_fields = ['decision']

    @staticmethod
    # The decision page will not be displayed to observer
    def is_displayed(player: Player):
        return player.pair_id != 0

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id != 0:
            return dict(past_players=get_previous_others(player),
                        cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = round_payoff_and_roll_die


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
                        cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1)


# Show observer the history of decisions all 6 active players have chosen
class ObserverHistory(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0 and player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1!=1

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id == 0:
            return dict(active_players_in_all_rounds=get_supergroup_previous_others(player),
                        cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1,
                        start_round=player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1])


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0

    @staticmethod
    def vars_for_template(player: Player):
        me = player
        opponent = other_player(player)  # TODO: How do I get the other player
        return {
            'my_decision': me.decision,
            'opponent_decision': opponent.decision,
            'same_choice': me.decision == opponent.decision,
            'both_cooperate': me.decision == "Action Y" and opponent.decision == "Action Y",
            'both_defect': me.decision == "Action Z" and opponent.decision == "Action Z",
            'i_cooperate_he_defects': me.decision == "Action Y" and opponent.decision == "Action Z",
            'i_defect_he_cooperates': me.decision == "Action Z" and opponent.decision == "Action Y",
            'cycle_round_number':player.round_number - player.session.vars['super_games_start_rounds'][
            player.subsession.curr_super_game - 1] + 1
        }


class EndRound(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number < player.session.vars['last_round'] + 1
    @staticmethod
    def vars_for_template(player: Player):
        continuation_chance = int(round(Constants.delta * 100))
        # if player.subsession.round_number in player.session.vars['super_games_end_rounds']:
        #     dieroll = random.randint(continuation_chance + 1, 100)
        # else:
        #     dieroll = random.randint(1, continuation_chance)
        return dict(dieroll=player.dieroll, continuation_chance=continuation_chance,
                        die_threshold_plus_one=continuation_chance + 1,
                        cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1
                        )

class EndCycle(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.session.vars['super_games_end_rounds'][
            player.subsession.curr_super_game - 1]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(earning_cycle=get_cycle_earning(player))


class End(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.session.vars['last_round']

    @staticmethod
    def vars_for_template(player: Player):
        import math
        previous_mes= player.in_all_rounds()
        cycles_earning=0
        for m in previous_mes:
            payoff=m.payoff
            cycles_earning= cycles_earning+payoff
        return dict(last_round=sum(player.session.vars['super_games_duration']),
                    conversion_rate=player.session.config['real_world_currency_per_point'],
                    participation_fee=player.session.config['participation_fee'],
                    cycle_earning_list=cycle_earning_list(player),
                    cycles_earning=cycles_earning,
                    quiz_earning= player.participant.quiz_earning,
                    payment=math.ceil(player.participant.payoff_plus_participation_fee()*4)/4,
                    rounding= (player.participant.payoff_plus_participation_fee()!= math.ceil(player.participant.payoff_plus_participation_fee()*4)/4))
#jump to demographics after this page
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        if player.round_number == player.session.vars['last_round']:
            return upcoming_apps[0]


page_sequence = [
    # Introduction,
    # Instructions0,
    # ComprehensionTest,
    AssignRole,
    Decision,
    ResultsWaitPage,
    Results,
    ObserverResults,
    EndRound,
    ObserverHistory,
    EndCycle,
    End
]
