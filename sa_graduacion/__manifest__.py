{
    'name': 'Proceso de graduación',

    'version': '1.0',

    'category': 'SA/Graduación',

    'summary': 'Manejo del proceso de graduación',

    'sequence': -100,

    'description': "",

    'author': 'Greivin Gamboa Flores',

    'website': 'https://erp.uia.ac.cr/',

    'license': 'LGPL-3',

    'depends': [
        'mail',
        'hr',
        'base',
    ],

    'data':[

        # Security
        'security/security.xml',
        'security/ir.model.access.csv',

        #Data
        'data/mail_template.xml',

        #Wizards
        # 'wizard/view_sa_periodo_crear_periodo_wizard.xml',

        # Views
        'views/view_proceso_graduacion_menu.xml',
        'views/periodo_graduacion/view_periodo_graduacion.xml',
        'views/graduacion_estudiante/view_graduacion_estudiante.xml',
        'views/web/web_proceso_graduacion_templates.xml',


        'static/assets.xml',

        #reports
        'report/boleta_gadaucion_report.xml',

        'static/assets.xml',

    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}