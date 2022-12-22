{
    'name': 'UC Poliza',

    'version': '1.0',

    'category': 'Recursos Humanos/Personal',

    'summary': 'Manejo de polizas de los estudiantes',

    'sequence': -100,

    'description': "",

    'author': 'Greivin Gamboa Flores',

    'website': 'https://erp.uia.ac.cr/',

    'license': 'LGPL-3',

    'depends':[
        'hr'
    ],

    'data':[
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/mail_template.xml',

        'static/assets.xml',

        'wizard/view_poliza_generar_reporte_beneficiarios_wizard.xml',

        'views/web/web_poliza_form_estudiante_view.xml',
        'views/views_menus.xml',
        'views/view_poliza_dashboard.xml',
        'views/view_poliza_configuraciones.xml',
    ],

    'qweb':[],

    'installable': True,
    'application': True,
    'auto_install': True,
}