from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Demographics(Page):
    form_model = 'player'
    form_fields = ['age', 'gender', 'field_of_study', 'country', 'length_in_US', 'race', 'gpa', 'years_at_uni', 'num_exper', 
                    'pay_sig1', 'pay_sig2',  'pay_sig3',  'pay_sig4',
                    'bid_A', 'bid_B', 'bid_C', 'bid_D', 'bid_E',
                    'decision_process', 'review']

    ## this doesn't work...
    # def length_in_US_choices(self):
    #     if self.player.country == 1:
    #         choices = [[1, "N/A"]]
    #     else:
    #         choices = [[2, 'More than 5 years'],
    #             [3, '2-5 years'],
    #             [4, '1-2 years'],
    #             [5, 'Less than 1 year'],]
    #     return choices

    # def error_message(self, values):
        # print('values is', values)
        # if values["country"] == 1 and values['length_in_US'] != 1:
            # return 'If you were born in the US, you must answer \'N/A\' for the question: \'If you were not born in the US, how long have you lived in the US?\''
        # if values["country"] != 1 and values['length_in_US'] == 1:
            # return 'If you were not born in the US, you cannot answer \'N/A\' for the question: \'If you were not born in the US, how long have you lived in the US?\''

class Final(Page):
    pass

page_sequence = [
    Demographics,
    Final,
]
