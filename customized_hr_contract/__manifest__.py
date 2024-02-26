# -*- coding: utf-8 -*-

{
    'name': "ADD Customized contratos",
    'summary' : "Modulo agrega a hr_contracts, campos para poder realizar descuentos en la nomina",
    'author': "Rafael Valencia",
    'website': "",
    'secuence':5,
    'depends':['base', 'base_setup', 'hr_contract','hr_payroll'],
    'data':[
        'data/hr_contract_data.xml',
        'views/hr_contract_view.xml',

    ],
    'demo':[],
    'qweb':[],
    'application':True,
    'installable':True,
    'auto_install':False,
}