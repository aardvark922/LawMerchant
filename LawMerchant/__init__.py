from otree.api import *
import numpy as np
import time
import random

c = Currency

doc = """
This is an indefinitely repeated Prisoner's Dilemma with random rematching every period.
"""


class Constants(BaseConstants):
    name_in_url = 'LM_1'
    instructions_template = 'LawMerchant/instructions.html'
    summary_template = 'LawMerchant/summary.html'
    players_per_group = None
    num_super_games = 2  # 5 in experiment
    delta = 0.5  # discount factor equals to 0.90 in experiment

    time_limit = 60 * 20
    time_limit_seconds = 60 * 20

    num_rounds = 100  # sum(super_game_duration)

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

    # payoff for observer
    observer_payoff = cu(18)
    # cost of Query in stage 1
    query_cost = cu(3)
    # cost of Report in stage 3
    report_cost = cu(3)
    # cost of pay the fine in stage 5
    fine = cu(20)

    true_false_choices = [(1, 'True'), (0, 'False')]
    yes_no_choices = [(1, 'Yes'), (0, 'No')]
    record_options = [(1, 'unpaid fine'), (0, 'no unpaid fine')]


class Subsession(BaseSubsession):
    curr_super_game = models.IntegerField(initial=0)
    dishonesty = models.BooleanField()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pair_id = models.IntegerField(initial=0)
    # TODO comprehenstion test questions for two treatments
    quiz1 = models.BooleanField(
        label='1. If you are the observer in current cycle, '
              'you will be an active participant in the next cycle for sure.',
        choices=Constants.true_false_choices)
    quiz2 = models.IntegerField(label='2.  If you are an active player in current cycle, '
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
    # stage 0 bribery decision
    bribery = models.CurrencyField(
        initial=0,
        label='''How much do you want to request from this active participants?''',
        min=0,
        max=Constants.betray_payoff
    )
    # stage 1 query decision
    query = models.BooleanField(
        choices=Constants.yes_no_choices,
        label=f"Do you want to spend {Constants.query_cost} to know whether your match has unpaid fine in the past?",
    )
    # stage 2 PD decision
    decision = models.StringField(
        initial='NA',
        choices=[['Action Y', 'Action Y'], ['Action Z', 'Action Z']],
        label="""This player's decision""",
        widget=widgets.RadioSelect
    )
    # stage 3 report decision
    report = models.BooleanField(
        choices=Constants.yes_no_choices,
        initial=False,
        label=f"Do you want to spend {Constants.report_cost} to report your partner to the observer?",
    )
    # stage 5 pay fine decision
    payfine = models.BooleanField(
        choices=Constants.yes_no_choices,
        initial=False,
        label=f"Do you want to give {Constants.fine} to your match?",
        widget=widgets.RadioSelect
    )
    receivefine= models.BooleanField(initial=False)

    record = models.StringField(
        initial='no unpaid fine',
        choices=Constants.record_options,
        widget=widgets.RadioSelect
    )
    cycle_round_number = models.IntegerField(initial=1)
    pd_payoff = models.IntegerField(initial=0)


# FUNCTIONS
def creating_session(subsession: Subsession):
    # generate treatment code of current session
    dishonesty = subsession.session.config['dishonesty']
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
        print('supergame duration:', super_games_duration)
        # subsession.session.vars['super_games_end_rounds'] = list(accumulate(super_games_duration))
        subsession.session.vars['super_games_end_rounds'] = [sum(super_games_duration[:i + 1]) for i in
                                                             range(len(super_games_duration))]
        print('supergames end at rounds:', subsession.session.vars['super_games_end_rounds'])
        # subsession.session.vars['super_games_start_rounds'] = [1] + [r + 1 for r in
        #                                                              subsession.session.vars['super_games_end_rounds'][
        #                                                              1:]]
        subsession.session.vars['super_games_start_rounds'] = [sum(([1] + super_games_duration)[:i + 1]) for i in
                                                               range(len(super_games_duration))]
        print('supergames start at rounds:', subsession.session.vars['super_games_start_rounds'])

        num_rounds_tot = sum(super_games_duration)
        if num_rounds_tot > const.num_rounds:
            raise ValueError('Oooops, super games are longer than the num_rounds in Constants')

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
    group_history = []
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
        result = dict(id=o.id_in_group, decision=o.decision, payoff=o.payoff, record=o.record, query=o.query,
                      report=o.report, partner_id=partner.id_in_group, partner_decision=partner.decision,
                      partner_payoff=partner.payoff, partner_record=partner.record, partner_query=partner.query,
                      partner_report=partner.report)
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
        cycle_earning = player.payoff
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


# Set payoffs for group in stage 2
def pd_set_payoffs(group: Group):
    for p in group.get_players():
        pd_set_payoff(p)


def pd_set_payoff(player: Player):
    #Get payoff for a player in Stage 2
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

def round_set_payoffs(group:Group):
    for p in group.get_players():
        if p.pair_id != 0:
            # print('player'+str(p.id_in_group)+'payoff from stage 2:' + str(p.payoff))
            p.payoff = p.payoff-p.query*Constants.query_cost-p.report*Constants.report_cost\
                       +p.receivefine*Constants.fine
            # print('payoff after counting stages:' + str(p.payoff))
            # print('xxxxxxxxxxxx')

        else:
            others = p.get_others_in_group()
            bribery_income=[]
            for o in others:
                bribery_income.append(o.bribery)
            p.payoff = Constants.observer_payoff + p.subsession.session.config['dishonesty']*sum(bribery_income)


# get a list of players who queried in stage 1
def get_query_list(player: Player):
    ls = []
    for p in player.get_others_in_group():
        if p.query:
            ls.append('Player ' + str(p.id_in_group))
    separator = ', '
    query_list = separator.join(ls)
    return query_list

# get a list of players who reported in stage 3
def get_report_list(player: Player):
    ls = []
    for p in player.get_others_in_group():
        if p.report:
            ls.append('Player ' + str(p.id_in_group))
    separator = ', '
    report_list = separator.join(ls)
    return report_list

# get a list of players who rejects to pay fine in stage 5
def get_reject_list(player: Player):
    ls = []
    for p in player.get_others_in_group():
        partner = other_player(p)
        if p.payfine is False and p.decision == "Action Z" and partner.decision == "Action Y":
            ls.append('Player ' + str(p.id_in_group))
    separator = ', '
    reject_list = separator.join(ls)
    return reject_list

def get_reject_id(player:Player):
    reject_id=[]
    for p in player.get_others_in_group():
        partner = other_player(p)
        if p.payfine is False and p.decision == "Action Z" and partner.decision == "Action Y":
            reject_id.append(p.id_in_group)
    return reject_id

def get_payfine_list(player:Player):
    ls=[]
    for p in player.get_others_in_group():
        if p.payfine:
            ls.append('Player ' + str(p.id_in_group))
    separator = ', '
    payfine_list = separator.join(ls)
    return payfine_list

def update_records(group:Group):
    for p in group.get_players():
        #Only active partcipants need to update record
        if p.pair_id != 0:
            update_record(p)
#TODO: something went wrong here, an invalid report now becomes a rejct of fine
def update_record(player: Player):
    #only update record if ac rejects to pay fine and the report is valid
    partner = other_player(player)
    if partner.report:
        if player.decision == "Action Z" and partner.decision == "Action Y":
            if player.payfine is False:
                player.record = 'unpaid fine'
            else:
                partner.receivefine = True
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
    form_fields = ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5']

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


class Stage0(Page):
    # Bribery request page that will only show when dishonesty= 1
    pass


class Stage1Query(Page):
    form_model = 'player'
    form_fields = ['query']

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


class S1ObWait(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0


class S1AcWait(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0

class Stage1Observer(Page):
    # The decision page will only be displayed to observer
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id == 0:
            # print(get_supergroup_round_results(player))
            return dict(active_players_round_results=get_supergroup_round_results(player),
                        cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1,
                        query_list=get_query_list(player))


class Stage1Outcome(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0

    @staticmethod
    def vars_for_template(player: Player):
        me = player
        opponent = other_player(player)
        return {
            'my_record': me.record,
            'opponent_record': opponent.record,
            'me_query': me.query,
            'partner_query': opponent.query,
            'both_query': me.query == True and opponent.query == True,
            'no_query': me.query == False and opponent.query == False,
            'i_query': me.query == True and opponent.query == False,
            'he_query': me.query == False and opponent.query == True,
            'cycle_round_number': player.round_number - player.session.vars['super_games_start_rounds'][
                player.subsession.curr_super_game - 1] + 1
        }


class Stage2Decision(Page):
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


class Stage2Results(Page):
    form_model = 'player'

    # report option will only be available to whoever queried in s1
    @staticmethod
    def get_form_fields(player):
        if player.query:
            return ['report']

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
            'me_query': me.query,
            'partner_query': opponent.query,
            'both_query': me.query == True and opponent.query == True,
            'no_query': me.query == False and opponent.query == False,
            'i_query': me.query == True and opponent.query == False,
            'he_query': me.query == False and opponent.query == True,
            'cycle_round_number': player.round_number - player.session.vars['super_games_start_rounds'][
                player.subsession.curr_super_game - 1] + 1
        }

class S3ObWait(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0

class S3AcWait(WaitPage):
    #active participants wait while observer in stage 4 makes judgement
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0


class Stage4Judge(Page):
    # The decision page will only be displayed to observer
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id == 0:
            # print(get_supergroup_round_results(player))
            return dict(active_players_round_results=get_supergroup_round_results(player),
                        cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1,
                        report_list=get_report_list(player))

class S4ObWait(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0

class S4AcWait(WaitPage):
    #active participants wait while observer in stage 4 makes judgement
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0

class Stage5Fine(Page):
    form_model = 'player'
    form_fields = ['payfine']
    #This page will only displayed to an active participant who has been reported by his match and the report is valid
    @staticmethod
    def is_displayed(player: Player):
        opponent = other_player(player)
        return player.pair_id != 0 and opponent.report == True \
               and player.decision == "Action Z" \
               and opponent.decision == "Action Y"

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id != 0:
            # print(get_supergroup_round_results(player))
            return dict(cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1,)

class S5ObWait(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0

class S5AcWait(WaitPage):
    #active participants wait while observer in stage 4 makes judgement
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0

class Stage6Update(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id == 0:
            # print(get_supergroup_round_results(player))
            return dict(active_players_round_results=get_supergroup_round_results(player),
                        cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1,
                        reject_list=get_reject_list(player), reject_id = get_reject_id(player),
                        payfine_list=get_payfine_list(player))

class RecordsWaitPage(WaitPage):
    after_all_players_arrive = update_records

class Stage2ResultsWaitPage(WaitPage):
    after_all_players_arrive = pd_set_payoffs

class RoundResultsWaitPage(WaitPage):
    after_all_players_arrive = round_set_payoffs
# Show observer what active players did in the last round

class RoundResults(Page):
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
            'cycle_round_number': player.round_number - player.session.vars['super_games_start_rounds'][
                player.subsession.curr_super_game - 1] + 1,
            'my_query':me.query,
            'query_payment': me.query*Constants.query_cost,
            'my_bribery':me.bribery,
            'my_report':me.report,
            'my_payfine':me.payfine,
            'my_receivefine':me.receivefine,
            'my_earning':me.payoff
        }


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
        return player.pair_id == 0

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id == 0:
            return dict(active_players_in_all_rounds=get_supergroup_previous_others(player),
                        cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1,
                        start_round=player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1])


class EndRound(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id != 0:
            continuation_chance = int(round(Constants.delta * 100))
            if player.subsession.round_number in player.session.vars['super_games_end_rounds']:
                # print('xxxxx  supergame ends at', player.session.vars['super_games_end_rounds'])
                # print('xxxxx  supergame starts at', player.session.vars['super_games_start_rounds'])
                # print('xxxxx  supergame duration', player.session.vars['super_games_duration'])
                dieroll = random.randint(continuation_chance + 1, 100)
            else:
                dieroll = random.randint(1, continuation_chance)
            return dict(dieroll=dieroll, continuation_chance=continuation_chance,
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
        return player.round_number == player.session.vars['super_games_end_rounds'][
            Constants.num_super_games-1]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(last_round=sum(player.session.vars['super_games_duration']),
                    conversion_rate=player.session.config['real_world_currency_per_point'],
                    participation_fee=player.session.config['participation_fee'],
                    cycle_earning_list=cycle_earning_list(player))


page_sequence = [
    # Introduction,
    # Instructions0,
    # ComprehensionTest,
    AssignRole,
    Stage1Query,
    S1ObWait,
    S1AcWait,
    Stage1Observer,
    Stage1Outcome,
    Stage2Decision,
    Stage2ResultsWaitPage,
    Stage2Results,
    S3ObWait,
    S3AcWait,
    Stage4Judge,
    S4ObWait,
    S4AcWait,
    Stage5Fine,
    RecordsWaitPage,
    S5ObWait,
    Stage6Update,
    RoundResultsWaitPage,
    RoundResults,
    # ObserverResults,
    # ObserverHistory,
     EndRound,
     EndCycle,
     End
]
