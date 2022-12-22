{
    'name': 'Planilla Administrativa',

    'version': '1.0',

    'category': 'Recursos Humanos/Personal',

    'summary': 'Manejo de planillas de personal',

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
        'data/planillaAdministrativa_cron.xml',


        'wizard/view_planillaPersonal_generarEmpleadosPlanilla.xml',
        'wizard/view_planilla_administrativa_generar_asistencia_wizard.xml',
        'wizard/view_planilla_administrativa_reporteria_wizard.xml',

        'views/view_planillaPersonal_menuRoot.xml',
        'views/PeriodoPago/view_planillaPersonal_periodoPago.xml',
        'views/EmpleadoPlanilla/view_planillaPersonal_empleadoPlanilla.xml',
        'views/Configuraciones/view_planillaPersonal_configuraciones_view.xml',
        'views/PrePlanilla/view_planillaPersonal_prePlanilla.xml',


        'report/report_planilla_detalle_pago_administrativo.xml',



    ],

    'qweb':[],

    'installable': True,
    'application': True,
    'auto_install': True,
}