# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models

import logging

_logger = logging.getLogger(__name__)

class ReportInvoiceTaxes(models.Model):
    _name = "report.invoice.taxes"
    _description = "Report Invoice Taxes"
    _rec_name = "invoice_date"
    _auto = False

    move_id = fields.Many2one('account.move', 'Factura')
    invoice_date = fields.Date('Fecha Factura')
    journal_id = fields.Many2one('account.journal', 'Diario')
    partner_id = fields.Many2one('res.partner', 'Cliente')
    company_id = fields.Many2one('res.company', 'Compañía')
    currency_id = fields.Many2one('res.currency', 'Moneda')
    amount_untaxed = fields.Monetary('Gravado')
    amount_iva = fields.Monetary('IVA')
    amount_with_iva = fields.Monetary('Subtotal + IVA')
    amount_ret_1 = fields.Monetary('Ret 1%')
    amount_ret_5 = fields.Monetary('Ret 5%')
    amount_total = fields.Monetary('Total')


    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE view %s as
                SELECT
                    row_number() OVER () AS id,
                    inv.id as move_id,
                    inv.invoice_date as invoice_date,
                    inv.journal_id as journal_id,
                    inv.partner_id as partner_id,
                    inv.company_id as company_id,
                    inv.currency_id as currency_id,
                    inv.amount_untaxed as amount_untaxed,
                    inv.amount_tax_iva as amount_iva, 
                    (inv.amount_untaxed + inv.amount_tax_iva) as amount_with_iva,
                    inv.amount_tax_ret_1 as amount_ret_1,
                    inv.amount_tax_ret_5 as amount_ret_5,
                    inv.amount_total as amount_total
                FROM account_move inv
                WHERE inv.type in ('out_invoice', 'out_refund', 'out_receipt') and inv.state not in ('draft', 'cancel')
                ORDER BY inv.invoice_date;
        """ %(self._table))

ReportInvoiceTaxes()