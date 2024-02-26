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
from odoo.addons.payment_voucher_custom import numero_a_texto


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def get_amount_in_word(self):
        #return self.currency_id.amount_to_text(self.amount)
        return str(numero_a_texto.Numero_a_Texto(self.amount))

    def fecha_letras(self):
        m = {
            '01': 'Enero',
            "02": 'Febrero',
            "03": 'Marzo',
            "04": 'Abril',
            "05": 'Mayo',
            "06": 'Junio',
            "07": 'Julio',
            "08": 'Agosto',
            "09": 'Septiembre',
            "10": 'Octubre',
            "11": 'Noviembre',
            "12": 'Diciembre',
            }
        fecha = str(self.payment_date).split("-")
        anio =  fecha[0]
        mes =  fecha[1]
        dia = fecha[2]
        try:
            out = str(m[mes])
            date_str = "%s de %s del %s" %(dia, out, anio)
            #print dia + "-" +  out + "-" + anio
            return date_str
        except:
            raise ValueError('No es un mes')