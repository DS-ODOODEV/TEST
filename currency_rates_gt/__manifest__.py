# -*- encoding: UTF-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution
# Copyright (C) 2018-Today Xetechs, S.A.
# (<https://www.xetechs.com>)
#
##############################################################################

{
    "name": "Currency Rates -BANGUAT-",
    "summary": "Currency Rates -BANGUAT-",
    'description': """
Currency Rates -BANGUAT-

    """,
    'author': "Xetechs, S.A.",
    'website': "https://www.xetechs.com",
    'support': "Luis Aquino --> laquino@xetechs.com",
    "version": "1.0",
    "category": "Tools",
    "depends": ['base', 'base_setup'],
    "data": [
        'data/cron_currency.xml',
        'views/res_currency_view.xml',
        
        ],
    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'application': True,
}
