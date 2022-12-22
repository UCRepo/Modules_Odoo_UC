{
    'name': 'Contrato',

    'version': '1.0',

    'category': 'Recursos Humanos/Personal/Contrato',

    'summary': 'Manejo de contratos del personal',

    'sequence': -100,

    'description': "",

    'author': 'Greivin Gamboa Flores',

    'website': 'https://erp.uia.ac.cr/',

    'license': 'LGPL-3',

    'depends':[
        'hr',
    ],

    'data':[

        'security/security.xml',
        'security/ir.model.access.csv',

        'data/mail_template.xml',
        'data/contrato_cron.xml',

        'views/view_contrato_empleado.xml',
        'views/view_hr_employee.xml'
    ],

    'qweb':[],

    'installable': True,
    'application': True,
    'auto_install': True,
}