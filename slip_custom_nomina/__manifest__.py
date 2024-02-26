# -*- coding: utf-8 -*-

{
    'name' :'Custom Nomina report -DevelSecurity-',
    'category': 'Accounting/Expenses',
    'author': 'Rafael Valencia',
    'sequence': 1,
    'summary': 'Nomina personalizada para Devel',
    'depends':['base_setup','account'],
    'data': [
        'security/groups.xml',
        'report/reports.xml',
        'report/custom_nomina_template_devel.xml',
    ],
    'application':True,
    'installable':True,
    'auto_install':False,
}