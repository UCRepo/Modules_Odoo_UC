# -*- coding: utf-8 -*-
import base64
import pytz
import requests
import math
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime


class PlanillaCCSSCuatrimestre(models.Model):
    _name="planilla.ccss.cuatrimestre"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Planilla CCSS"

    name = fields.Char(
        string="Nombre",
        required=False,
    )
    incluirTutotias = fields.Boolean(
        string="Incluir las Tutorias",
        default=False,
    )
    incluirAdicionales = fields.Boolean(
        string="Incluir los Adicionales y Ajustes",
        default=False,
    )
    cuatrimestrePlanilla_id = fields.Many2one(
        string='Cuatrimestre',
        tracking=True,
        required=True,
        comodel_name='periodo.cuatrimestre',
    )

    fechaInicioPago = fields.Date(
        string="Fecha Inicio",
        tracking=True,
        required=True,
    )

    fechaFinalPago = fields.Date(
        string="Fecha Final",
        tracking=True,
        required=True,
    )

    mes = fields.Selection(
        string='Mes',
        tracking=True,
        required=True,
        selection=[
            ('Enero','Enero'),
            ('Febrero', 'Febrero'),
            ('Marzo', 'Marzo'),
            ('Abril', 'Abril'),
            ('Mayo', 'Mayo'),
            ('Junio', 'Junio'),
            ('Julio', 'Julio'),
            ('Agosto', 'Agosto'),
            ('Septiembre', 'Septiembre'),
            ('Octubre', 'Octubre'),
            ('Noviembre', 'Noviembre'),
            ('Diciembre', 'Diciembre')
        ]
    )


    miembrosPlanilla_id = fields.One2many(
        string='Miembros',
        comodel_name='planilla.ccss.cuatrimestre.line',
        inverse_name='docentesLinea_id',
    )


    def action_done(self):
        """
            Agrega un empleado a la lista de la pre planilla
        :return:
        """
        pagoTutorias = 0
        datosCursos = self.env['cursos.docente'].search([('cuatrimestre_id','=',self.cuatrimestrePlanilla_id.id)])
        horas = 0
        deduccionEntradaTardia = 0
        deduccionSalidaTemprana = 0
        deduccionOmisionMarca = 0
        deduccionAusencia = 0
        deduccionTotal = 0
        configuraciones = self.env['configuraciones'].search([])

        semanas = math.ceil(((self.fechaFinalPago - self.fechaInicioPago).days) / 7)

        semana = int(math.ceil((((self.fechaFinalPago -self.cuatrimestrePlanilla_id.fechaInicioCuatrimestre).days + 1) / 7)))
        pago =""
        if semana <= 4:
            pago = "Primer Pago"
        elif semana > 4 and semana <= 9:
            pago = "Segundo Pago"
        elif semana > 9:
            pago = "Tercer Pago"

        for dataDocenteCursos in datosCursos:
            deduccionEntradaTardia = 0
            deduccionSalidaTemprana = 0
            deduccionOmisionMarca = 0
            deduccionAusencia = 0
            deduccionTotal = 0
            horas = 0
            if dataDocenteCursos.cursos_lines_ids.search_count([]) > 0:
                    contratoDocente = self.env['contrato.empleado'].search([('empleado_id','=',dataDocenteCursos.docente_id.id)])

                    deduccionEntradaTardia = 0
                    deduccionSalidaTemprana = 0
                    deduccionOmisionMarca = 0
                    deduccionAusencia = 0
                    deduccionTotal = 0

                    for dataAsistencia in dataDocenteCursos.asistencia_line_ids:
                        if dataAsistencia.aplicar == True and \
                                dataAsistencia.fechaCurso >= self.fechaInicioPago and \
                                dataAsistencia.fechaCurso <= self.fechaFinalPago:
                            horas += dataAsistencia.tiempoClases
                            deduccionEntradaTardia += dataAsistencia.deduccionEntradaTardia
                            deduccionSalidaTemprana += dataAsistencia.deduccionSalidaTemprana
                            deduccionOmisionMarca += dataAsistencia.deduccionOmisionMarca
                            deduccionAusencia += dataAsistencia.deduccionAusencia
                            deduccionTotal += dataAsistencia.deduccionTotal


                    idDocente = dataDocenteCursos.docente_id.id
                    nombreDocente = dataDocenteCursos.docente_id.name
                    correoDocente = dataDocenteCursos.docente_id.work_email
                    cedulaDocente = dataDocenteCursos.docente_id.identification_id
                    telefonoDocente = dataDocenteCursos.docente_id.work_phone
                    horasDocente = horas
                    tarifaDocente = self.env['contrato.empleado'].search([('empleado_id','=',dataDocenteCursos.docente_id.id)]).salario
                    horasContratoDocente = 0
                    cantidadCursosDocente = 0
                    adicionales = 0
                    rebajosNeto = 0

                    for data3 in dataDocenteCursos.cursos_lines_ids:
                        if data3.cursoActivo == True:
                            if self.env['configuraciones.cursos.taller.graduacion'].search([('codigoCurso','=',data3.codigoCurso)]):
                                if pago == "Primer Pago":
                                    horasContratoDocente += data3.cantiadadHoras
                                    cantidadCursosDocente += 1
                                elif pago == "Segundo Pago":
                                    horasContratoDocente += data3.cantiadadHoras / (float(semanas)/2)
                                    cantidadCursosDocente += 1
                            else:
                                if not self.env['configuraciones.cursos.medicina'].search([('codigoCurso', '=', data3.codigoCurso)]).planillaExterna:
                                    horasContratoDocente += data3.cantiadadHoras
                                    cantidadCursosDocente += 1
                    if self.incluirAdicionales:
                        for data in dataDocenteCursos.adicionales_lines_ids.search(
                                ['&', ('cuatrimestre_id', '=', self.cuatrimestrePlanilla_id.id),
                                 ('docente_id', '=', dataDocenteCursos.docente_id.id),
                                 ('fechaAdicional','>=',self.fechaInicioPago),
                                 ('fechaAdicional','<=',self.fechaFinalPago)]):
                            adicionales += data.totalAdicionales
                        for data in dataDocenteCursos.ajustes_lines_ids.search(
                                ['&', ('cuatrimestre_id', '=', self.cuatrimestrePlanilla_id.id),
                                 ('docente_id', '=', dataDocenteCursos.docente_id.id),
                                 ('fechaAjuste','>=',self.fechaInicioPago),
                                 ('fechaAjuste','<=',self.fechaFinalPago)]):
                            adicionales += data.total
                        for data in dataDocenteCursos.reposiciones_lines_ids.search(
                                ['&', ('cuatrimestre_id', '=', self.cuatrimestrePlanilla_id.id),
                                 ('docente_id', '=', dataDocenteCursos.docente_id.id),
                                 ('fechaRepocicion','>=',self.fechaInicioPago),
                                 ('fechaRepocicion','<=',self.fechaFinalPago)]):
                            adicionales += data.total
                        for data in dataDocenteCursos.rebajos_lines_ids.search(
                                ['&', ('cuatrimestre_id', '=', self.cuatrimestrePlanilla_id.id),
                                 ('docente_id', '=', dataDocenteCursos.docente_id.id),
                                 ('fechaRebajo','>=',self.fechaInicioPago),
                                 ('fechaRebajo','<=',self.fechaFinalPago)]):
                            rebajosNeto += data.monto

                    if self.incluirTutotias:
                        for data in dataDocenteCursos.cursos_lines_ids:
                            if (data.estadoCurso == 'Tutoria' or data.estadoCurso == "Tutoria Ext") and data.alumnos <= 3:
                                pagoTutorias += (configuraciones.tutoriasMonto /configuraciones.factor ) * data.alumnos

                    docentelinea = self.env['planilla.ccss.cuatrimestre.line'].search(
                        ['&', ("docente_id", '=', dataDocenteCursos.docente_id.id),
                         ('cuatrimestre_id', '=', dataDocenteCursos.cuatrimestre_id.id),
                         ('docentesLinea_id', '=', self.id),
                         ('pago','=',pago)])


                    if not docentelinea:
                        self.miembrosPlanilla_id = [(0, 0, {'nombreDocente': nombreDocente,
                                                            'docentesLinea_id': self.id,
                                                            'docente_id': idDocente,
                                                            'cuatrimestre_id': self.cuatrimestrePlanilla_id.id,
                                                            'correoDocente': correoDocente,
                                                            'cedulaDocente': cedulaDocente,
                                                            'telefonoDocente': telefonoDocente,
                                                            'horasDocente': horasDocente ,
                                                            'horasSemanaContratoDocente': horasContratoDocente,
                                                            'horasContratoDocente': (horasContratoDocente * float(semanas)),
                                                            'tarifaDocente': tarifaDocente,
                                                            'cantidadCursosDocente': cantidadCursosDocente,
                                                            'totalDocente': 0,
                                                            'adicionales': adicionales+pagoTutorias,
                                                            'prePlanillaAceptada': True,
                                                            'pagoEfectuado': False,
                                                            'pago': pago,
                                                            'rebajosNeto': rebajosNeto,
                                                            'cuentaBac': contratoDocente.cuentaBac,
                                                            'cuentaBacActiva': contratoDocente.cuentaBacActiva,
                                                            })]
                        pagoTutorias = 0
                    else:
                        docentelinea.nombreDocente = nombreDocente
                        docentelinea.correoDocente = correoDocente
                        docentelinea.cedulaDocente = cedulaDocente
                        docentelinea.telefonoDocente = telefonoDocente
                        docentelinea.horasDocente = horasDocente
                        docentelinea.horasSemanaContratoDocente = horasContratoDocente
                        docentelinea.horasContratoDocente = (horasContratoDocente * float(semanas))
                        docentelinea.tarifaDocente = tarifaDocente
                        docentelinea.cantidadCursosDocente = cantidadCursosDocente
                        docentelinea.adicionales = adicionales+pagoTutorias
                        docentelinea.prePlanillaAceptada = True
                        docentelinea.pago = pago
                        docentelinea.rebajosNeto = rebajosNeto
                        pagoTutorias = 0

                    self._calculosPlanilla(pago,deduccionTotal, deduccionAusencia,deduccionOmisionMarca,deduccionSalidaTemprana,deduccionEntradaTardia,contratoDocente,dataDocenteCursos.cursos_lines_ids,self.miembrosPlanilla_id )


    def createCCSSReport(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/nomina/excel_ccss_docente_detallado_report/%s' % (self.id),
            'target': 'new',
        }

    @api.model
    def create(self, vals):
        """
             Funcion que retorna el registro de la pre planilla con los cursos asignados para poder ser creado
             Evalua que el valor de warning sea False el cual en este estado significa que no se tiene ningun error en el registro para poder ser creado
        :return:
            :: retorna el registro
        """
        datos = self.env['periodo.cuatrimestre'].search([('id', '=', vals['cuatrimestrePlanilla_id'])])
        vals['name'] = 'Planilla de CSS :' + datos.name + " " + vals['mes']
        res = super(PlanillaCCSSCuatrimestre, self).create(vals)
        return res

    def _calculosPlanilla(self,pago,deduccionTotal, deduccionAusencia,deduccionOmisionMarca,deduccionSalidaTemprana,deduccionEntradaTardia,contratoDocente,cursosDocente,miembrosPlanilla_id):
        """
            Hace los calculos nesesarios para calcular le pre planilla del docente
        :param marcasDeduciones: deducciones de marca si es que existen
        :return:
        """

        CCSS = any
        renta = 0
        pagoTutorias = 0
        embargo = 0
        pensionAlimenticia = 0
        horasMD = 0
        pagoCursoMD = 0
        lineaPlanilla = miembrosPlanilla_id.search(['&',('docente_id','=',contratoDocente.empleado_id.id),('pago','=',pago),('docentesLinea_id','=',self.id)])
        calculosPlanilla = self.env['configuraciones'].search([])
        if 2==2:
            deduccionesMarcas = deduccionTotal
            for data in cursosDocente:
                if data.cursoActivo == True:
                    cursoMD = self.env['configuraciones.cursos.medicina'].search([('codigoCurso','=',data.codigoCurso)])
                    if cursoMD:
                        cantiadadHoras = 0
                        for asistencia in self.env['asistencia.docente.line'].search(['&',('cursoMarca','=',data.codigoCurso),
                                                                                      ('horarioCurso','=',data.horario),
                                                                                      ('cuatrimestre_id','=',self.cuatrimestrePlanilla_id.id),
                                                                                      ('docente_id','=',data.docente_id.id),
                                                                                      ('fechaCurso','>=',self.fechaInicioPago),
                                                                                      ('fechaCurso','<=',self.fechaFinalPago)]):
                            cantiadadHoras += asistencia.tiempoClases

                        horasMD += cantiadadHoras
                        pagoCursoMD += (cantiadadHoras) * cursoMD.tarifaCurso


            calculo = (((lineaPlanilla.horasDocente-horasMD) * lineaPlanilla.tarifaDocente))

            brutoDocente = calculo + lineaPlanilla.adicionales

            calculo += pagoCursoMD

            calculo += lineaPlanilla.adicionales

            calculo -= deduccionesMarcas

            calculo -= lineaPlanilla.rebajosNeto

            if contratoDocente.pensionado == False:
                CCSS = calculo * calculosPlanilla.CCSSNormal
            else:
                CCSS = calculo * calculosPlanilla.CCSSPensionado

            if calculo > calculosPlanilla.desde0 and calculo < calculosPlanilla.hasta0:
                renta += (calculo - calculosPlanilla.desde0) * calculosPlanilla.porciento0

            elif calculo > calculosPlanilla.desde1 and calculo < calculosPlanilla.hasta1:

                renta += (calculosPlanilla.hasta0 - calculosPlanilla.desde0) * calculosPlanilla.porciento0
                renta += (calculo - calculosPlanilla.desde1) * calculosPlanilla.porciento1

            elif calculo > calculosPlanilla.desde2 and calculo < calculosPlanilla.hasta2:

                renta += (calculosPlanilla.hasta0 - calculosPlanilla.desde0) * calculosPlanilla.porciento0
                renta += (calculosPlanilla.hasta1 - calculosPlanilla.desde1) * calculosPlanilla.porciento1
                renta += (calculo - calculosPlanilla.desde2) * calculosPlanilla.porciento2

            elif calculo > calculosPlanilla.desde3:

                renta += (calculosPlanilla.hasta0 - calculosPlanilla.desde0) * calculosPlanilla.porciento0
                renta += (calculosPlanilla.hasta1 - calculosPlanilla.desde1) * calculosPlanilla.porciento1
                renta += (calculosPlanilla.hasta2 - calculosPlanilla.desde2) * calculosPlanilla.porciento2
                renta += (calculo - calculosPlanilla.desde3) * calculosPlanilla.porciento3

            if contratoDocente.embargo:
                preCalculo  = calculo - (calculosPlanilla.salarioBase * 2 )
                if preCalculo > 1000:
                    embargo = preCalculo * calculosPlanilla.porcientoRebajoEmbargo

            calculo -= embargo

            totalDeducciones = (CCSS + renta)
            aguinaldo = (calculo) * calculosPlanilla.aguinaldo
            vacaciones = (calculo) * calculosPlanilla.vacaciones
            calculo = (calculo + aguinaldo  + vacaciones) - totalDeducciones

            if (lineaPlanilla.totalDocente - calculo) > 10 or (lineaPlanilla.totalDocente - calculo) < -10:
                lineaPlanilla.pagoEfectuado = False
                self.miembrosPlanilla_id = [(1, lineaPlanilla.id, {'totalDocente': calculo,
                                                                   'CCSSDocente': CCSS,
                                                                   'brutoDocente': brutoDocente,
                                                                   'rentaDocente': renta,
                                                                   'deducionesEntradaTardia': deduccionEntradaTardia,
                                                                   'deducionesSalidaTemprana': deduccionSalidaTemprana,
                                                                   'deducionesOmisionMarca': deduccionOmisionMarca,
                                                                   'deducionesAusencia': deduccionAusencia,
                                                                   'totalDeduccionDocente': totalDeducciones + deduccionesMarcas + embargo,
                                                                   'aguinaldoDocente': aguinaldo,
                                                                   'vacacionesDocente': vacaciones,
                                                                   'embargo': embargo,
                                                                   'cuentaBac': contratoDocente.cuentaBac,
                                                                   'cuentaBacActiva': contratoDocente.cuentaBacActiva,
                                                                   })]


