# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def _default_tax_iva(self):
        tax_id = self.env['account.tax'].search([('id', '=', 64)], limit=1)
        return tax_id

    @api.model
    def _default_tax_ret_1(self):
        tax_id = self.env['account.tax'].search([('id', '=', 69)], limit=1)
        return tax_id
    
    @api.model
    def _default_tax_ret_5(self):
        tax_id = self.env['account.tax'].search([('id', '=', 84)], limit=1)
        return tax_id

    tax_ret_1_id = fields.Many2many('account.tax', 'rel_company_ret_1', 'tax_ret_1_id', 'company_id', string="Impuestos Retencion 1%", default=_default_tax_ret_1)
    tax_ret_5_id = fields.Many2many('account.tax', 'rel_company_ret_5', 'tax_ret_5_id', 'company_id', string="Impuestos Retencion 5%", default=_default_tax_ret_5)
    tax_iva_id = fields.Many2many('account.tax', 'rel_company_iva', 'tax_iva_id', 'company_id', string="Impuestos IVA", default=_default_tax_iva)
    account_ret_5_id = fields.Many2many('account.account', 'rel_company_account_ret_5', 'account_ret_5_id', 'company_id', string="Impuestos Retencion 5%")



ResCompany()


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tax_ret_1_id = fields.Many2many('account.tax', 'rel_company_ret_1', 'tax_ret_1_id', 'company_id', related="company_id.tax_ret_1_id", readonly=False, string="Impuestos Retencion 1%")
    tax_ret_5_id = fields.Many2many('account.tax', 'rel_company_ret_5', 'tax_ret_5_id', 'company_id', related="company_id.tax_ret_5_id", readonly=False, string="Impuestos Retencion 5%")
    tax_iva_id = fields.Many2many('account.tax', 'rel_company_iva', 'tax_iva_id', 'company_id', related="company_id.tax_iva_id", readonly=False, string="Impuestos IVA")
    account_ret_5_id = fields.Many2many('account.account', 'rel_company_account_ret_5', 'account_ret_5_id', 'company_id', related="company_id.account_ret_5_id", readonly=False, string="Impuestos Retencion 5%")

    def update_invoice_taxes(self):
        invoice_ids = self.env['account.move'].search([('type', 'in', ('out_invoice', 'out_refund', 'out_receipt'))])
        for rec in invoice_ids:
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
                rec.write({
                    'amount_tax_iva': amount_iva or 0.00,
                    'amount_tax_ret_1': amount_ret_1 or 0.00,
                    'amount_tax_ret_5': amount_ret_5 or 0.00,
                })

ResConfigSettings()