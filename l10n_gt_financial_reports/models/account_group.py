# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from .account_general_ledger import AccountGeneralLedgerReport as GLedger
import re
import copy
from odoo.osv import expression
from datetime import datetime



import logging

_logger = logging.getLogger( __name__ )

class AccountGroups(models.Model):
    _inherit = 'account.group'

    code_prefix_start = fields.Char('Desde')
    code_prefix_end = fields.Char('Hasta')
    
AccountGroups()