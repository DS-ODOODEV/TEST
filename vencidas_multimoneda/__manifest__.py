# -*- coding: utf-8 -*-
{
    'name': "Reporte vencidas multimoneda",
    'summary': """
    Reporte vencidas multimoneda
    """,
    'license': 'AGPL-3',
    'author': 'Fernando Flores --> fflores@xetechs.com',
    'website': 'https://xetechs.odoo.com',
    'maintainer': 'Xetechs, S.A.',
    'depends': ['account', 'account_reports'],
    'data': [
        'security/ir.model.access.csv',
        'views/vencidas_multimoneda.xml',
        'views/vencidas_multimoneda_data.xml',
    ],
    'installable': True,
    'aplication': True,
    'auto_install': False,
}
