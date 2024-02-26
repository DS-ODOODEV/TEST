# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError, AccessError



class Lead(models.Model):
    _inherit = "crm.lead"

    currency_display = fields.Many2one('res.currency', 'Currency', compute="_get_currency_display")

    @api.depends('company_id')
    def _get_currency_display(self):
        for rec in self:
            currency_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
            rec.update({
                'currency_display': currency_id.id or False,
            })
Lead()
