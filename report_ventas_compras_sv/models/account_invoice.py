from odoo import fields, models, api, _


class AccountInvoice(models.Model):
    _inherit = "account.move"

    DUCA = fields.Float('DUCA')


AccountInvoice()
