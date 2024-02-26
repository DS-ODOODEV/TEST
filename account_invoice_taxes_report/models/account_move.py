# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    amount_tax_ret_1 = fields.Float('Retencion 1%', compute='_compute_invoice_taxes', store=True)
    amount_tax_ret_5 = fields.Float('Retencion 5%', compute='_compute_invoice_taxes', store=True)
    amount_tax_iva = fields.Float('IVA', compute='_compute_invoice_taxes', store=True)

    @api.depends(
        'invoice_line_ids.tax_ids', 
        'invoice_line_ids.quantity', 
        'invoice_line_ids.price_unit'
    )
    def _compute_invoice_taxes(self):
        for rec in self:
            amount_iva = amount_ret_1 = amount_ret_5 = 0.00
            for line in rec.invoice_line_ids:
                #Calculo del monto del IVA para el reporte
                reconciled_payments = rec._get_reconciled_info_JSON_values()
                for pay in reconciled_payments:
                    pay_move = pay.get('move_id', False)
                    if pay_move:
                        pay_move_id = self.env['account.move'].browse([pay_move])
                        amount_ret_5 = sum([(x.debit - x.credit) for x in pay_move_id.line_ids.filtered(lambda l: l.account_id.id in rec.company_id.account_ret_5_id.ids)])
                for tax in line.tax_ids:
                    #calculo de IVA de la factura
                    if tax.id in rec.company_id.tax_iva_id.ids:
                        tax_res = tax.compute_all(line.price_unit, rec.company_id.currency_id, line.quantity, line.product_id, rec.partner_id)
                        for t in tax_res.get('taxes', []):
                            amount_iva += t.get('amount', 0.00)
                    #Calculo de la Retencion 1%
                    if tax.id in rec.company_id.tax_ret_1_id.ids:
                        tax_res = tax.compute_all(line.price_unit, rec.company_id.currency_id, line.quantity, line.product_id, rec.partner_id)
                        for t in tax_res.get('taxes', []):
                            amount_ret_1 += t.get('amount', 0.00)
                    #Calculo de la Retencion 5%
                    #if tax.id in rec.company_id.tax_ret_5_id.ids:
                    #    tax_res = tax.compute_all(line.price_unit, rec.company_id.currency_id, line.quantity, line.product_id, rec.partner_id)
                    #    for t in tax_res.get('taxes', []):
                    #        amount_ret_5 += t.get('amount', 0.00)
            rec.update({
                'amount_tax_iva': amount_iva or 0.00,
                'amount_tax_ret_1': amount_ret_1 or 0.00,
                'amount_tax_ret_5': amount_ret_5 or 0.00,
            })


AccountMove()