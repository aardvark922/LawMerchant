from otree.api import *
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
    num_super_games = 5  # 5 in experiment
    delta = 0.9  # discount factor equals to 0.90 in experiment

    time_limit = 60 * 20
    time_limit_seconds = 60 * 20

    # pre-draw random sequence of supergame for all sessions
    supergame_duration=[10,3,21,10,12]
    ##for demo testing
    # supergame_duration =[2,1,3,1,1]
    ##for app building
    # supergame_duration = [1]

    num_rounds = sum(supergame_duration)  # sum(super_game_duration)
    last_round= sum(supergame_duration)

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
    # cost of Query in stage 1
    query_cost = cu(3)
    # cost of Report in stage 3
    report_cost = cu(3)
    # cost of pay the fine in stage 5
    fine = cu(20)
    #payment observer receives per query
    query_payment = cu(1)

    true_false_choices = [(1, 'True'), (0, 'False')]
    yes_no_choices = [(1, 'Yes'), (0, 'No')]
    record_options = [(1, 'Bad'), (0, 'Good')]
    bribery_options = [0,5,10,15,20]
    numbers = [1, 2, 3, 4]


class Subsession(BaseSubsession):
    curr_super_game = models.IntegerField(initial=0)
    last_round=models.IntegerField()
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
    quiz6 = models.BooleanField(
        label="6. If you are an active player in current cycle, "
              "you can report to the observer even if you didn’t ask for a statement about my match.",
        choices=Constants.true_false_choices
    )
    quiz7 = models.BooleanField(
        label="7. If you are an active player in current cycle, if you reject to pay a fine, "
              "your record will become Bad for the remainder of this cycle.",
        choices=Constants.true_false_choices
    )
    quiz8 = models.BooleanField(
        label="8. If you are an active player in current cycle, "
              "if you reject to give the requested number of points to the observer, your record will become Bad.",
        choices=Constants.true_false_choices
    )
    quiz9 = models.BooleanField(
        label=f"9. If you are the observer in current cycle, "
              f"your sources of earning in each round are only a flat rate of {Constants.observer_payoff} and the payment from queries.",
        choices=Constants.true_false_choices
    )
    quiz10 = models.BooleanField(
        label="10. If you are the observer in current cycle, "
              "and if an active participant accepts to pay the fine, you will change his/her record to “Bad”.",
        choices=Constants.true_false_choices
    )
    # stage 0 bribery decision
    #Observer decides whether to request any active participants.
    bribery1 = models.IntegerField(
        initial=0,
        label='''How many points do you want to request from player 1?''',
        choices=Constants.bribery_options,
        widget=widgets.RadioSelectHorizontal
    )
    bribery2 = models.IntegerField(
        initial=0,
        label='''How many points do you want to request from player 2?''',
        choices=Constants.bribery_options,
        widget=widgets.RadioSelectHorizontal
    )
    bribery3 = models.IntegerField(
        initial=0,
        label='''How many points do you want to request from player 3?''',
        choices=Constants.bribery_options,
        widget=widgets.RadioSelectHorizontal
    )
    bribery4 = models.IntegerField(
        initial=0,
        label='''How many points do you want to request from player 4?''',
        choices=Constants.bribery_options,
        widget=widgets.RadioSelectHorizontal
    )
    # bribery5 = models.CurrencyField(
    #     initial=0,
    #     label='''How much do you want to request from player 5?''',
    #     min=0,
    #     max=Constants.betray_payoff
    # )
    # bribery6 = models.CurrencyField(
    #     initial=0,
    #     label='''How much do you want to request from player 6?''',
    #     min=0,
    #     max=Constants.betray_payoff
    # )#Whoever receives request from ob decides whether to accept it
    bribery = models.BooleanField(
        choices=Constants.yes_no_choices,
        initial=False,
        label="Do you want to give the requested amount to the observer ?",
    )
    #the amount of bribery a player give the observer
    bribery_requested= models.CurrencyField(initial=0,)
    # stage 1 query decision
    query = models.BooleanField(
        choices=Constants.yes_no_choices,
        label=f"Do you want to spend {Constants.query_cost} to receive a statement about the record of your match?",
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
        label=f"Do you want to spend {Constants.report_cost} to report that your are unsatisfied with your match to the observer?",
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
        initial='Good',
        choices=Constants.record_options,
        widget=widgets.RadioSelect
    )
    cycle_round_number = models.IntegerField(initial=1)
    pd_payoff = models.IntegerField(initial=0)
    guilty = models.BooleanField(initial=False)
    dieroll = models.IntegerField(min=1, max=100)


