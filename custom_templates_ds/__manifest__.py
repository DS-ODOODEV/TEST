# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Custom Report Template -DEVELSECURITY-',
    'version': '1.0',
    'category': 'Accounting/Expenses',
    'sequence': 1,
    'summary': 'Custom Report Template -DEVELSECURITY-',
    'description': """
Custom Report Template -DEVELSECURITY-
============================
""",
    'website': 'https://www.xetechs.odoo.com',
    'depends': ['base_setup', 'account'],
    'data': [
        'security/groups.xml',
        'views/account_invoice_view.xml',
        'reports/reports.xml',
        'reports/report_invoice_srl.xml',
        'reports/report_invoice_hn.xml',
        'reports/report_comprobante_sv.xml',
        'reports/report_exportacion_sv.xml',
        'reports/report_factura_sv.xml',
        'reports/nota_de_credito_ds_sv.xml',
        'reports/report_factura_ds_sv.xml',
        'reports/report_comprobante_ds_sv.xml',

    ],
    'installable': True,
    'application': True,
}
