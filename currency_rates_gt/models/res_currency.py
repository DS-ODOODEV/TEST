# -*- encoding: UTF-8 -*-
##############################################################################
#
# Odoo, Open Source Management Solution
# Copyright (C) 2018-Today Xetechs, S.A.
# (<https://www.xetechs.com>)
#
##############################################################################
from odoo import fields, api, models, tools
from suds.client import Client
from datetime import datetime, date, time, timedelta
from odoo.exceptions import AccessError, UserError

url = 'http://www.banguat.gob.gt/variables/ws/TipoCambio.asmx?WSDL'


class ResCurrency(models.Model):
    _inherit = "res.currency"
    
    active_webservice = fields.Boolean('¿Tipo de cambio de Banguat?', required=False, default=False)

    def get_currency_update(self):
        try:
            client = Client(url)
            cambio = client.service.TipoCambioDia()
            dolar = float(cambio.CambioDolar.VarDolar[0].referencia)
            return float(1/dolar)
        except Exception as e:
            raise UserError(('%s') %(e))
            #return float(1/dolar)

    def get_currency_rate(self):
        rate_obj = self.env['res.currency.rate']
        for rec in self:
            try:
                if rec.name == 'USD' and rec.active_webservice == True:
                    client = Client(url)
                    response = client.service.TipoCambioDia()
                    amount_usd = float(response.CambioDolar.VarDolar[0].referencia)
                    rate_obj.create({
                        'currency_id': rec.id,
                        'name': fields.Date.today(),
                        'rate': float((1/amount_usd)),
                    })
                elif rec.name == 'EUR' and rec.active_webservice == True:
                    client = Client(url)
                    cambio_multi = client.service.Variables(24)
                    amount_eur = cambio_multi.CambioDia.Var[0].venta
                    rate_obj.create({
                        'currency_id': rec.id,
                        'name': fields.Date.today(),
                        'rate': float((1/amount_eur)),
                    })
                else:
                    continue
            except Exception as e:
                raise UserError(('%s') %(e))
        
    @api.model
    def _process_get_currency_rate(self):
        rate_obj = self.env['res.currency.rate']
        currency_ids = self.env['res.currency'].search([('active_webservice', '=', True)])
        for rec in currency_ids:
            try:
                if rec.name == 'USD':
                    client = Client(url)
                    response = client.service.TipoCambioDia()
                    amount_usd = float(response.CambioDolar.VarDolar[0].referencia)
                    rate_obj.create({
                        'currency_id': rec.id,
                        'name': fields.Date.today(),
                        'rate': float((1/amount_usd)),
                    })
                elif rec.name == 'EUR':
                    client = Client(url)
                    cambio_multi = client.service.Variables(24)
                    amount_eur = cambio_multi.CambioDia.Var[0].venta
                    rate_obj.create({
                        'currency_id': rec.id,
                        'name': fields.Date.today(),
                        'rate': float((1/amount_eur)),
                    })
                else:
                    continue
            except Exception as e:
                raise UserError(('%s') %(e))


ResCurrency()