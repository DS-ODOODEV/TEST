from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    nc_type = fields.Selection(
        [('anulacion','ANULACION'), ('devolucion','DEVOLUCION'), ('descuento','DESCUENTO')],
        string="Tipo de accion",
        default="anulacion"
    )