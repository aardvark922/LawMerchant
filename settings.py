from os import environ

SESSION_CONFIGS = [
    dict(
         name='control',
         app_sequence=['control'],
         num_demo_participants=14,
     ),
    dict(
         name='honest',
         app_sequence=['LawMerchant'],
         dishonesty=False,
         num_demo_participants=10,
     ),
    dict(
         name='dishonest',
         app_sequence=['LawMerchant'],
         dishonesty=True,
         num_demo_participants=10,
     ),

    # dict(
    #     name='Prisoner_Dilemma',
    #     app_sequence=['Prisoner_Dilemma'],
    #     num_demo_participants=2,
    # ),
    # dict(
    #     name='history_table',
    #     app_sequence=['history_table'],
    #     num_demo_participants=1,
    # ),
    # dict(
    #     name='show_other_players_payoffs',
    #     app_sequence=['show_other_players_payoffs'],
    #     num_demo_participants=4,
    # ),
    # dict(
    #     name='public_goods',
    #     app_sequence=['public_goods', 'payment_info'],
    #     num_demo_participants=3,
    # ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.01,
    participation_fee=5.00,
    # use_browser_bots=True,
    doc=""
)

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = [
    dict(
        name='LM',
        display_name='Law_Merchant',
        participant_label_file='_rooms/lab.txt',
        # use_secure_urls=True
    )
]
ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '5312458349911'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']
