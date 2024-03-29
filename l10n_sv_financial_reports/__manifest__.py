# -*- coding: utf-8 -*-
{
    'name': "Libros Financieros Contables -SV-",

    'summary': """Añade reportes financieros contables""",
    'description': """
Añade reportes financieros contables:
    * Libro de Partida de Diario
    """,
    'author': 'J2L Tech GT',
    'website': "https://j2ltechgt.com",
    'support': 'soporte@j2ltechgt.com',
    'category': 'Accounting',
    'version': '0.01.1',
    'depends': ['account', 'account_accountant'],
    "external_dependencies": {"python": ["xlwt"]},
    'data': [
        'views/account_move_view.xml',
        'report/reports.xml',
        'report/layout.xml',
        'report/report_account_move_tmpl.xml',
    ],
}
