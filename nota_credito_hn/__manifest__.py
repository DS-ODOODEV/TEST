{
    'name': 'Nota de credito HN',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 1,
    'summary': 'Nota de credito GT',
    'website': 'https://www.xetechs.odoo.com',
    'author': 'Justo Rivera --> justo.rivera@xetechs.com',
    'depends': ['account',],
    'data': [
        'reports/nota_credito_template.xml',
        'reports/actions.xml',
        'views/account_move.xml'
    ],
    'installable': True,
    'application': True,
}
