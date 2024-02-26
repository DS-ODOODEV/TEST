# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'CRM Customs Extends',
    'version': '1.0',
    'category': 'CRM',
    'sequence': 1,
    'summary': 'CRM Customs Extends',
    'description': """
CRM Customs Extends
============================
    * Currency to display on amounts
""",
    'website': 'https://www.xetechs.odoo.com',
    'author': 'Xetechs, S.A.',
    'suppor': 'Luis Aquino --> laquino@xetechs.com',
    'depends': ['crm'],
    "data": [
        'views/crm_view.xml',
    ],
    'installable': True,
    'application': True,
}
