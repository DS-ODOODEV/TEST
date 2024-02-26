# -*- coding: utf-8 -*-

{
    'name': 'Sale Order Title on Tree View',
    'version': '13.0.1.0.0',
    'category': 'Sales',
    'license': 'AGPL-3',
    'summary': 'Adds a project_title field on tree view sales order',
    'description': """
Adds a project_title field on tree view sales order
====================

This module only adds a field *project_title* on sale.order (to be displayed in tree view).

    """,
    'author': 'Xetechs',
    'website': 'http://www.xetechs.com',
    'depends': ['sale','customized_invoice'],
    'data': ['sale_view.xml'],
    'installable': True,
}
