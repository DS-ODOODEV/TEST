# -*- coding: utf-8 -*-
{
    'name': "Balance Sheet Salvador",
    'summary': """
        Custom fields for balance sheet in Salvador""",
    'description': """
        Custom fields for balance sheet in Salvador
    """,
    'license': 'AGPL-3',
    'author': 'Fernando Flores --> fflores@xetechs.com',
    'website': 'https://xetechs.odoo.com',
    'maintainer': 'Xetechs, S.A.',
    'depends': ['account', 'account_reports'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/balance_sheet_report_data.xml',
        'views/balance_sheet.xml'
    ],
    'installable': True,
    'aplication': True,
    'auto_install': False,
}
