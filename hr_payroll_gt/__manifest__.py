# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Hr Payroll GT',
    'version': '1.0',
    'category': 'HR',
    'sequence': 1,
    'summary': 'Hr Payroll GT Extends',
    'description': """
Hr Payroll GT Extends
============================
    * 
""",
    'website': 'https://www.xetechs.odoo.com',
    'author': 'Luis Aquino --> laquino@xetechs.com',
    'depends': ['hr_payroll', 'hr_contract'],
    'data': [
        'security/hr_payroll_security.xml',
        'views/hr_contract_view.xml',
        'views/hr_payroll_report_views.xml',
        'data/hr_rule_data.xml',
    ],
    'installable': True,
    'application': True,
}
