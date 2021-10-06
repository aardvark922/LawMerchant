from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    cases = [
        'query_cooperate',  # players agree on an amount under the threshold
        'noquery_cooperate',
        'noquery_defect',
        'query_defect',
        'greedy_observer'  # players ask for too much so end up with nothing
    ]

    def play_round(self):

        # start
        yield AssignRole
        # for observer
        if self.case == 'greedy_observer':
            if self.player.pair_id == 0:
                yield Stage0RequestB, dict(bribery1=0, bribery2=3, bribery3=0, bribery4=5, bribery5=0, bribery6=0)
                yield Stage1Observer
                yield Stage4Judge
                yield Stage6Update
                yield RoundResultsOb

                # the observer that would requests bribery
            else:
                if self.player.bribery_requested != 0:
                    yield Stage0Bribery, dict(bribery=False)
                    # active player faces greedy observer
                    if self.case == 'query_cooperate':
                        # the player that would query, cooperate, report
                        yield Stage1Query, dict(query=True)
                        yield Stage1Outcome
                        yield Stage2Decision, dict(decision='Action Y')
                        yield Stage2Results, dict(report=False)

                    elif self.case == 'noquery_cooperate':
                        # the player that would not query but just cooperate
                        yield Stage1Query, dict(query=False)
                        yield Stage1Outcome
                        yield Stage2Decision, dict(decision='Action Y')
                        yield Stage2Results

                    elif self.case == 'noquery_defect':
                        # the player would not query and would defect and refuses to pay fine
                        yield Stage1Query, dict(query=False)
                        yield Stage1Outcome
                        yield Stage2Decision, dict(decision='Action Z')
                        yield Stage2Results
                    # yield Stage5Fine, dict(payfine=False)

                    else:
                        yield Stage1Query, dict(query=False)
                        yield Stage1Outcome
                        yield Stage2Decision, dict(decision='Action Z')
                        yield Stage2Results
                    # yield Stage5Fine, dict(payfine=True)
                yield RoundResultsAc

        else:
            if self.player.pair_id == 0:
                yield Stage0RequestB, dict(bribery1=0, bribery2=0, bribery3=0, bribery4=0, bribery5=0, bribery6=0)
                yield Stage1Observer
                yield Stage4Judge
                yield Stage6Update
                yield RoundResultsOb

            else:
                # the kind of observer that does not ask for bribery
                # for active participants
                if self.case == 'query_cooperate':
                    yield Stage1Query, dict(query=True)
                    yield Stage1Outcome
                    yield Stage2Decision, dict(decision='Action Y')
                    yield Stage2Results, dict(report=False)

                    # the player that would query, cooperate, report
                elif self.case == 'noquery_cooperate':
                    yield Stage1Query, dict(query=False)
                    yield Stage1Outcome
                    yield Stage2Decision, dict(decision='Action Y')
                    yield Stage2Results

                elif self.case == 'noquery_defect':
                    # the player would not query and would defect and refuses to pay fine
                    yield Stage1Query, dict(query=False)
                    yield Stage1Outcome
                    yield Stage2Decision, dict(decision='Action Z')
                    yield Stage2Results
                    # yield Stage5Fine, dict(payfine=False)
                else:
                    # the player would not query and would defect and pay fine
                    yield Stage0Bribery, dict(bribery=False)
                    yield Stage1Outcome
                    yield Stage2Decision, dict(decision='Action Z')
                    yield Stage2Results
                    # yield Stage5Fine, dict(payfine=True)
                yield RoundResultsAc
        yield EndRound
        if self.player.round_number == self.player.session.vars['super_games_end_rounds'][
            self.player.subsession.curr_super_game] - 1:
            yield EndCycle
