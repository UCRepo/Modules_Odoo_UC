{
    'name': 'Horario Empleados',

    'version': '1.0',

    'category': 'Recursos Humanos/Personal/Horario',

    'summary': 'Manejo de horarios del personal',

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

        'wizard/view_horario_generacion_horario.xml',

        'views/view_horario_empleado.xml',
        'views/view_hr_employee.xml',
        'views/view_horario_horario_predeterminado.xml',
    ],

    'qweb':[],

    'installable': True,
    'application': True,
    'auto_install': True,
}