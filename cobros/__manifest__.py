{
    'name': 'Cobros',

    'version': '1.0',

    'category': 'Recursos Humanos/Docentes',

    'summary': 'Manejo de las planillas de los docentes',

    'sequence': -100,

    'description': "",

    'author': 'Greivin Gamboa Flores',

    'website': 'https://erp.uia.ac.cr/',

    'license': 'LGPL-3',

    'depends':[
        'hr',
        'nomina',
        'website'
    ],

    'data':[
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/mail_template.xml',
        'data/cobros_cron.xml',

        'wizard/view_cobros_asignar_letras_wizard.xml',
        'wizard/view_cobros_reporte_estado_letra.xml',

        'views/view_periodos_pago.xml',
        'views/view_cobros_menu.xml',
        'views/cobros_configuraciones.xml',


    ],

    'qweb':[],

    'installable': True,
    'application': True,
    'auto_install': True,
}