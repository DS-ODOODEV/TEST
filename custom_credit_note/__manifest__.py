# -*- coding: utf-8 -*-

{
    'name': 'Custom Credit Note -DS-',
    'version': '1.0.1',
    'author': 'Odoo Inc',
    'website': 'https://www.odoo.com', 
    'category': 'Accounting',
    'depends': ['account'],
    'summary': 'Custom Credit Note -DS-',
    'data': [
        'views/reports.xml',
        'views/custom_credit_note_tmpl.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}