# FUNCTIONS
def creating_session(subsession: Subsession):
    # generate treatment code of current session
    subsession.dishonesty = subsession.session.config['dishonesty']
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
        # print('supergame duration:', super_games_duration)
        # subsession.session.vars['super_games_end_rounds'] = [sum(super_games_duration[:i + 1]) for i in
        #                                                      range(len(super_games_duration))]
        #
        # subsession.session.vars['last_round'] = subsession.session.vars['super_games_end_rounds'][const.num_super_games-1]
        # subsession.last_round= subsession.session.vars['last_round']
        # print('supergames end at rounds:', subsession.session.vars['super_games_end_rounds'])
        # print('the last round of the experiment is:', subsession.session.vars['last_round'])
        # subsession.session.vars['super_games_start_rounds'] = [sum(([1] + super_games_duration)[:i + 1]) for i in
        #                                                        range(len(super_games_duration))]
        # print('supergames start at rounds:', subsession.session.vars['super_games_start_rounds'])
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

    subsession.session.vars['last_round'] = subsession.session.vars['super_games_end_rounds'][const.num_super_games - 1]
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


def get_supergroup_round_results(player: Player):
    others = player.get_others_in_group()
    round_results = []
    for o in others:
        partner = other_player(o)
        result = dict(id=o.id_in_group, decision=o.decision, payoff=o.payoff, record=o.record, query=o.query, partner_id=partner.id_in_group, partner_decision=partner.decision,
                          partner_payoff=partner.payoff, partner_record=partner.record, partner_query=partner.query,)
        round_results.append(result)
    return round_results

def get_supergroup_query_results(player: Player):
    others = player.get_others_in_group()
    query_results = []
    for o in others:
        partner = other_player(o)
        result = dict(id=o.id_in_group, payoff=o.payoff, record=o.record, bribery_request=o.bribery_requested,
                      bribery=o.bribery,query=o.query, partner_id=partner.id_in_group,
                      partner_payoff=partner.payoff, partner_bribery_request=partner.bribery_requested,
                      partner_bribery=partner.bribery,partner_record=partner.record, partner_query=partner.query)
        query_results.append(result)
    return query_results

def get_supergroup_record_results(player: Player):
    others = player.get_others_in_group()
    record_results = []
    for o in others:
        partner = other_player(o)
        result = dict(id=o.id_in_group, record=o.record, partner_id=partner.id_in_group, partner_record=partner.record)
        record_results.append(result)
    return record_results

def get_supergroup_report_results(player: Player):
    others = get_report_player(player)
    report_results = []
    for o in others:
        partner = other_player(o)
        if o.report:
            result = dict(id=o.id_in_group, decision=o.decision, partner_id=partner.id_in_group,
                      partner_decision=partner.decision)
            report_results.append(result)
    return report_results

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

def get_observer(player:Player):
    if player.pair_id != 0:
        observer = [p for p in player.get_others_in_group() if p.pair_id == 0][0]

    else:
        observer = player
    return observer

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
            p.payoff = p.payoff-p.bribery*p.bribery_requested -p.query*Constants.query_cost-p.report*Constants.report_cost\
                       -p.payfine*Constants.fine+p.receivefine*Constants.fine
            # print('payoff after counting stages:' + str(p.payoff))
            # print('xxxxxxxxxxxx')

        else:
            #the second half only counts when dishonesty == 1
            p.payoff = Constants.observer_payoff +\
                       p.subsession.session.config['dishonesty']*(Constants.query_payment*len(get_query_player(p))+ get_bribery_income(p))
