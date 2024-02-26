# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

import xlwt
import base64
from io import BytesIO
from odoo.tools.misc import xlsxwriter
from PIL import Image

class WizardFinancialReports(models.TransientModel):
    _name = 'wizard.financial.reports'
    _description = "Wizard Financial Reports"

    
    #General Fields for all financial reports
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company)
    journal_ids = fields.Many2many('account.journal', 'rel_wizar_account_journal', 'wizard_id', 'account_journal_id', 'Journals', required=True)
    date_from = fields.Date('Date From', required=True, default=lambda *a: time.strftime('%Y-%m-01'))
    date_to = fields.Date('Date To', required=True, default=str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10])
    type_book = fields.Selection([
        ('journal_ledger', 'Journal Ledger'),
        ('general_ledger', 'General Ledger'),
        ('trial_balance', 'Trial Balance')], string="Financial Report Type", required=True, default="journal_ledger", readonly=True)
    type_report = fields.Selection([
        ('pdf', 'PDF'),
        ('xls', 'XLS')],string="Report Type", required=True, default="pdf")
    type_entries = fields.Selection([
        ('posted', 'Only Posted'),
        ('all', 'All')], string='Type Entries', default='posted')
    page_number = fields.Integer('Folio', required=False, default=1)

    #Binary fields
    file_name = fields.Char('File Name', size=32)
    file = fields.Binary('File')

    def generate_journal_entries(self, domain=None):
        if domain:
            moves = []
            lines = []
            total_debit = total_credit = 0.0
            moves_ids = self.env['account.move'].search(domain, order='date asc')
            for move in moves_ids:
                lines = []
                res = {
                    'name': move.name,
                    'date': move.date.strftime("%d/%m/%Y"),
                    'lines': [],
                }
                for line in move.line_ids.sorted(key=lambda l: l.debit > 0.00):
                    line_res = {
                        'account_code': line.account_id.code,
                        'account_name': line.account_id.name,
                        'debit': line.debit or 0.00,
                        'credit': line.credit or 0.00,
                    }
                    lines.append(line_res)
                    total_debit += line.debit or 0.00
                    total_credit += line.credit or 0.00
                if lines:
                    res.update({
                        'lines': lines,
                    })
                    moves.append(res)
            return moves, total_debit, total_credit
    
    def print_journal_ledger(self):
        self.ensure_one()
        domain = [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('company_id', '=', self.company_id.id)]
        if self.journal_ids:
            domain.append(('journal_id', 'in', self.journal_ids.ids))
        if self.type_entries == 'posted':
            domain.append(('state', '=', 'posted'))
        if self.type_entries == 'all':
            domain.append(('state', 'in', ('draf', 'posted', 'cancel')))
        values, total_debit, total_credit = self.generate_journal_entries(domain=domain)
        datas = {
            'values': values,
            'company': self.company_id.id,
            'company_name': self.company_id.name,
            'company_vat': self.company_id.vat,
            'report': 'LIBRO DIARIO',
            'dates': (("PERIODO: DEL %s AL %s") %(self.date_from.strftime("%d/%m/%Y"), self.date_to.strftime("%d/%m/%Y"))),
            'folio': self.page_number,
            'total_debit': total_debit,
            'total_credit': total_credit,
        }
        return self.env.ref('l10n_gt_financial_reports.report_journal_ledger_book').report_action(self, data=datas)


    def print_journal_ledger_excel(self):
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        company = self.env.company
        for rec in self:
            domain = [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('company_id', '=', self.company_id.id)]
            if self.journal_ids:
                domain.append(('journal_id', 'in', self.journal_ids.ids))
            if self.type_entries == 'posted':
                domain.append(('state', '=', 'posted'))
            if self.type_entries == 'all':
                domain.append(('state', 'in', ('draf', 'posted', 'cancel')))
            values, sum_debit, sum_credit = rec.generate_journal_entries(domain=domain)
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output, {
                'in_memory': True,
                'strings_to_formulas': False,
            })
            company_tittle_style = workbook.add_format({'align': 'center', 'font_name': 'Arial', 'font_size': 12, 'bold': True})
            company_subtittle_style = workbook.add_format({'align': 'center', 'font_name': 'Arial', 'font_size': 10, 'bold': True})
            header_left_style = workbook.add_format({'left': 1, 'top': 1, 'bottom': 1, 'align': 'center', 'font_name': 'Arial', 'font_size': 10, 'bold': True})
            header_center_style = workbook.add_format({'top': 1, 'bottom': 1,'align': 'center', 'font_name': 'Arial', 'font_size': 10, 'bold': True})
            header_right_style = workbook.add_format({'right': 1, 'top': 1, 'bottom': 1,'align': 'center', 'font_name': 'Arial', 'font_size': 10, 'bold': True})
            entrie_header_style = workbook.add_format({'align': 'left', 'font_name': 'Arial', 'font_size': 10, 'bold': False})
            row_text_style = workbook.add_format({'align': 'left', 'font_name': 'Arial', 'font_size': 8, 'bold': False, 'underline': False, 'left': 1, 'right': 1})
            row_text_style = workbook.add_format({'align': 'left', 'font_name': 'Arial', 'font_size': 8, 'bold': False, 'underline': False})
            row_amount_style = workbook.add_format({'num_format': '#,##0.00', 'align': 'right', 'font_name': 'Arial', 'font_size': 8, 'bold': False, 'underline': False})
            row_total_text_style = workbook.add_format({'align': 'center', 'font_name': 'Arial', 'font_size': 8, 'bold': True, 'underline': False})
            row_total_style = workbook.add_format({'num_format': '#,##0.00', 'align': 'right', 'font_name': 'Arial', 'font_size': 8, 'bold': True, 'underline': False, 'top':1, 'bottom': 1})
            #Titulos
            sheet = workbook.add_worksheet("Libro Diario")
            y = 0
            sheet.set_column(0, 0, 15)
            sheet.set_column(1, 1, 40)
            sheet.set_column(2, 2, 15)
            sheet.set_column(3, 3, 15)
            sheet.merge_range(0, 3, 0, y, rec.company_id.name, company_tittle_style)
            sheet.merge_range(1, 3, 1, y, "LIBRO DIARIO" , company_subtittle_style)
            sheet.merge_range(2, 3, 2, y, (("PERIODO del %s al %s") %(rec.date_from.strftime('%d/%m/%y'), rec.date_to.strftime('%d/%m/%y'))), company_subtittle_style)
            y += 5
            sheet.write(y, 0, "CUENTA", header_left_style)
            sheet.write(y, 1, "DESCRIPCION DE LA CUENTA", header_center_style)
            sheet.write(y, 2, "DEBE", header_center_style)
            sheet.write(y, 3, "HABER", header_right_style)
            #iteracion para los journal entries
            for val in values:
                y +=1
                sheet.write(y, 0, (('Poliza No.: %s') %(val.get('name', ''))), entrie_header_style)
                sheet.write(y, 1, val.get('date', ''), entrie_header_style)
                total_debit = total_credit = 0.00
                for line in val.get('lines', []):
                    y += 1
                    sheet.write(y, 0, line.get('account_code', ''), row_text_style)
                    sheet.write(y, 1, line.get('account_name', ''), row_text_style)
                    sheet.write(y, 2, line.get('debit', 0.00), row_amount_style)
                    sheet.write(y, 3, line.get('credit', 0.00), row_amount_style)
                    total_debit += line.get('debit', 0.00)
                    total_credit += line.get('credit', 0.00)
                y += 1
                sheet.write(y, 1, '*TOTAL*', row_total_text_style)
                sheet.write(y, 2, total_debit, row_total_style)
                sheet.write(y, 3, total_credit, row_total_style)
                y += 2
            y += 1
            sheet.write(y, 1, '*TOTAL*', row_total_text_style)
            sheet.write(y, 2, sum_debit, row_total_style)
            sheet.write(y, 3, sum_credit, row_total_style)

            #Guardado de binario en campo del wizard
            workbook.close()
            output.seek(0)
            generated_file = base64.encodebytes(output.read())
            output.close()
            rec.write({'file_name': 'libro_diario.xlsx', 'file': generated_file })
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/?model=wizard.financial.reports&field=file&download=true&id=%s&filename=libro_diario.xlsx' % (rec.id),
                'target': 'new',
            }

WizardFinancialReports()