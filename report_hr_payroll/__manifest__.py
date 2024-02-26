# -*- coding: utf-8 -*-
{
    'name': "HR Payroll Report (Excel)",
    'category': 'Generic Modules/Human Resources',
    'version': '14.0.0.3',
    'author': "BoostechCR",
    'website': "https://www.boostechcr.com",
    'summary': 'HR Payroll Report (Excel)',
    'description': "",
    'depends': ['base','hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payslip_view.xml',
        'views/res_config_settings_views.xml',
        'wizard/wizard_report_hr_slips_view.xml',
        'report/layouts.xml',
        'report/report_hr_payroll_tmpl.xml',
        'report/reports.xml',
    ],
    'sequence': 1,
}
