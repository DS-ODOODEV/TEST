# -*- coding: utf-8 -*-

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = "res.company"

    report_id = fields.Many2one('hr.payslip.report', 'Payslip Report', required=False, readonly=False)

ResCompany()

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    report_id = fields.Many2one('hr.payslip.report', 'Payslip Report', related="company_id.report_id", readonly=False)

ResConfigSettings()

