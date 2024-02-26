# -*- coding: utf-8 -*-

from . import models
from odoo import api, SUPERUSER_ID

def post_update_invoice_taxes(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    invoice_ids = env['account.move'].search([('type', 'in', ('out_invoice', 'out_refund', 'out_receipt'))])
    for rec in invoice_ids:
        amount_iva = amount_ret_1 = amount_ret_5 = 0.00
        for line in rec.invoice_line_ids:
            #Calculo del monto del IVA para el reporte
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
                if tax.id in rec.company_id.tax_ret_5_id.ids:
                    tax_res = tax.compute_all(line.price_unit, rec.company_id.currency_id, line.quantity, line.product_id, rec.partner_id)
                    for t in tax_res.get('taxes', []):
                        amount_ret_5 += t.get('amount', 0.00)
            rec.write({
                'amount_tax_iva': amount_iva or 0.00,
                'amount_tax_ret_1': amount_ret_1 or 0.00,
                'amount_tax_ret_5': amount_ret_5 or 0.00,
            })
