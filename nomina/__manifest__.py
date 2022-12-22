{
    'name': 'Nomina Profesores',

    'version': '1.0',

    'category': 'Recursos Humanos/Docentes',

    'summary': 'Manejo de las planillas de los docentes',

    'sequence': -100,

    'description': "",

    'author': 'Greivin Gamboa Flores',

    'website': 'https://erp.uc.ac.cr/',

    'license': 'LGPL-3',

    'depends':[
        'hr',
        'website'
    ],

    'data':[
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/consecutivo_contrato_cuatrimestre.xml',
        'data/mail_template.xml',
        'data/nomina_cron.xml',

        'wizard/view_nomina_cargar_asistencia_docente_wizard.xml',
        'wizard/view_nomina_generar_reporte_marcas_wizard.xml',
        'wizard/view_nomina_cargar_tesis_docent_wizard.xml',
        'wizard/view_nomina_cargar_cursos_docente_wizard.xml',
        'wizard/view_nomina_cargar_cursos_libres_docente_wizard.xml',
        'wizard/view_nomina_cargar_adicionales_wizard.xml',
        'wizard/view_nomina_cargar_justificacion_marcas_docente_wizard.xml',
        'wizard/view_nomina_cargar_ajuste_pago_docente_wizard.xml',
        'wizard/view_nomina_reenvio_descarga_reporte_pago_docente_wizard.xml',
        'wizard/view_nomina_cargar_suficiencias_docente_wizard.xml',
        # 'views/nomina_hr_employee_inherit.xml',
        'views/nomina_periodo_cuatrimestre_view.xml',
        'views/nomina_periodo_cursos_libre.xml',
        #'views/nomina_contrato_cuatrimestre_view.xml',
        'views/nomina_cursos_docente_view.xml',
        'views/nomina_cursos_libre_docente_view.xml',
        #'views/nomina_miembro_cuatrimestre_view.xml',
        'views/nomina_planilla_cuatrimestre.xml',
        'views/nomina_configuraciones_view.xml',
        'views/nomina_tesis_docente.xml',
        'views/nomina_planilla_tesis.xml',
        'views/nomina_planilla_cursos_libre_view.xml',
        # 'views/nomina_planilla_cuatrimestre_aceptados.xml',
        # 'views/nomina_planilla_cuatrimestre_rechazados.xml',
        'static/src/assets.xml',
        # 'static/src/cssload.xml',
        'views/web/webpage_nomina_aceptacion_planilla_docente.xml',
        'views/web/webpage_docentes.xml',

        'report/report_detalle_pago_docente.xml',
        'report/nomina_asistencia_docente_report.xml'
    ],

    'qweb':[],

    'installable': True,
    'application': True,
    'auto_install': True,
}