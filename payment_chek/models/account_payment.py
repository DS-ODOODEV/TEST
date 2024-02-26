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
from odoo import fields, models, api, _

class AccountPayment(models.Model):
	_inherit = "account.payment"
	
	other_reference = fields.Char('Ref. Cheque', required=False, help="Referencia de cheque")
	is_negociable = fields.Selection([
		('no_negociable', '*NO NEGOCIABLE*'),
		('negociable', '*NEGOCIABLE*')], 'Negociable', required=False, default='no_negociable', help="Active cualquier de las opciones para hacer el cheque *NEGOCIABLE* o *NO NEGOCIABLE*")
AccountPayment()
