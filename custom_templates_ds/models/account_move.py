# -*- coding: utf-8 -*-


from odoo import fields, models, api
from datetime import date, datetime
import locale

class AccountMove(models.Model):
    _inherit = 'account.move'

    date_spanish=fields.Char('Fecha completa', required=False,copy=False,compute="_convert_spanish_date")
    #locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    @api.depends('invoice_date')
    def _convert_spanish_date(self):
        for rec in self:
            if rec.invoice_date != 0:
                rec.date_spanish = rec.invoice_date.strftime("%A %d %B %Y")
            else:
                rec.date_spanish = 0



AccountMove()