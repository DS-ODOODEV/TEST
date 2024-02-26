# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date
import time

MONTHS = {
        'January': 'Enero', 
        'February': 'Febrero', 
        'March': 'Marzo', 
        'April': 'Abril', 
        'May': 'Mayo',
        'June': 'Junio', 
        'July': 'Julio', 
        'August': 'Agosto', 
        'September': 'Septiembre',
        'October': 'Octubre',
        'November': 'Noviembre', 
        'December': 'Diciembre'
    }

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def _get_months(self, date):
        months_format = date.strftime('%B')
        return months_format