class PlanillaCuatrimestreLine(models.Model):
    _name="planilla.ccss.cuatrimestre.line"
    _description = "Docente Planilla Line"


    docentesLinea_id = fields.Many2one(
        string='Docentes Linea',
        comodel_name='planilla.ccss.cuatrimestre',
        ondelete="cascade"
    )

    docente_id = fields.Many2one(
        required=False,
        comodel_name='hr.employee',
    )
    cuatrimestre_id = fields.Many2one(
        required=False,
        comodel_name='periodo.cuatrimestre',
    )

    nombreDocente = fields.Char(
        string='Nombre Docente',
    )

    correoDocente = fields.Char(
        string='Correo Docente',
    )
    cedulaDocente = fields.Char(
        string='Cedula Docente',
    )
    telefonoDocente = fields.Char(
        string='Telefono Docente',
    )
    horasDocente = fields.Float(
        digits=(2,2),
        string='Horas trabajadas ',
    )
    horasSemanaContratoDocente = fields.Float(
        digits=(2,2),
        string='Horas del Curso por Semana',
    )
    horasContratoDocente = fields.Float(
        digits=(2,2),
        string='Total de horas por X Semanas',
    )
    tarifaDocente = fields.Float(
        digits=(16,2),
        string='Tarifa por Hora'
    )
    cantidadCursosDocente = fields.Integer(
        string="Cantidad Cursos",
        required=False,
    )
    totalDocente = fields.Float(
        digits=(16,2),
        string='Total'
    )
    brutoDocente = fields.Float(
        digits=(16,2),
        string='Bruto'
    )
    CCSSDocente = fields.Float(
        digits=(16,2),
        string='CCSS'
    )
    rentaDocente = fields.Float(
        digits=(16,2),
        string='Renta'
    )
    deducionesEntradaTardia = fields.Float(
        digits=(16,2),
        string='Deduciones Entrada Tardia'
    )
    deducionesSalidaTemprana = fields.Float(
        digits=(16,2),
        string='Deduciones Salida Temprana'
    )
    deducionesOmisionMarca = fields.Float(
        digits=(16,2),
        string='Deduciones Omision Marca'
    )
    deducionesAusencia = fields.Float(
        digits=(16,2),
        string='Deduciones Ausencia'
    )
    totalDeduccionDocente = fields.Float(
        digits=(16, 2),
        string='Total Deducciones'
    )
    adicionales = fields.Float(
        digits=(16, 2),
        string="Total Adicionales" )
    aguinaldoDocente = fields.Float(
        digits=(16,2),
        string='Aguinaldo'
    )
    cesantiaDocente = fields.Float(
        digits=(16,2),
        string='Cesantia'
    )
    preavisoDocente = fields.Float(
        digits=(16, 2),
        string='Preaviso'
    )
    vacacionesDocente = fields.Float(
        digits=(16, 2),
        string='Vacaciones'
    )
    prePlanillaAceptada = fields.Boolean(
        string="Planilla aceptada",
    )
    pagoEfectuado = fields.Boolean(
        string="Pago efectuado",
    )
    prePlanillaEnviadad = fields.Boolean(
        string="Pre Planilla Enviada",
    )
    fechaCorte = fields.Date(
        string="Fecha de Corte",
        required=False,
    )
    embargo = fields.Float(
        string="Embargo",
        required=False,
    )

    rebajosNeto = fields.Float(
        string="Rebajos Netos",
        required=False,
    )
    pago = fields.Char(
        string="Pago",
        required=False,
    )
    cuentaBac = fields.Char(
        string="Cuenta BAC",
        required=False,
    )
    cuentaBacActiva = fields.Boolean(
        string="Cuenta BAC Activa",
        default = False
    )
    correoEnviado = fields.Boolean(
        string="CorreoEnviado",
        default=False
    )