#roll a die with the same number of entire group
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
    round_set_payoffs(group)

def get_bribery_income(player:Player):
    if player.pair_id == 0:
        others = player.get_others_in_group()
        bribery_income = []
        for o in others:
            bribery_income.append(o.bribery * o.bribery_requested)
        bribery_earning = sum(bribery_income)
        # print('bribery income is')
        # print(bribery_earning)
    return bribery_earning

def get_bribery_amount(player:Player):
    if player.pair_id !=0:
        field_name = 'bribery{}'.format(player.id_in_group)
        observer = get_observer(player)
        bribery_amount = cu(getattr(observer, field_name))
    return bribery_amount

def get_bribery_amounts(group:Group):
    for p in group.get_players():
        if p.pair_id != 0:
            p.bribery_requested = get_bribery_amount(p)

# get a string list of players who refused to pay bribery in stage 0 eg. [player 1, player3]
def get_refuse_bribery_list(player: Player):
    ls = []
    for p in player.get_others_in_group():
        if p.bribery_requested != 0 and p.bribery is False and p.pair_id != 0:
            ls.append('Player ' + str(p.id_in_group))
    separator = ', '
    refuse_bribery_list = separator.join(ls)
    return refuse_bribery_list

# get a id list of players who queried in stage 1 eg:[2,3,5]
def get_refuse_bribery_player(player:Player):
    refuse_bribery_player = []
    for p in player.get_others_in_group():
        if p.pair_id != 0 and p.bribery is False and p.bribery_requested != 0:
            refuse_bribery_player.append(p)
    return refuse_bribery_player
# get a string list of players who queried in stage 1 eg. [player 1, player3]
def get_query_list(player: Player):
    ls = []
    for p in player.get_others_in_group():
        if p.query and p.pair_id !=0:
            ls.append('Player ' + str(p.id_in_group))
    separator = ', '
    query_list = separator.join(ls)
    return query_list

# get a id list of players who queried in stage 1 eg:[2,3,5]
def get_query_player(player:Player):
    query_player = []
    for p in player.get_others_in_group():
        if p.pair_id != 0 and p.query:
            query_player.append(p)
    return query_player

# get a string list of players who reported in stage 3 eg: [player 1, player3]
def get_report_list(player: Player):
    ls = []
    for p in get_query_player(player):
        if p.report:
            ls.append('Player ' + str(p.id_in_group))
    separator = ', '
    report_list = separator.join(ls)
    return report_list
# get a list of players who reported in stage 3 eg:[2,3,5]
def get_report_player(player:Player):
    report_player = []
    for p in get_query_player(player):
        if p.report:
            report_player.append(p)
    return report_player

# get a string list of players who rejects to pay fine in stage 5 eg. [player 1, player3]
def get_reject_list(player: Player):
    ls = []
    for o in get_report_player(player):
        #if my partner report, I will have a chance to reject
        me = other_player(o)
        if me.payfine is False and me.decision == "Action Z" and o.decision == "Action Y":
            ls.append('Player ' + str(me.id_in_group))
    separator = ', '
    reject_list = separator.join(ls)
    return reject_list

    # for p in player.get_others_in_group():
    #     partner = other_player(p)
    #     if p.payfine is False and p.decision == "Action Z" and partner.decision == "Action Y":
    #         ls.append('Player ' + str(p.id_in_group))
    # separator = ', '
    # reject_list = separator.join(ls)
    # return reject_list
