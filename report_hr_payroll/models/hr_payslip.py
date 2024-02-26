# -*- coding:utf-8 -*-

import babel
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

import xlwt
import base64
from io import BytesIO
from odoo.tools.misc import xlsxwriter
from PIL import Image

import logging
_logger = logging.getLogger(__name__)


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'


    #Relation Fields
    report_id = fields.Many2one('hr.payslip.report', 'Report Type', required=True, copy=False, default=lambda self: self.env.company.report_id)

    #Binary
    file_name = fields.Char('Nombre archivo', size=32)
    file = fields.Binary('Archivo', filters='.xls')

    def recompute_payslip(self):
        for rec in self:
            if not rec.slip_ids:
                raise UserError(_("There aren't payslips to recompute."))
            for slip in rec.slip_ids:
                slip.compute_sheet()
        return True

    def get_header(self):
        for rec in self:
            lines = []
            if not rec.report_id:
                raise UserError(_('There is payslip report configurated on company settings.'))
            #lines.append('Departamento/Empleado')
            #if rec.report_id.show_wage:
            #    lines.append('Días')
            #if rec.report_id.show_workdays:
            #    lines.append('Salario Base')
            for line in rec.report_id.line_ids:
                lines.append(line.column_name)
            return lines

    def print_report_payroll(self):
        self.ensure_one()
        if not self.slip_ids:
            raise UserError(_("There aren't Payslip to generate report."))
        if not self.report_id:
            raise UserError(_('There is payslip report configurated on company settings.'))
        headers = self.get_header()
        values = self.generate_values(slips=self.slip_ids, report=self.report_id)
        datas = {
            'company_name': self.company_id.name,
            'report_title': (('Planilla de beneficios a empleados correspondiente del %s al %s') %(self.date_start.strftime("%d/%m/%Y"), self.date_end.strftime("%d/%m/%Y"))),
            'currency_name': self.company_id.currency_id.currency_unit_label,
            'report_type': 'Reporte de Nóminas',
            'headers': headers,
            'values': values,
            'docs': self,
        }
        return self.env.ref('report_hr_payroll.action_report_hr_payroll').report_action(self, data=datas)


    def action_generate_excel(self):
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        company = self.env.company
        for rec in self:
            if not rec.slip_ids:
                raise UserError(_("There aren't Payslip to generate report."))
            if not rec.report_id:
                raise UserError(_('There is payslip report configurated on company settings.'))
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output, {
                'in_memory': True,
                'strings_to_formulas': False,
            })
            company_tittle_style = workbook.add_format({'align': 'left', 'font_name': 'Arial', 'font_size': 12, 'bold': True})
            company_subtittle_style = workbook.add_format({'align': 'left', 'font_name': 'Arial', 'font_size': 10, 'bold': True})
            user_date_style = workbook.add_format({'align': 'left', 'font_name': 'Arial', 'font_size': 9, 'bold': False})
            titulos_principales_style = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'font_name': 'Arial', 'font_size': 10, 'bold': True, 'border': 1})
            row_depto_style = workbook.add_format({'align': 'left', 'font_name': 'Arial', 'font_size': 8, 'bold': True, 'underline': True})
            row_text_style = workbook.add_format({'align': 'left', 'font_name': 'Arial', 'font_size': 8, 'bold': False, 'underline': False, 'left': 1, 'right': 1})
            row_days_style = workbook.add_format({'align': 'center', 'font_name': 'Arial', 'font_size': 8, 'bold': False, 'underline': False, 'left': 1, 'right': 1})
            row_amount_style = workbook.add_format({'num_format': '#,##0.00', 'align': 'right', 'font_name': 'Arial', 'font_size': 8, 'bold': False, 'underline': False, 'left': 1, 'right': 1})
            row_total_text_style = workbook.add_format({'align': 'center', 'font_name': 'Arial', 'font_size': 8, 'bold': True, 'underline': False, 'border': 1})
            row_total_style = workbook.add_format({'num_format': '#,##0.00', 'align': 'right', 'font_name': 'Arial', 'font_size': 8, 'bold': True, 'underline': False, 'border': 1})
            #date_value_style = workbook.add_format({'num_format': 'dd/mm/yy', 'border': 1, 'font_name': 'Arial', 'font_size': 12, 'bold': False})
            #amount_value_style = workbook.add_format({'num_format': '$#,##0', 'border': 1, 'font_name': 'Arial', 'font_size': 12, 'bold': False})
            #Titulos
            sheet = workbook.add_worksheet("Hoja de Socios")
            values = self.generate_values(slips=rec.slip_ids, report=rec.report_id)
            #Tittles
            len_ids = len(rec.report_id.line_ids.ids)
            x_header = 0
            if rec.report_id.show_workdays:
                x_header = 1
            if rec.report_id.show_wage:
                x_header = 2
            sheet.merge_range(0, 1, 0, (len_ids + x_header ), company.name, company_tittle_style)
            sheet.merge_range(1, 1, 1, (len_ids + x_header ), (("Planilla de beneficios a empleados correspondiente del %s al %s") %(rec.date_start.strftime('%d/%m/%y'), rec.date_end.strftime('%d/%m/%y'))), company_subtittle_style)
            sheet.merge_range(2, 1, 2, (len_ids + x_header ), (("Expresada en %s ") %(company.currency_id.currency_unit_label)), company_subtittle_style)
            sheet.merge_range(3, 1, 3, (len_ids + x_header ), ("Planilla Regular"), company_subtittle_style)
            sheet.write(4, ((len_ids + x_header) - 2), (("Generado por: %s") %(self.env.user.name)), user_date_style)
            sheet.write(5, ((len_ids + x_header) - 2), (("Tiempo: %s") %(fields.Datetime.now().strftime('%d/%M/%Y, %H:%M:%S'))), user_date_style)
            if company and company.logo:
                company_image = BytesIO(base64.b64decode(company.logo))
                x_scale = 5/50.0
                y_scale = 10/145.00
                sheet.insert_image(0, 0, "image.png", {'image_data': company_image, 'x_scale': x_scale, 'y_scale': y_scale})
            #Excel Headers
            y = 8
            x = 0
            sheet.set_row(y, 30)
            sheet.set_column(0, 0, 26.75)
            sheet.write(y, 0, 'Departamento/Empleado', titulos_principales_style)
            #Condicion para mostrar columnas Dia Trabajado/Salario Base
            if rec.report_id.show_workdays:
                x += 1
                sheet.set_column(x, x, 15)
                sheet.write(y, x, 'Días', titulos_principales_style)
            if rec.report_id.show_wage:
                x += 1
                sheet.set_column(x, x, 15)
                sheet.write(y, x, 'Salario Base', titulos_principales_style)
        
            for col in rec.report_id.line_ids:
                x += 1
                #sheet.col(x).width = 4000
                col_width = col.column_width / 0.25
                sheet.set_column(y, x, col_width)
                sheet.write(y, x, col.column_name, titulos_principales_style)
            x = 0
            if rec.report_id and rec.report_id.show_workdays:
                x += 1
            if rec.report_id and rec.report_id.show_wage:
                x += 1
            total = {}
            sum_wage = 0.00
            for row in values:
                y += 1
                if row.get('type', False) == 'depto':
                    #sheet.col(0).width = 7000
                    sheet.write(y, 0, row.get('depto', ""), row_depto_style)
                if row.get('type', False) == 'line':
                    #sheet.col(0).width = 7000
                    sheet.write(y, 0, row.get('depto', False), row_text_style)
                    #sheet.col(1).width = 4000
                    x = 0
                    if rec.report_id and rec.report_id.show_workdays:
                        x += 1
                        sheet.write(y, x, row.get('days', False), row_days_style)
                    #sheet.col(2).width = 4000
                    if rec.report_id and rec.report_id.show_wage:
                        x += 1
                        sheet.write(y, x, row.get('wage', False), row_amount_style)
                    #x = 0
                    #if company.report_id and company.report_id.show_workdays:
                    #    x = 1
                    #if company.report_id and company.report_id.show_wage:
                    #    x = 2
                    rx = 0
                    for line in row.get('colums', []):
                        x += 1
                        rx += 1
                        key = 'col' + str(rx)
                        #sheet.col(x).width = 4000
                        sheet.write(y, x, line[key], row_amount_style)
                if row.get('type', "") == 'subtotal':
                    #sheet.col(0).width = 7000
                    sheet.write(y, 0, '', row_total_text_style)
                    #sheet.col(1).width = 4000
                    #sheet.write(y, 1, '', row_total_text_style)
                    #sheet.col(2).width = 4000
                    #sheet.write(y, 2, row.get('wage', 0.00), row_total_style)
                    sum_wage += row.get('wage', 0.00)
                    x = 0
                    if rec.report_id and rec.report_id.show_workdays:
                        x += 1
                        sheet.write(y, x, '', row_total_text_style)
                    if rec.report_id and rec.report_id.show_wage:
                        x += 1
                        sheet.write(y, x, row.get('wage', 0.00), row_total_style)
                    rx = 0
                    for col in rec.report_id.line_ids:
                        x += 1
                        rx += 1
                        key = 'col' + str(rx)
                        sum_value = sum(row[key])
                        #sheet.col(x).width = 4000
                        sheet.write(y, x, sum_value, row_total_style)
                        #Total Slip
                        if key not in total:
                            total[key] = []
                        total[key].append(sum_value)
            #Inserte Total Payslip
            y += 2
            #sheet.col(0).width = 7000
            sheet.write(y, 0, 'TOTAL', row_total_text_style)
            #sheet.col(1).width = 4000
            #sheet.write(y, 1, '', row_total_text_style)
            #sheet.col(2).width = 4000
            #sheet.write(y, 2, sum_wage, row_total_style)
            tx = 0
            if rec.report_id and rec.report_id.show_workdays:
                tx += 1
                sheet.write(y, tx, '', row_total_text_style)
            if rec.report_id and rec.report_id.show_wage:
                tx += 1
                sheet.write(y, tx, sum_wage, row_total_style)
            trx = 0
            for col in rec.report_id.line_ids:
                tx += 1
                trx += 1
                key = 'col' + str(trx)
                total_value = sum(total[key])
                #sheet.col(tx).width = 4000
                sheet.write(y, tx, total_value, row_total_style)
            #Guardado de binario en campo del wizard
            workbook.close()
            output.seek(0)
            generated_file = base64.encodebytes(output.read())
            output.close()
            rec.write({'file_name': 'nominas.xlsx', 'file': generated_file })
            return {
                'type': 'ir.actions.act_url',
                'url': 'web/content/?model=hr.payslip.run&field=file&download=true&id=%s&filename=nominas.xlsx' % (rec.id),
                'target': 'new',
            }

    def generate_values(self, slips=None, report=None):
        res = []
        header = {'type': 'header', 'depto': 'Departamento/Empleado', 'days': 'Días'}
        depto = {}
        lines = {}
        colums = {}
        items = []
        y = 0
        values = self.group_by_depto(slips=slips)
        item = 0
        subtotal = total = {}
        for k, v in values.items():
            lines['type'] = "depto"
            lines['depto'] = k.name
            lines['days'] = ""
            lines['wage'] = 0.00
            res.append(lines)
            lines = {}
            subtotal = {}
            subitems = []
            sum_wage = 0.00
            for slip in v:
                lines['type'] = 'line'
                lines['depto'] = slip.employee_id.name
                lines['days'] = 0.00
                lines['wage'] = slip.contract_id.wage
                sum_wage += slip.contract_id.wage
                subitem = 0
                colums = {}
                items = []
                subitems = []
                for col in report.line_ids:
                    colums = {}
                    subitem += 1
                    kk = 'col' + str(subitem)
                    col_value = sum([x.total for x in slip.line_ids.filtered(lambda s: s.salary_rule_id.id in col.rule_ids.ids)])
                    colums[kk] = col_value
                    #Sum by key
                    if kk not in subtotal:
                        subtotal[kk] = []
                    subtotal[kk].append(col_value)
                    items.append(colums)
                lines['colums'] = items
                res.append(lines)
                lines = {}
            #Create new item in res
            subtotal['type'] = "subtotal"
            subtotal['depto'] = ""
            subtotal['days'] = ""
            subtotal['wage'] = sum_wage
            res.append(subtotal)
        return res
    
    def group_by_depto(self, slips=None):
        grouped_result = {}
        if slips:            
            if len(slips.filtered(lambda x: len(x.contract_id.department_id) == 0)):
                raise UserError(_("Es requerido el departamento en los contratos."))
            grouped_result = {}
            for slip in slips.filtered(lambda x: x.state != 'cancel').sorted(key=lambda x: x.contract_id.department_id.name):
                if slip.contract_id.department_id not in grouped_result:
                    grouped_result[slip.contract_id.department_id] = []
                grouped_result[slip.contract_id.department_id].append(slip)
        return grouped_result

HrPayslipRun()
