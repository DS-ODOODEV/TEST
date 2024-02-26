# -*- coding: utf-8 -*-
{
    'name': "Account Invoice Taxes Report",
    'author': "Odoo Developer",
    'website': "https://www.odoo.com",
    'category': 'Account Reports',
    'version': '13.0.0.1',
    'depends': ['base', 'account'],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_view.xml',
        'views/account_move_view.xml',
        'views/account_invoice_taxes_view.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
