# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.tools import config, date_utils, get_lang
from datetime import datetime, timedelta
from dateutil.parser import parse


class VencidasMultimonedaReport(models.AbstractModel):
    _name = "vencidas.multimoneda.report"
    _description = "Vencidas Multimoneda"
    _inherit = "account.report"
    #
    filter_date = {'mode': 'single', 'filter': 'today'}
    filter_partner = True

    @api.model
    def _get_report_name(self):
        return "Vencidas Multimoneda"

    def _get_templates(self):
        templates = super(VencidasMultimonedaReport, self)._get_templates()
        templates['main_template'] = 'vencidas_multimoneda.main_template'
        templates['line_template'] = 'vencidas_multimoneda.line_template'
        return templates

    def _get_columns_name(self, options):
        return [{'name': ''}] * 12

    def do_query(self, type):
        company_id = self.env.company.id
        query = """
           SELECT DISTINCT AM.id,
                            AM.partner_id,
                            RP.name,
                            AM.amount_total,
                            AM.currency_id,
                            AM.invoice_date_due,
                            AJ.name AS journal,
                            AA.name AS account,
                            AM.currency_id as movecur,
                            AM.name as move_name
            --                 AP.amount
            FROM account_move AM
                     JOIN res_partner RP ON RP.id = AM.partner_id
                     JOIN account_move_line AML ON (AM.id = AML.move_id)
                     JOIN account_account AA ON AML.account_id = AA.id
                     JOIN account_account_type AAT ON AA.user_type_id = AAT.id
                     JOIN account_journal AJ ON (AM.journal_id = AJ.id)
            WHERE Am.company_id = {}
              AND AM.invoice_date_due IS NOT NULL
              AND AAT.type = '{}'
              AND AM.state = 'posted'
              AND AM.amount_residual > 0
            ORDER BY AM.currency_id, RP.name, AM.invoice_date_due
        """.format(company_id, type)

        self.env.cr.execute(query)
        result = self.env.cr.dictfetchall()
        return result

    def do_query_payments(self, date, field1, field2, type):
        company_id = self.env.company.id
        query = """
            SELECT DISTINCT AP.amount, AM.partner_id, AP.id, AP.payment_date, AP.currency_id, AM.currency_id as movecur
            FROM account_move AM
                     JOIN account_move_line AML ON (AM.id = AML.move_id)
                     JOIN account_account AA ON AML.account_id = AA.id
                     JOIN account_account_type AAT ON AA.user_type_id = AAT.id
                     JOIN account_partial_reconcile APR ON (AML.id = APR.{})
                     JOIN account_move_line AML2 ON (AML2.id = APR.{})
                     JOIN account_payment AP ON (AML2.payment_id = AP.id)
            WHERE AM.company_id = {}
              AND AP.payment_date < '{}'
              AND AM.type IN ('out_invoice', 'out_refund', 'in_refund', 'in_invoice')
              AND AAT.type = '{}'
              AND AM.state = 'posted'
              AND AM.amount_residual > 0
              
        """.format(field1, field2, company_id, date, type)
        self.env.cr.execute(query)
        result = self.env.cr.dictfetchall()
        return result

    # def do_query_payments(self, date):
    #     company_id = self.env.company.id
    #     query = """
    #            SELECT DISTINCT AP.amount, AP.partner_id, AP.id, AP.payment_date, AP.currency_id
    #            FROM account_payment AP
    #            JOIN account_journal AJ ON (AJ.id = AP.journal_id)
    #            WHERE AJ.company_id = {}
    #              AND AP.payment_date < '{}'
    #              AND AP.state = 'posted'
    #        """.format(company_id, date)
    #     self.env.cr.execute(query)
    #     result = self.env.cr.dictfetchall()
    #     return result

    def group_by_date(self, date):
        result = self.do_query()
        grouped = {}
        for row in result:
            group = '{}-{}'.format(row['partner_id'], row['currency_id'])
            if group not in grouped:
                grouped[group] = {'name': row['name'],
                                  'partner_id': row['id'],
                                  'periods': [0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
                                  'currency_id': row['currency_id'],
                                  'move_currency_id': row['movecur'],
                                  'name': row['name'],
                                  }
            diff = date - row['invoice_date_due']
            if diff < timedelta(days=1):
                grouped[group]['periods'][0] += row['amount_total']
            if (diff >= timedelta(days=1)) and (diff < timedelta(days=31)):
                grouped[group]['periods'][1] += row['amount_total']

            if (diff >= timedelta(days=31)) and (diff < timedelta(days=61)):
                grouped[group]['periods'][2] += row['amount_total']
            if (diff >= timedelta(days=61)) and (diff < timedelta(days=91)):
                grouped[group]['periods'][3] += row['amount_total']
            if (diff >= timedelta(days=91)) and (diff < timedelta(days=121)):
                grouped[group]['periods'][4] += row['amount_total']
            if diff >= timedelta(days=121):
                grouped[group]['periods'][5] += row['amount_total']
        return grouped

    def group_by_date_payment(self, date):

        result = self.do_query_payments(date)
        result = self.clean_currency_move_id(result)
        grouped = self.group_by_date(date)
        for row in result:
            group = '{}-{}'.format(row['partner_id'], row['currency_id'])
            diff = date - row['payment_date']
            try:
                if diff < timedelta(days=1):
                    grouped[group]['periods'][0] -= row['amount']
                if (diff >= timedelta(days=1)) and (diff < timedelta(days=31)):
                    grouped[group]['periods'][1] -= row['amount']
                if (diff >= timedelta(days=31)) and (diff < timedelta(days=61)):
                    grouped[group]['periods'][2] -= row['amount']
                if (diff >= timedelta(days=61)) and (diff < timedelta(days=91)):
                    grouped[group]['periods'][3] -= row['amount']
                if (diff >= timedelta(days=91)) and (diff < timedelta(days=121)):
                    grouped[group]['periods'][4] -= row['amount']
                if diff >= timedelta(days=121):
                    grouped[group]['periods'][5] -= row['amount']
            except KeyError:
                pass
        return grouped

    def clean_currency_move_id(self, data):
        cont = 0
        for row in data:
            if data[cont]['currency_id'] != data[cont]['movecur']:
                date = data[cont]['payment_date'].strftime("%d/%m/%Y")
                rate = self.env['res.currency.rate'].search(
                    [
                        ('name', '=', data[cont]['payment_date']),
                        ('currency_id', '=', data[cont]['movecur'])
                    ],
                    limit=1
                )
                if rate:
                    data[cont]['amount'] = data[cont]['amount'] / (1/rate.rate)
            data[cont]['currency_id'] = data[cont]['movecur']
            cont += 1

        return data


    @api.model
    def _get_lines(self, options, line_id=None):
        lines = []
        try:
            date = parse(options['date']['date_to']).date()
        except KeyError:
            date = datetime.now().date()

        partners = self.group_by_date_payment(date)

        lines.append({
            'id': 'header_2',
            'name': '',
            'columns': [
                {'name': 'Fecha vencimiento'},
                {'name': 'Diario'},
                {'name': 'cuenta'},
                {'name': 'Exp. Date'},
                {'name': 'A partir de {}'.format(date.strftime('%d/%m/%Y')), 'class': 'text-right'},
                {'name': '1 - 30', 'class': 'text-right'},
                {'name': '31 - 60', 'class': 'text-right'},
                {'name': '61 - 90', 'class': 'text-right'},
                {'name': '91 - 120', 'class': 'text-right'},
                {'name': 'Older', 'class': 'text-right'},
                {'name': 'Total', 'class': 'text-right'},
            ],
            'level': 1
        })
        currencies = {}
        totals = [0.00] * 7
        for partner in partners.values():
            if partner['currency_id'] == 2:
                continue

            # zero_line code allow to exclude lines with 0 amount in all periods, no needed if all the lines with total 0 are excluded
            # zero_line = True
            if partner['currency_id'] not in currencies:
                currency = self.env['res.currency'].search([('id', '=', partner['currency_id'])], limit=1)
                currencies[currency.id] = currency
            total_partner = sum(partner['periods'])

            for index, total in enumerate(totals):
                if index == 6:
                    totals[index] += total_partner
                else:
                    totals[index] += partner['periods'][index]
                    # if round(partner['periods'][index], 2) != 0:
                    #     zero_line = False

            # if zero_line:
            #     continue
            if round(total_partner, 2) == 0:
                continue
            lines.append({
                'id': 'header_2',
                'name': partner['name'],
                'columns': [
                    {'name': ''},
                    {'name': ''},
                    {'name': ''},
                    {'name': ''},
                    {'name': self.format_value(partner['periods'][0], currencies[partner['currency_id']]),
                     'class': 'text-right'},
                    {'name': self.format_value(partner['periods'][1], currencies[partner['currency_id']]),
                     'class': 'text-right'},
                    {'name': self.format_value(partner['periods'][2], currencies[partner['currency_id']]),
                     'class': 'text-right'},
                    {'name': self.format_value(partner['periods'][3], currencies[partner['currency_id']]),
                     'class': 'text-right'},
                    {'name': self.format_value(partner['periods'][4], currencies[partner['currency_id']]),
                     'class': 'text-right'},
                    {'name': self.format_value(partner['periods'][5], currencies[partner['currency_id']]),
                     'class': 'text-right'},
                    {'name': self.format_value(total_partner, currencies[partner['currency_id']]),
                     'class': 'text-right'},
                ],
                'level': 3
            })
        try:
            lines.append({
                'id': 'total_2',
                'name': 'Total',
                'columns': [
                    {'name': ''},
                    {'name': ''},
                    {'name': ''},
                    {'name': ''},
                    {'name': self.format_value(totals[0], currencies[partner['currency_id']]), 'class': 'text-right'},
                    {'name': self.format_value(totals[1], currencies[partner['currency_id']]), 'class': 'text-right'},
                    {'name': self.format_value(totals[2], currencies[partner['currency_id']]), 'class': 'text-right'},
                    {'name': self.format_value(totals[3], currencies[partner['currency_id']]), 'class': 'text-right'},
                    {'name': self.format_value(totals[4], currencies[partner['currency_id']]), 'class': 'text-right'},
                    {'name': self.format_value(totals[5], currencies[partner['currency_id']]), 'class': 'text-right'},
                    {'name': self.format_value(totals[6], currencies[partner['currency_id']]), 'class': 'text-right'},
                ],
                'level': 2
            })
        except UnboundLocalError:
            pass

        lines.append({'id': 'empty_line', 'columns': [{'name': ''}], 'level': 3})
        lines.append({'id': 'empty_line', 'columns': [{'name': ''}], 'level': 3})
        lines.append({'id': 'empty_line', 'columns': [{'name': ''}], 'level': 3})
        lines.append({
            'id': 'header_2',
            'name': '',
            'columns': [
                {'name': 'Fecha vencimiento'},
                {'name': 'Diario'},
                {'name': 'cuenta'},
                {'name': 'Exp. Date'},
                {'name': 'A partir de {}'.format(date.strftime('%d/%m/%Y')), 'class': 'text-right'},
                {'name': '1 - 30', 'class': 'text-right'},
                {'name': '31 - 60', 'class': 'text-right'},
                {'name': '61 - 90', 'class': 'text-right'},
                {'name': '91 - 120', 'class': 'text-right'},
                {'name': 'Older', 'class': 'text-right'},
                {'name': 'Total', 'class': 'text-right'},
            ],
            'level': 1
        })
        totals = [0.00] * 7
        for partner in partners.values():
            if partner['currency_id'] != 2:
                continue

            # zero_line = True
            if partner['currency_id'] not in currencies:
                currency = self.env['res.currency'].search([('id', '=', partner['currency_id'])], limit=1)
                currencies[currency.id] = currency
            total_partner = sum(partner['periods'])

            for index, total in enumerate(totals):
                if index == 6:
                    totals[index] += total_partner
                else:
                    totals[index] += partner['periods'][index]
                    # if round(partner['periods'][index], 2) != 0:
                    #     zero_line = False

            # if zero_line:
            #     continue
            if round(total_partner, 2) == 0:
                continue
            lines.append({
                'id': 'header_2',
                'name': partner['name'],
                'columns': [
                    {'name': ''},
                    {'name': ''},
                    {'name': ''},
                    {'name': ''},
                    {'name': self.format_value(partner['periods'][0], currencies[partner['currency_id']]),
                     'class': 'text-right'},
                    {'name': self.format_value(partner['periods'][1], currencies[partner['currency_id']]),
                     'class': 'text-right'},
                    {'name': self.format_value(partner['periods'][2], currencies[partner['currency_id']]),
                     'class': 'text-right'},
                    {'name': self.format_value(partner['periods'][3], currencies[partner['currency_id']]),
                     'class': 'text-right'},
                    {'name': self.format_value(partner['periods'][4], currencies[partner['currency_id']]),
                     'class': 'text-right'},
                    {'name': self.format_value(partner['periods'][5], currencies[partner['currency_id']]),
                     'class': 'text-right'},
                    {'name': self.format_value(total_partner, currencies[partner['currency_id']]),
                     'class': 'text-right'},
                ],
                'level': 3
            })

        try:
            lines.append({
                'id': 'total_2',
                'name': 'Total',
                'columns': [
                    {'name': ''},
                    {'name': ''},
                    {'name': ''},
                    {'name': ''},
                    {'name': self.format_value(totals[0], currencies[2]), 'class': 'text-right'},
                    {'name': self.format_value(totals[1], currencies[2]), 'class': 'text-right'},
                    {'name': self.format_value(totals[2], currencies[2]), 'class': 'text-right'},
                    {'name': self.format_value(totals[3], currencies[2]), 'class': 'text-right'},
                    {'name': self.format_value(totals[4], currencies[2]), 'class': 'text-right'},
                    {'name': self.format_value(totals[5], currencies[2]), 'class': 'text-right'},
                    {'name': self.format_value(totals[6], currencies[2]), 'class': 'text-right'},
                ],
                'level': 2
            })
        except KeyError:
            pass

        # {'name': self.format_value(total_vencido, currencies[partner['currency_id']])},

        return lines


class VencidasCobrarMultimonedaReport(VencidasMultimonedaReport):
    _name = "vencidas.cobrar.multimoneda.report"
    _description = "Vencidas Multimoneda"

    def do_query(self, type='receivable'):
        return super(VencidasCobrarMultimonedaReport, self).do_query(type)

    def do_query_payments(self, date, field1='debit_move_id', field2='credit_move_id', type='receivable'):
        return super(VencidasCobrarMultimonedaReport, self).do_query_payments(date, field1, field2, type)


class VencidasPagarMultimonedaReport(VencidasMultimonedaReport):
    _name = "vencidas.pagar.multimoneda.report"
    _description = "Vencidas Multimoneda"

    def do_query(self, type='payable'):
        return super(VencidasPagarMultimonedaReport, self).do_query(type)

    def do_query_payments(self, date, field1='credit_move_id', field2='debit_move_id', type='payable'):
        return super(VencidasPagarMultimonedaReport, self).do_query_payments(date, field1, field2, type)
