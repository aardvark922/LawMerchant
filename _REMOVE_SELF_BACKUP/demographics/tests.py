from otree.api import Currency as c, currency_range
from . import pages
from ._builtin import Bot
from .models import Constants
import random


class PlayerBot(Bot):

    def play_round(self):
        cnty = "country"
        
        yield (pages.Demographics, {'age': random.randint(18,50),
                                    'gender': random.randint(1,2),
                                    'field_of_study': random.randint(1,12),
                                    'country': cnty,
                                    'length_in_US': random.randint(1,5),
                                    'race': random.randint(1,5),
                                    'gpa': random.randint(1,5),
                                    'years_at_uni': random.randint(1,5),
                                    'num_exper': random.randint(0,20),
                                    'pay_sig1': random.randint(0,100),
                                    'pay_sig2': random.randint(0,100),
                                    'pay_sig3': random.randint(0,100),
                                    'pay_sig4': random.randint(0,100),
                                    'bid_A': random.randint(0,1400),
                                    'bid_B': random.randint(0,1400),
                                    'bid_C': random.randint(0,1400),
                                    'bid_D': random.randint(0,1400),
                                    'bid_E': random.randint(0,1400),
                                    }
               )