# get a list of players who rejects to pay fine in stage 5
def get_reject_id(player:Player):
    reject_id=[]
    for o in get_report_player(player):
        #if my partner report, I will have a chance to reject
        me = other_player(o)
        if me.payfine is False and me.decision == "Action Z" and o.decision == "Action Y":
            reject_id.append(me.id_in_group)
    return reject_id



    # for p in player.get_others_in_group():
    #     partner = other_player(p)
    #     if p.payfine is False and p.decision == "Action Z" and partner.decision == "Action Y":
    #         reject_id.append(p.id_in_group)
    # return reject_id

def get_payfine_list(player:Player):
    ls=[]
    for p in player.get_others_in_group():
        if p.payfine:
            ls.append('Player ' + str(p.id_in_group))
    separator = ', '
    payfine_list = separator.join(ls)
    return payfine_list
def fetch_records(group:Group):
    for p in group.get_players():
        prev_p = p.in_round(p.round_number-1)
        if p.pair_id != 0:
            p.record = prev_p.record

def update_records(group:Group):
    for p in group.get_players():
        #Only active partcipants need to update record
        if p.pair_id != 0:
            update_record(p)
#TODO: something went wrong here, an invalid report now becomes a rejct of fine
def update_record(player: Player):
    #only update record if ac rejects to pay fine and the report is valid
    partner= other_player(player)
    if player.guilty:
        if not player.payfine:
            player.record = 'Bad'
        else:
            partner.receivefine = True

#judge whether the defandant is guilty
def judge_report(player:Player):
    partner = other_player(player)
    if partner.report:
        if player.decision == "Action Z" and partner.decision == "Action Y":
            player.guilty = True

def judge_reports(group:Group):
    for p in group.get_players():
        #Only active partcipants need to update record
        if p.pair_id != 0:
            judge_report(p)


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

# class Instructions1(Page):
#     # instruction will be shown to players before they start the game
#     @staticmethod
#     def is_displayed(player: Player):
#         return player.round_number == 1


class ComprehensionTest(Page):
    form_model = 'player'

    # instruction will be shown to players before they start the game
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def get_form_fields(player):
        if player.subsession.dishonesty is True:
            #comprehentions test for dishonest treatment
            return ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5','quiz6','quiz7','quiz8','quiz9','quiz10']
        else:
            return ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5']

    @staticmethod
    def error_message(player: Player, values):
        # alternatively, you could make quiz1_error_message, quiz2_error_message, etc.
        # but if you have many similar fields, this is more efficient.
        if player.subsession.dishonesty is True:
            solutions = dict(quiz1=0, quiz2=2, quiz3=0, quiz4=1, quiz5=1, quiz6=0, quiz7=1, quiz8=0, quiz9=0,quiz10=0)
        else:
            solutions = dict(quiz1=0, quiz2=2, quiz3=0, quiz4=1, quiz5=1)

        errors = {f: 'Wrong Answer. You may refer to Instructions.' for f in solutions if values[f] != solutions[f]}
        if errors:
            return errors


class AssignRole(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == player.session.vars['super_games_start_rounds'][
            player.subsession.curr_super_game - 1]



# Bribery request page that will only show when dishonesty= 1
class Stage0RequestB(Page):
    form_model = 'player'
    form_fields = ['bribery{}'.format(n) for n in Constants.numbers]

    @staticmethod
    def is_displayed(player: Player):
        return player.subsession.dishonesty is True and player.pair_id == 0 and player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1 > 1 and player.round_number< player.session.vars['last_round']+1

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id == 0:
            return dict(active_players_record_results=get_supergroup_record_results(player),
                        cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1)

#Active participants decides whether to give observer the compensation he requested
#Only when requested by observer will a player have to decide
class Stage0Bribery(Page):
    form_model = 'player'
    form_fields = ['bribery']

    @staticmethod
    def is_displayed(player: Player):
        return player.bribery_requested != 0 and player.round_number< player.session.vars['last_round']+1

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id != 0:
            return dict(cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                                player.subsession.curr_super_game - 1] + 1,
                        bribery_amount=player.bribery_requested)

