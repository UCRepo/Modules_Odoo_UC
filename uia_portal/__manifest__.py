{
    'name': 'Portal Users',

    'version': '1.0',

    'category': 'Recursos Humanos/Personal',

    'summary': 'Manejo de portal de usuarios web',

    'sequence': -100,

    'description': "",

    'author': 'Greivin Gamboa Flores',

    'website': 'https://erp.uia.ac.cr/',

    'license': 'LGPL-3',

    'depends':[
        'hr'
    ],

    'data':[

        # Security

        #Data
        'data/mail_template.xml',

        #Wizards

        # Views
        'views/portal_templates.xml',
        'views/portal_configuraciones_view.xml',
        # Static
        'static/assets.xml',

        #reports
        'report/report_accion_personal_vacaciones.xml',
        'report/report_accion_personal_tiempo_acumulado.xml',

    ],

    'qweb':[
    ],

    'installable': True,
    'application': True,
    'auto_install': True,
}