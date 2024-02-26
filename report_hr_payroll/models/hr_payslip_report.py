# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class HrPayslipReport(models.Model):
    _name = 'hr.payslip.report'
    _description = "Settings Payslip Report"

    name = fields.Char('Report name', required=True, copy=True, tracking=True)
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    line_ids = fields.One2many('hr.payslip.report.lines', 'report_id', string="Report Columns")

    struct_id = fields.Many2one('hr.payroll.structure', 'Payroll Structure', required=False)
    show_wage = fields.Boolean('Show Wage', required=False, default=True)
    show_workdays = fields.Boolean('Show Workdays', required=False, default=True)

HrPayslipReport()

class HrPayslipReportLines(models.Model):
    _name = 'hr.payslip.report.lines'
    _rec_name = 'column_name'

    report_id = fields.Many2one('hr.payslip.report', required=False, ondelete='cascade')
    company_id = fields.Many2one('res.company', 'Company', related="report_id.company_id")
    column_name = fields.Char('Column Name', required=True)
    operation = fields.Selection([
        ('+', 'Sum'),
        ('-', 'Minus'),
        ('=', 'Total')], string="Operation", default="+", required=True)
    column_width = fields.Float('Column Width (cm)', required=False, default=5.00)
    rule_ids = fields.Many2many('hr.salary.rule', 'rel_report_lines_rules', 'line_id', 'rule_id', string="Salary Rules")

HrPayslipReportLines()