class BriberyResultsWait(WaitPage):
    after_all_players_arrive = get_bribery_amounts

    @staticmethod
    def is_displayed(player: Player):
        return player.subsession.dishonesty is True and player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1 > 1 and player.round_number< player.session.vars['last_round']+1

class S0ObWait(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0 and player.subsession.dishonesty is True and player.round_number< player.session.vars['last_round']+1


class S0AcWait(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0 and player.round_number< player.session.vars['last_round']+1



class Stage1Query(Page):
    form_model = 'player'
    form_fields = ['query']

    @staticmethod
    # The decision page will not be displayed to observer
    def is_displayed(player: Player):
        return player.pair_id != 0 and player.round_number< player.session.vars['last_round']+1

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id != 0:
            return dict(past_players=get_previous_others(player),
                        cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1)


class S1ObWait(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0 and player.round_number< player.session.vars['last_round']+1


class S1AcWait(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0 and player.round_number< player.session.vars['last_round']+1

class Stage1Observer(Page):
    # The decision page will only be displayed to observer
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0 and player.round_number< player.session.vars['last_round']+1

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id == 0:
            # print(get_supergroup_round_results(player))
            return dict(active_players_query_results=get_supergroup_query_results(player),
                        cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1,
                        query_list=get_query_list(player), refuse_bribery_list= get_refuse_bribery_list(player),
                        refuse_bribery_player=get_refuse_bribery_player(player))


class Stage1Outcome(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0 and player.round_number< player.session.vars['last_round']+1

    @staticmethod
    def vars_for_template(player: Player):
        me = player
        opponent = other_player(player)
        return {
            'my_record': me.record,
            'opponent_record': opponent.record,
            'opponent_refuse_bribery': opponent.bribery_requested != 0 and opponent.bribery == False,
            'i_refuse_bribery': me.bribery == False and me.bribery_requested != 0,
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
        return player.pair_id != 0 and player.round_number< player.session.vars['last_round']+1

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
        if player.query and player.decision == "Action Y" and other_player(player).decision == "Action Z":
            return ['report']

    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0 and player.round_number< player.session.vars['last_round']+1

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
        return player.pair_id == 0 and player.round_number< player.session.vars['last_round']+1

class S3AcWait(WaitPage):
    #active participants wait while observer in stage 4 makes judgement
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0 and player.round_number< player.session.vars['last_round']+1


class Stage4Judge(Page):
    # The decision page will only be displayed to observer
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0 and player.round_number< player.session.vars['last_round']+1

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id == 0:
            # print(get_supergroup_round_results(player))
            return dict(active_players_report_results=get_supergroup_report_results(player),
                        active_players_round_results=get_supergroup_round_results(player),
                        cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1,
                        report_list=get_report_list(player))

class S4ObWait(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0 and player.round_number< player.session.vars['last_round']+1

class S4AcWait(WaitPage):
    #active participants wait while observer in stage 4 makes judgement
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0 and player.round_number< player.session.vars['last_round']+1

class Stage5Fine(Page):
    form_model = 'player'
    form_fields = ['payfine']
    #This page will only displayed to an active participant who has been reported by his match and the report is valid
    @staticmethod
    def is_displayed(player: Player):
        return player.guilty and player.round_number< player.session.vars['last_round']+1

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id != 0:
            # print(get_supergroup_round_results(player))
            return dict(cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1,)

class S5ObWait(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0 and player.round_number< player.session.vars['last_round']+1

class S5AcWait(WaitPage):
    #active participants wait while observer in stage 4 makes judgement
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0 and player.round_number< player.session.vars['last_round']+1

class Stage6Update(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0 and player.round_number< player.session.vars['last_round']+1

    @staticmethod
    def vars_for_template(player: Player):
        if player.pair_id == 0:
            # print(get_supergroup_round_results(player))
            return dict(active_players_round_results=get_supergroup_round_results(player),
                        cycle_round_number=player.round_number - player.session.vars['super_games_start_rounds'][
                            player.subsession.curr_super_game - 1] + 1,
                        reject_list=get_reject_list(player), reject_id = get_reject_id(player),
                        payfine_list=get_payfine_list(player))

class FetchRecords(WaitPage):
    #fetch player's record from last round and is only displayed on and after round 2
    after_all_players_arrive = fetch_records

    @staticmethod
    def is_displayed(player: Player):

        return player.round_number - player.session.vars['super_games_start_rounds'][
                player.subsession.curr_super_game - 1] + 1 != 1 and player.round_number< player.session.vars['last_round']+1

class RecordsWaitPage(WaitPage):
    after_all_players_arrive = update_records
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number < player.session.vars['last_round'] + 1

class Stage2ResultsWaitPage(WaitPage):
    after_all_players_arrive = pd_set_payoffs

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number < player.session.vars['last_round'] + 1


class JudgeWaitPage(WaitPage):
    after_all_players_arrive = judge_reports

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number < player.session.vars['last_round'] + 1


class RoundResultsWaitPage(WaitPage):
    after_all_players_arrive = round_payoff_and_roll_die

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number < player.session.vars['last_round'] + 1

# Set payoff for this round and at mean time roll a die

class RoundResultsAc(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id != 0 and player.round_number< player.session.vars['last_round']+1

    @staticmethod
    def vars_for_template(player: Player):
        continuation_chance = int(round(Constants.delta * 100))
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
            'my_query':me.query,
            'query_payment': me.query*Constants.query_cost,
            'my_bribery':me.bribery,
            'my_paidbribery':me.bribery_requested,
            'my_report':me.report,
            'my_payfine':me.payfine,
            'my_receivefine':me.receivefine,
            'my_earning':me.payoff,
            'dieroll':player.dieroll,
            'continuation_chance': continuation_chance,
            'die_threshold_plus_one': continuation_chance + 1,
            'cycle_round_number': player.round_number - player.session.vars['super_games_start_rounds'][
                player.subsession.curr_super_game - 1] + 1
        }
class RoundResultsOb(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.pair_id == 0 and player.round_number< player.session.vars['last_round']+1
    @staticmethod
    def vars_for_template(player: Player):
        continuation_chance = int(round(Constants.delta * 100))
        return {'receive_bribery': get_bribery_income(player) != 0,
                'bribery_income': get_bribery_income(player),
                'cycle_round_number': player.round_number - player.session.vars['super_games_start_rounds'][
                    player.subsession.curr_super_game - 1] + 1,
                'my_earning': player.payoff,
                'query_list': get_query_list(player),
                'query_income': Constants.query_payment*len(get_query_player(player)),
                'dieroll': player.dieroll,
                'continuation_chance': continuation_chance,
                'die_threshold_plus_one': continuation_chance + 1,
                }
#ac and ob would see the same end round outcome
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
            player.subsession.curr_super_game - 1] and player.round_number < player.session.vars['last_round'] + 1

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
        return dict(last_round=sum(player.session.vars['super_games_duration']),
                    conversion_rate=player.session.config['real_world_currency_per_point'],
                    participation_fee=player.session.config['participation_fee'],
                    cycle_earning_list=cycle_earning_list(player),
                    cycle_earning=player.payoff,
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
    # Instructions1,
    # ComprehensionTest,
    AssignRole,
    FetchRecords,
    Stage0RequestB,
    BriberyResultsWait,
    Stage0Bribery,
    Stage1Query,
    S1ObWait,
    Stage1Observer,
    S1AcWait,
    Stage1Outcome,
    Stage2Decision,
    Stage2ResultsWaitPage,
    Stage2Results,
    JudgeWaitPage,
    Stage4Judge,
    S4ObWait,
    Stage5Fine,
    S5ObWait,
    RecordsWaitPage,
    Stage6Update,
    RoundResultsWaitPage,
    RoundResultsAc,
    RoundResultsOb,
    EndCycle,
    End
]
