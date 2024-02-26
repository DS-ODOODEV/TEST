# -*- encoding: UTF-8 -*-
##############################################################################
#
#    Odoo, XETECHS, S.A.
#    Copyright (C) 2018-Today XETECHS, S.A.
#    (<http://www.xetechs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
{
    'name': 'Personalizaciones Cheques',
    'summary': """Check""",
    'version': '1.0.',
    'description': """This is a module for add custom fields for checks""",
    'author': 'Xetechs, S.A.',
    'maintainer': 'Xetechs, S.A.',
    'support': 'Luis Aquino -> laquino@xetechs.com',
    'website': 'https://xetechs.odoo.com',
    'category': 'account',
    'depends': ['account', 'account_check_printing'],
    'license': 'AGPL-3',
    'data': [
            'views/account_payment_view.xml',
            ],
    'demo': [],
    'sequence': 1,
    'installable': True,
    'auto_install': False,
    'application': True,

}
