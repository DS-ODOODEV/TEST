# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import config, date_utils, get_lang
from dateutil.parser import parse


class BalanceSheetSV(models.AbstractModel):
    _name = "balance.sheet.sv"
    _description = "Balance de Situación"
    _inherit = "account.report"

    filter_date = {'mode': 'single'}
    empty_line = {'id': 'empty_line', 'name': '', 'columns': [{'name': 'empty', 'style': 'color: transparent'}],
                  'level': 1}

    @api.model
    def _get_report_name(self):
        return "Balance de Situación SV"

    def _get_templates(self):
        templates = super(BalanceSheetSV, self)._get_templates()
        templates['main_template'] = 'balance_sheet_sv.main_template'
        templates['line_template'] = 'balance_sheet_sv.line_template'
        return templates

    def _get_columns_name(self, options):
        return [{'name': ''}] * 7

    def _do_query(self, options):
        date = parse(options['date']['date_to'])
        BA = self.env['account.move.line'].search(
            [('account_id.user_type_id', '=', self.env.ref('account.data_account_type_liquidity').id),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        REC = self.env['account.move.line'].search([('account_id.user_type_id.type', '=', 'receivable'),
                                                    ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        CAS = self.env['account.move.line'].search(
            [('account_id.user_type_id', '=', self.env.ref('account.data_account_type_current_assets').id),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        PRE = self.env['account.move.line'].search(
            [('account_id.user_type_id', '=', self.env.ref('account.data_account_type_prepayments').id),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        CL1 = self.env['account.move.line'].search(
            [('account_id.user_type_id', 'in', [self.env.ref('account.data_account_type_current_liabilities').id,
                                                self.env.ref('account.data_account_type_credit_card').id]),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        CL2 = self.env['account.move.line'].search([('account_id.user_type_id.type', '=', 'payable'),
                                                    ('company_id', '=', self.env.company.id), ('date', '<=', date)])
        ACYOCPP = self.env['account.move.line'].search([('company_id', '=', self.env.company.id), ('date', '<=', date),
                                                        '|', '|', '|', '|', ('account_id.code', '=', '2102010201'),
                                                        ('account_id.code', '=', '21020302'),
                                                        ('account_id.code', '=', '2102030301'),
                                                        ('account_id.code', '=', '2102030302'),
                                                        ('account_id.code', '=', '2102030303')])
        PPIC = self.env['account.move.line'].search([('company_id', '=', self.env.company.id), ('date', '<=', date),
                                                     '|', '|', ('account_id.code', '=', '210402'),
                                                     ('account_id.code', '=', '210403'),
                                                     ('account_id.code', '=', '210406')])
        PRPP = self.env['account.move.line'].search([('company_id', '=', self.env.company.id), ('date', '<=', date),
                                                     ('account_id.code', '=', '2107010101')])

        FA = self.env['account.move.line'].search(
            [('account_id.user_type_id', '=', self.env.ref('account.data_account_type_fixed_assets').id),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        NL = self.env['account.move.line'].search(
            [('account_id.user_type_id', '=', self.env.ref('account.data_account_type_non_current_liabilities').id),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        PPE = self.env['account.move.line'].search([('company_id', '=', self.env.company.id), ('date', '<=', date),
                                                    ('account_id.code', 'in', ['12010102', '12010202'])])

        DAP = self.env['account.move.line'].search([('company_id', '=', self.env.company.id), ('date', '<=', date),
                                                    ('account_id.code', 'in', ['12010301', '12010303'])])

        PNC = self.env['account.move.line'].search([('company_id', '=', self.env.company.id), ('date', '<=', date),
                                                    ('account_id.code', '=', '22040101')])

        OPINC = self.env['account.move.line'].search(
            [('account_id.user_type_id', '=', self.env.ref('account.data_account_type_revenue').id),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        OIN = self.env['account.move.line'].search(
            [('account_id.user_type_id', '=', self.env.ref('account.data_account_type_other_income').id),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        COS = self.env['account.move.line'].search(
            [('account_id.user_type_id', '=', self.env.ref('account.data_account_type_direct_costs').id),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        EXP = self.env['account.move.line'].search(
            [('account_id.user_type_id', '=', self.env.ref('account.data_account_type_expenses').id),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        DEP = self.env['account.move.line'].search(
            [('account_id.user_type_id', '=', self.env.ref('account.data_account_type_depreciation').id),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        PREV_YEAR_EARNINGS = self.env['account.move.line'].search(
            [('account_id.user_type_id', '=', self.env.ref('account.data_unaffected_earnings').id),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        CURR_YEAR_EARNINGS_PNL = self.env['account.move.line'].search(
            [('account_id.user_type_id', 'in', [self.env.ref('account.data_account_type_revenue').id,
                                                self.env.ref('account.data_account_type_other_income').id,
                                                self.env.ref('account.data_account_type_direct_costs').id,
                                                self.env.ref('account.data_account_type_expenses').id,
                                                self.env.ref('account.data_account_type_depreciation').id
                                                ]),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        CURR_YEAR_EARNINGS_ALLOC = self.env['account.move.line'].search(
            [('account_id.user_type_id', '=', self.env.ref('account.data_unaffected_earnings').id),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        RETAINED_EARNINGS = self.env['account.move.line'].search(
            [('account_id.user_type_id', '=', self.env.ref('account.data_account_type_equity').id),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        CS = self.env['account.move.line'].search([('company_id', '=', self.env.company.id), ('date', '<=', date),
                                                   ('account_id.code', 'in', ['310101', '310103', '310201'])])

        RL = self.env['account.move.line'].search([('company_id', '=', self.env.company.id), ('date', '<=', date),
                                                   ('account_id.code', '=', '320101')])

        UEA = self.env['account.move.line'].search([('company_id', '=', self.env.company.id), ('date', '<=', date),
                                                    ('account_id.code', '=', '330101')])

        PNCA = self.env['account.move.line'].search(
            [('account_id.user_type_id', '=', self.env.ref('account.data_account_type_non_current_assets').id),
             ('company_id', '=', self.env.company.id), ('date', '<=', date)])

        results = {
            'BA': self._get_balance(BA),
            'REC': self._get_balance(REC),
            'CAS': self._get_balance(CAS),
            'PRE': self._get_balance(PRE),
            'CL1': self._get_balance(CL1) * -1,
            'CL2': self._get_balance(CL2) * -1,
            'ACYOCPP': self._get_balance(ACYOCPP) * -1,
            'PPIC': self._get_balance(PPIC) * -1,
            'PRPP': self._get_balance(PRPP) * -1,
            'FA': self._get_balance(FA),
            'NL': self._get_balance(NL) * -1,
            'PPE': self._get_balance(PPE),
            'DAP': self._get_balance(DAP),
            'PNC': self._get_balance(PNC) * -1,
            'OPINC': self._get_balance(OPINC) * -1,
            'OIN': self._get_balance(OIN) * -1,
            'COS': self._get_balance(COS),
            'EXP': self._get_balance(EXP),
            'DEP': self._get_balance(DEP),
            'CURR_YEAR_EARNINGS_PNL': self._get_balance(CURR_YEAR_EARNINGS_PNL) * -1,
            'CURR_YEAR_EARNINGS_ALLOC': self._get_balance(CURR_YEAR_EARNINGS_ALLOC) * -1,
            'RETAINED_EARNINGS': self._get_balance(RETAINED_EARNINGS) * -1,
            'CS': self._get_balance(CS) * -1,
            'RL': self._get_balance(RL) * -1,
            'UEA': self._get_balance(UEA) * -1,
            'PNCA': self._get_balance(PNCA),
        }

        results['CA'] = results['BA'] + results['REC'] + results['CAS'] + results['PRE']
        results['CL'] = results['CL1'] + results['CL2']
        results['L'] = results['CL'] + results['NL']
        results['PC'] = results['ACYOCPP'] + results['PPIC'] + results['PRPP']
        results['NEP'] = results['OPINC'] + results['OIN'] - results['COS'] - results['EXP'] - results['DEP']
        results['CURR_YEAR_EARNINGS'] = results['CURR_YEAR_EARNINGS_PNL'] + results['CURR_YEAR_EARNINGS_ALLOC']
        results['PREV_YEAR_EARNINGS'] = results['NEP'] - self._get_balance(PREV_YEAR_EARNINGS) - results[
            'CURR_YEAR_EARNINGS']
        results['UNAFFECTED_EARNINGS'] = results['CURR_YEAR_EARNINGS'] + results['PREV_YEAR_EARNINGS']
        results['EQ'] = results['UNAFFECTED_EARNINGS'] + results['RETAINED_EARNINGS']
        results['TA'] = results['CA'] + results['FA'] + results['PNCA']
        results['LE'] = results['L'] + results['EQ']

        return results

    def _get_balance(self, amls):
        return sum([aml.balance for aml in amls])

    @api.model
    def _get_lines(self, options, line_id=None):
        results = self._do_query(options)
        date = parse(options['date']['date_to'])
        lines = []
        lines += self._get_header(date)

        lines.append({
            'id': 'activo',
            'name': '',
            'columns': [
                {'name': 'ACTIVO', 'colspan': 3, 'class': 'text-left title'},
                {'name': 'PASIVO', 'colspan': 3, 'class': 'text-left title'},
            ],
            'level': 1,
            'class': 'header_producto'
        })
        lines.append({
            'id': 'activo',
            'name': '',
            'columns': [
                {'name': 'ACTIVOS CORRIENTES', 'class': 'text-left title'},
                {'name': '', 'class': 'text-right'},
                {'name': self._format(results['CA']), 'class': 'text-right'},
                {'name': 'PASIVOS CORRIENTES', 'class': 'text-left title'},
                {'name': '', 'class': 'text-right'},
                {'name': self._format(results['PC']), 'class': 'text-right'},
            ],
            'level': 1,
            'class': 'header_producto'
        })
        lines.append({
            'id': 'activo',
            'name': '',
            'columns': [
                {'name': 'EFECTIVO y EQUIVALENTES DEL EFECTIVO', 'class': 'text-left'},
                {'name': self._format(results['BA']), 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
                {'name': 'ACREEDORES COMERCIALES Y OTRAS CUENTAS POR PAGAR', 'class': 'text-left'},
                {'name': self._format(results['ACYOCPP']), 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
            ],
            'level': 2,
            'class': 'header_producto'
        })
        lines.append({
            'id': 'activo',
            'name': '',
            'columns': [
                {'name': 'INVENTARIOS', 'class': 'text-left'},
                {'name': self._format(results['CAS']), 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
                {'name': 'PASIVO POR IMPUESTOS CORRIENTES', 'class': 'text-left'},
                {'name': self._format(results['PPIC']), 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
            ],
            'level': 2,
            'class': 'header_producto'
        })
        lines.append({
            'id': 'activo',
            'name': '',
            'columns': [
                {'name': 'DEUDORES COMERCIALES Y OTRAS CUENTAS POR COBRAR', 'class': 'text-left'},
                {'name': self._format(results['REC']), 'class': 'text-right total'},
                {'name': '', 'class': 'text-right'},
                {'name': 'PARTES RELACIONADAS POR PAGAR', 'class': 'text-left'},
                {'name': self._format(results['PRPP']), 'class': 'text-right total'},
                {'name': '', 'class': 'text-right'},
            ],
            'level': 2,
            'class': 'header_producto'
        })
        lines.append(self.empty_line)
        lines.append(self.empty_line)
        lines.append(self.empty_line)
        lines.append({
            'id': 'activo',
            'name': '',
            'columns': [
                {'name': 'ACTIVOS NO CORRIENTES', 'class': 'text-left title'},
                {'name': '', 'class': 'text-right'},
                {'name': self._format(results['FA']), 'class': 'text-right'},
                {'name': 'PASIVOS NO CORRIENTES', 'class': 'text-left title'},
                {'name': '', 'class': 'text-right'},
                {'name': self._format(results['PNC']), 'class': 'text-right'},
            ],
            'level': 1,
            'class': 'header_producto'
        })

        lines.append({
            'id': 'activo',
            'name': '',
            'columns': [
                {'name': 'PROPIEDAD PLANTA Y EQUIPO', 'class': 'text-left'},
                {'name': self._format(results['PPE']), 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
                {'name': 'BENEFICIOS EMPLEADOS POR PAGAR', 'class': 'text-left'},
                {'name': self._format(results['PNC']), 'class': 'text-right total'},
                {'name': '', 'class': 'text-right total'},
            ],
            'level': 2,
            'class': 'header_producto'
        })

        lines.append({
            'id': 'activo',
            'name': '',
            'columns': [
                {'name': 'DEPRECIACION ACUMULADA DE PIE', 'class': 'text-left'},
                {'name': self._format(results['DAP']), 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
                {'name': 'TOTAL PASIVO', 'class': 'text-left'},
                {'name': '', 'class': 'text-right'},
                {'name': self._format(results['L']), 'class': 'text-right'},
            ],
            'level': 2,
            'class': 'header_producto'
        })
        lines.append({
            'id': 'activo',
            'name': '',
            'columns': [
                {'name': '', 'class': 'text-left'},
                {'name': '', 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
                {'name': 'PATRIMONIO', 'class': 'text-left title'},
                {'name': '', 'class': 'text-right'},
                {'name': self._format(results['EQ']), 'class': 'text-right'},
            ],
            'level': 1,
            'class': 'header_producto'
        })
        lines.append({
            'id': 'activo',
            'name': '',
            'columns': [
                {'name': '', 'class': 'text-left'},
                {'name': '', 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
                {'name': 'CAPITAL SOCIAL', 'class': 'text-left'},
                {'name': self._format(results['CS']), 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
            ],
            'level': 2,
            'class': 'header_producto'
        })
        lines.append({
            'id': 'activo',
            'name': '',
            'columns': [
                {'name': '', 'class': 'text-left'},
                {'name': '', 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
                {'name': 'RESERVA LEGAL', 'class': 'text-left'},
                {'name': self._format(results['RL']), 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
            ],
            'level': 2,
            'class': 'header_producto'
        })
        lines.append({
            'id': 'activo',
            'name': '',
            'columns': [
                {'name': '', 'class': 'text-left'},
                {'name': '', 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
                {'name': 'UTILIDAD DE EJERCICIOS ANTERIORES', 'class': 'text-left'},
                {'name': self._format(results['UEA']), 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
            ],
            'level': 2,
            'class': 'header_producto'
        })
        year = date = parse(options['date']['date_to']).year
        lines.append({
            'id': 'activo',
            'name': '',
            'columns': [
                {'name': '', 'class': 'text-left'},
                {'name': '', 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
                {'name': 'UTILIDAD DE EJERCICIO {}'.format(year), 'class': 'text-left'},
                {'name': self._format(results['CURR_YEAR_EARNINGS']), 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
            ],
            'level': 2,
            'class': 'header_producto'
        })

        lines.append(self.empty_line)
        lines.append(self.empty_line)
        lines.append(self.empty_line)

        lines.append({
            'id': 'activo',
            'name': '',
            'columns': [
                {'name': 'TOTAL ACTIVOS', 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
                {'name': self._format(results['TA']), 'class': 'text-right total_end'},
                {'name': 'TOTAL PASIVOS MAS PATRIMONIO', 'class': 'text-right'},
                {'name': '', 'class': 'text-right'},
                {'name': self._format(results['LE']), 'class': 'text-right total_end'},
            ],
            'level': 2,
            'class': 'header_producto'
        })

        return lines

    def _format(self, value):
        return "$  {:,.2f}".format(round(value, 2))

    def _get_header(self, date):
        date_formatted = date.strftime('%d DE %B DEL %Y').upper()
        months = {'january': 'enero', 'february': 'febrero', 'march': 'marzo', 'april': 'abril', 'may': 'mayo',
                  'june': 'junio', 'july': 'julio', 'august': 'agosto', 'september': 'septiembre', 'october': 'octubre',
                  'november': 'noviembre', 'december': 'diciembre'}
        for k, v in months.items():
            date_formatted = date_formatted.upper().replace(k.upper(), v.upper())
        return [
            {
                'id': 'header_1',
                'name': '',
                'columns': [
                    {'name': self.env.company.name, 'colspan': 6, 'class': 'text-center'},
                ],
                'level': 1,
                'class': 'header_company'
            },
            {
                'id': 'header_2',
                'name': '',
                'columns': [
                    {'name': '(COMPAÑÍA SALVADOREÑA)', 'colspan': 6, 'class': 'text-center'},
                ],
                'level': 1,
                'class': 'header'
            },
            {
                'id': 'header_2',
                'name': '',
                'columns': [
                    {'name': 'BALANCE GENERAL AL {}'.format(date_formatted), 'colspan': 6, 'class': 'text-center'},
                ],
                'level': 1,
                'class': 'header_company'
            },
            {
                'id': 'header_4',
                'name': '',
                'columns': [
                    {'name': 'EXPRESADOS EN DOLARES DE LOS ESTADOS UNIDOS DE AMERICA', 'colspan': 6,
                     'class': 'text-center'},
                ],
                'level': 1,
                'class': 'header'
            },
            self.empty_line, self.empty_line, self.empty_line
        ]
