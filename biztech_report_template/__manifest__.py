# -*- coding: utf-8 -*-
# Part of Appjetty. See LICENSE file for full copyright and licensing details.

{
    'name': 'Clever Multiple Invoice Template',
    'version': '13.0.1.1.0',
    'author': 'Appjetty',
    'license': 'OPL-1',
    'category': 'Accounting',
    'depends': ['account', 'sale_management', 'purchase'],
    'website': 'https://www.appjetty.com',
    'description': '''Professiona Templates ,  
    Professional Report Templates , Customizable Invoice Templates , 
    Multiple Professional Invoice Templates  , Customized Invoice''',
    'summary': 'Get Diverse Invoice Templates In One Go!',
    'data': [
        'security/ir.model.access.csv',
        'data/template_data.xml',
        'views/web_widget_color_view.xml',
        'views/templates.xml',
        'views/template_report.xml',
        'views/creative_template.xml',
        'views/elegant_template.xml',
        'views/professional_template.xml',
        'views/exclusive_template.xml',
        'views/advanced_template.xml',
        'views/incredible_template.xml',
        'views/innovative_template.xml',
        'views/custom_template.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'views/invoice_view.xml',
        'views/report_extra_content_view.xml',
        'views/invoice_report_templates.xml',
    ],
    'qweb': [
        'static/src/xml/widget_color.xml',
    ],
    'external_dependencies': {
        'python': ['img2pdf', 'fpdf']
    },
    'images': ['static/description/splash-screen.png'],
    'price': 29.00,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'web_preload': True,
}
