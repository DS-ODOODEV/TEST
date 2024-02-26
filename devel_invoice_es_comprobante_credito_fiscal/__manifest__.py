{
    'name': "DEVEL Comprobante Credito Fiscal ES",
    'author': 'XETECHS S.A',
    'category': 'Account Invoice',
    'summary': """Comprobante credito Fiscal""",
    'website': 'http://www.xetechs.com',
    'description': """

""",
    'version': '13.0.1.0',
    "depends": ["account",],
    "data": [
        'views/invoice_report.xml',
        'views/invoice_custom_report.xml',
        'views/factura_consumidor_final.xml',
        'views/factura_consumidor_final_report.xml',
        'views/exportacion.xml',
        'views/exportacion_report.xml',
    ],

    'images': [''],
    'installable': True,
    'application': True,
    'auto_install': False,
}