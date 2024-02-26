# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api, _
from odoo.exceptions import ValidationError
from odoo.tools import config, date_utils, get_lang
from datetime import datetime, timedelta
import dateutil
from dateutil.parser import parse
from dateutil import parser


class BankBalanceReportAbstract(models.AbstractModel):
    _name = "bank.balance.abstract.report"
    _description = "Bank Balance Report Abstract"
    _inherit = "account.report"

    filter_date = {'mode': 'single', 'filter': 'today'}
    filter_journals = True

    @api.model
    def _get_report_name(self):
        return "Reporte de Saldos de Bancos"

    def _get_templates(self):
        return super(BankBalanceReportAbstract, self)._get_templates()

    def _get_columns_name(self, options):
        return [{'name': ''}] * 2

    @api.model
    def _get_lines(self, options, line_id=None):
        date_to = parser.parse(options.get('date').get('date_to'))

        journal_ids = []

        for obj in options.get('journals'):
            if obj.get('selected'):
                journal_ids.append(obj.get('id'))

        lines = list([])

        lines.append({
            'id': 'header_1',
            'name': 'USD Bank Accounts',
            'columns':
                [
                    {'name': 'Total', 'class': 'text-right total'},
                ],
            'level': 1
        })
        account_types = self.env['account.account.type'].search(['|', ('name', '=', 'Banco y caja'), ('name', '=', 'Bank and Cash')]).mapped('id')
        usd_currency = self.env['res.currency'].search([('name', '=', 'USD')])
        accounts = self.env['account.account'].search([('user_type_id', 'in', account_types), ('currency_id', '=', usd_currency.id)])
        count = 0
        total_usd = 0
        for account in accounts:
            count += 1
            if not journal_ids:
                move_lines = self.env['account.move.line'].search([('account_id', '=', account.id)])
            else:
                move_lines = self.env['account.move.line'].search([('account_id', '=', account.id), ('journal_id', 'in', journal_ids)])

            if date_to:
                move_lines = move_lines.filtered(lambda move_line: move_line.create_date.date() <= date_to.date())

            debit = 0
            credit = 0
            for move_line in move_lines:
                if move_line.amount_currency:
                    if move_line.debit > 0:
                        debit += move_line.amount_currency
                    elif move_line.credit > 0:
                        credit += abs(move_line.amount_currency)
                else:
                    accounting_date = move_line.move_id.date
                    currency_rate = self.env['res.currency.rate'].search([('currency_id', '=', usd_currency.id), ('name', '=', accounting_date)])

                    if move_line.debit > 0:
                        debit += (move_line.debit * currency_rate.rate)
                    elif move_line.credit > 0:
                        credit += (move_line.credit * currency_rate.rate)

            total = debit - credit
            if total != 0:
                total_usd += total
                lines.append({
                    'id': 'header_2',
                    'name': str(account.code) + ' ' + str(account.name),
                    'columns':
                        [
                            {'name': '$ ' + str("%.2f" % total), 'class': 'text-right total', 'style': 'color: green'},
                        ],
                    'level': 2
                })

        lines.append({
            'id': 'header_2',
            'name': 'Total',
            'columns':
                [
                    {'name': '$ ' + str("%.2f" % total_usd), 'class': 'text-right total', 'style': 'color: blue'},
                ],
            'level': 2
        })

        lines.append({
            'id': 'header_2',
            'name': 'GTQ Bank Accounts',
            'columns':
                [
                    {'name': 'Total', 'class': 'text-right total'},
                ],
            'level': 1
        })

        accounts = self.env['account.account'].search([('user_type_id', 'in', account_types), ('currency_id', '!=', usd_currency.id)])

        count = 0
        total_gtq = 0
        for account in accounts:
            count += 1
            if not journal_ids:
                move_lines = self.env['account.move.line'].search([('account_id', '=', account.id)])
            else:
                move_lines = self.env['account.move.line'].search([('account_id', '=', account.id), ('journal_id', 'in', journal_ids)])

            if date_to:
                move_lines = move_lines.filtered(lambda move_line: move_line.create_date.date() <= date_to.date())

            debit = 0
            credit = 0

            for move in move_lines:
                debit += move.debit
                credit += move.credit

            total = debit - credit
            total_gtq += total

            if total > 0:
                lines.append({
                    'id': 'header_2',
                    'name': str(account.code) + ' ' + str(account.name),
                    'columns':
                        [
                            {'name': 'Q ' + str("%.2f" % total), 'class': 'text-right total', 'style': 'color: green'},
                        ],
                    'level': 2
                })

        lines.append({
            'id': 'header_2',
            'name': 'Total',
            'columns':
                [
                    {'name': 'Q ' + str("%.2f" % total_gtq), 'class': 'text-right total', 'style': 'color: blue'},
                ],
            'level': 2
        })

        return lines


class BankBalanceReport(BankBalanceReportAbstract):
    _name = "bank.balance.report"
    _description = "Bank Balance Report"

    def do_query(self, type='receivable'):
        return super(BankBalanceReport, self).do_query(type)

    def do_query_payments(self, date, field1='debit_move_id', field2='credit_move_id', type='receivable'):
        return super(BankBalanceReport, self).do_query_payments(date, field1, field2, type)
