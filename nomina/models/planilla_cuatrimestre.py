# -*- coding: utf-8 -*-
import base64
import pytz
import requests
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime


class PlanillaCuatrimestre(models.Model):
    _name="planilla.cuatrimestre"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Planilla Cuatrimestre"

    urlEmail = fields.Char(string="", required=False, readonly=True)
    docenteNombre = fields.Char(string="", required=False, readonly=True)

    name = fields.Char(string="Nombre", required=False, )


    cuatrimestrePlanilla_id = fields.Many2one(
        string='Cuatrimestre',
        tracking=True,
        required=True,
        comodel_name='periodo.cuatrimestre',
    )

    fechaInicioPago = fields.Date(string="Fecha Inicio",tracking=True,required=True, )

    fechaFinalPago = fields.Date(string="Fecha Final", tracking=True, required=True, )

    semanasPago = fields.Char(digits=(1,0), string="Semanas de pago", required=False, )

    pago = fields.Char( string="Pago", required=False, )

    warning = fields.Boolean(default=False, store=False)

    miembrosPlanilla_id = fields.One2many(
        string='Miembros',
        comodel_name='planilla.cuatrimestre.line',
        inverse_name='docentesLinea_id',
    )

    def get_marcas_cursos(self,docente_id,planilla_id,cuatrimestre_id,contratoDocente):

        """
            Optiene las deducciones segun las marcas de los docentes
        :param docente_id: ID de docente
        :param planilla_id: ID de planialla
        :param cuatrimestre_id: ID de cuatriemstre
        :return: Diccionario con los datos de las deducciones si existen
        """
        datosDocenteCursos= self.env['cursos.docente'].search(['&',('cuatrimestre_id', '=', cuatrimestre_id),('docente_id', '=', docente_id) ])
        datosCursos = self.env['cursos.docente.line'].search([('cursos_id', '=', datosDocenteCursos.id)])
        datosMarcasVirtuales = self.env['hr.attendance'].search([('employee_id','=',docente_id)])
        datosPlanillaDocente = self.env['planilla.cuatrimestre'].search([('id', '=', planilla_id)])
        user_tz = pytz.timezone(self.env.user.tz)

        marcasDeduciones = {}
        marcaslist = []
        horas = 0
        deducionesEntradaTardia = 0
        deducionesSalidaTemprana = 0
        deducionesOmisionMarca = 0
        deducionesAusencia = 0
        for dataCurso in datosCursos:
            if dataCurso.cantiadadHoras > 0:
                diasCurso = []
                if dataCurso.dia1 != 'N/A':
                    diasCurso.append(dataCurso.dia1)
                if dataCurso.dia2 != 'N/A':
                    diasCurso.append(dataCurso.dia2)
                if dataCurso.dia3 != 'N/A':
                    diasCurso.append(dataCurso.dia3)

                fechasMarcas = self.get_fechas_curso_docente(datosPlanillaDocente.fechaInicioPago,datosPlanillaDocente.fechaFinalPago,diasCurso)

                for dataFechasMarcas in fechasMarcas:
                    ausencia = True
                    for dataMarcasVirtuales in datosMarcasVirtuales:
                        fecha = pytz.utc.localize(dataMarcasVirtuales.check_in).astimezone(user_tz).date()
                        if dataFechasMarcas == fecha:
                            ausencia = False
                            marcaEntrada = pytz.utc.localize(dataMarcasVirtuales.check_in).astimezone(user_tz)
                            marcaSalida = pytz.utc.localize(dataMarcasVirtuales.check_out).astimezone(user_tz)

                            marcaEntradaSistema = datetime.strptime(marcaEntrada.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                            marcaSalidaSistema = datetime.strptime(marcaSalida.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

                            if dataMarcasVirtuales.worked_hours >= dataCurso.cantiadadHoras:

                                if marcaSalidaSistema.hour == 0:
                                    deducionesOmisionMarca = (contratoDocente.salario * 1.5)
                                    horas += dataCurso.cantiadadHoras
                                else:
                                    horas += dataMarcasVirtuales.worked_hours
                            else:
                                entradaHora = marcaEntradaSistema.hour - int(dataCurso.horaInicio)
                                entradaMinuto = marcaEntradaSistema.minute - int(dataCurso.minutoInicio)
                                totalEntrada = ((entradaHora*60)+entradaMinuto)

                                salidaHora =  (int(dataCurso.horaFinal)+12) - marcaSalidaSistema.hour
                                salidaMinuto = int(dataCurso.minutoFinal) - marcaSalidaSistema.minute
                                totalSalida = ((salidaHora*60)+salidaMinuto)

                                if totalEntrada > 1:
                                    deducionesEntradaTardia += (contratoDocente.salario * 0.5)
                                    horas += dataMarcasVirtuales.worked_hours
                                elif totalEntrada > 35:
                                    deducionesEntradaTardia += contratoDocente.salario
                                    horas += dataMarcasVirtuales.worked_hours

                                if totalSalida > 1:
                                    deducionesSalidaTemprana += (contratoDocente.salario* 0.5)
                                    horas += dataMarcasVirtuales.worked_hours
                                elif totalSalida > 35:
                                    deducionesSalidaTemprana += contratoDocente.salario
                                    horas += dataMarcasVirtuales.worked_hours


                    if ausencia == True:
                        deducionesAusencia += contratoDocente.salario * dataCurso.cantiadadHoras
                        horas -= dataCurso.cantiadadHoras

        marcasDeduciones = {
            'horas':horas,
            'deducionesEntradaTardia': deducionesEntradaTardia,
            'deducionesSalidaTemprana': deducionesSalidaTemprana,
            'deducionesOmisionMarca': deducionesOmisionMarca,
            'deducionesAusencia':deducionesAusencia
        }
        return  marcasDeduciones

    def get_fechas_curso_docente(self,fechaInicioPago,fechaFinalPago,diasCurso):
        """
            Optiene las fechas de marca segun los dias y los rangos de fechaas que se le envian
        :param fechaInicioPago:  Fecha inicial de pago
        :param fechaFinalPago:  Fecha final de pago
        :param diasCurso:  dias  que el profesor da cursos por semana
        :return: retorna un a lista de fechas
        """
        curr = fechaInicioPago
        end = fechaFinalPago
        step = timedelta(1)
        fechasMarcas = []
        dia = any

        for dataDia in diasCurso:
            dia:0
            if dataDia == 'L':
                dia = 0
            elif dataDia == 'K':
                dia = 1
            elif dataDia == 'M':
                dia = 2
            elif dataDia == 'J':
                dia = 3
            elif dataDia == 'V':
                dia = 4
            elif dataDia == 'S':
                dia = 5
            elif dataDia == 'D':
                dia = 6

            while curr <= end-timedelta(days=1):
                if curr.weekday() == dia:
                    fechasMarcas.append(curr)
                curr += step
        return fechasMarcas

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

        semanas = str(((self.fechaFinalPago - self.fechaInicioPago).days) / 7)
        self.semanasPago = semanas

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
                            cursoMD = self.env['configuraciones.cursos.medicina'].search([('codigoCurso', '=', data3.codigoCurso)])
                            if self.env['configuraciones.cursos.taller.graduacion'].search([('codigoCurso','=',data3.codigoCurso)]):
                                if self.pago == "Primer Pago":
                                    horasContratoDocente += data3.cantiadadHoras
                                    cantidadCursosDocente += 1
                            elif cursoMD:
                                if cursoMD.planillaExterna == False:
                                    horasContratoDocente += data3.cantiadadHoras
                                    cantidadCursosDocente += 1
                            elif (data3.estadoCurso == "Tutoria" or data3.estadoCurso == "Tutoria Ext"):
                                hastaSemana = self.env['configuraciones.tutorias.line'].search([('numeroEstudiantes', '=', data3.alumnos)])
                                if self.pago == "Primer Pago":
                                    cant = self.env['configuraciones.tutorias.semana.line'].search_count(['&',('tutoria_id', '=', hastaSemana.id),('semanaMarca','<=',4)])
                                    if cant == 2:
                                        horasContratoDocente += data3.cantiadadHoras/cant
                                    else:
                                        horasContratoDocente += data3.cantiadadHoras
                                    cantidadCursosDocente += 1
                                elif self.pago == "Segundo Pago":
                                    cant = self.env['configuraciones.tutorias.semana.line'].search_count(['&', ('tutoria_id', '=', hastaSemana.id), ('semanaMarca', '>', 4),('semanaMarca', '<', 10)])
                                    horasContratoDocente += (data3.cantiadadHoras * (hastaSemana.semanasTutoria - 4)) / (float(self.semanasPago))
                                    cantidadCursosDocente += 1
                                elif self.pago == "Tercer Pago" and hastaSemana.semanasTutoria > 9:
                                    cant = self.env['configuraciones.tutorias.semana.line'].search_count(['&', ('tutoria_id', '=', hastaSemana.id), ('semanaMarca', '>=', 10)])
                                    horasContratoDocente += (data3.cantiadadHoras * (hastaSemana.semanasTutoria - 9)) / (float(self.semanasPago))
                                    cantidadCursosDocente += 1
                            else:
                                horasContratoDocente += data3.cantiadadHoras
                                cantidadCursosDocente += 1


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

                    docentelinea = self.env['planilla.cuatrimestre.line'].search(
                        ['&', ("docente_id", '=', dataDocenteCursos.docente_id.id),
                         ('cuatrimestre_id', '=', dataDocenteCursos.cuatrimestre_id.id),
                         ('docentesLinea_id', '=', self.id),
                         ('pago','=',self.pago)])


                    if not docentelinea:
                        self.miembrosPlanilla_id = [(0, 0, {'nombreDocente': nombreDocente,
                                                            'docentesLinea_id': self.id,
                                                            'docente_id': idDocente,
                                                            'cuatrimestre_id': self.cuatrimestrePlanilla_id.id,
                                                            'correoDocente': correoDocente,
                                                            'cedulaDocente': cedulaDocente,
                                                            'telefonoDocente': telefonoDocente,
                                                            'horasDocente': horasDocente,
                                                            'horasSemanaContratoDocente': horasContratoDocente,
                                                            'horasContratoDocente': (horasContratoDocente * float(self.semanasPago)),
                                                            'tarifaDocente': tarifaDocente,
                                                            'cantidadCursosDocente': cantidadCursosDocente,
                                                            'totalDocente': 0,
                                                            'adicionales': adicionales+pagoTutorias,
                                                            'prePlanillaAceptada': True,
                                                            'pagoEfectuado': False,
                                                            'pago': self.pago,
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
                        docentelinea.horasContratoDocente = (horasContratoDocente * float(self.semanasPago))
                        docentelinea.tarifaDocente = tarifaDocente
                        docentelinea.cantidadCursosDocente = cantidadCursosDocente
                        docentelinea.adicionales = adicionales+pagoTutorias
                        docentelinea.prePlanillaAceptada = True
                        docentelinea.pago = self.pago
                        docentelinea.rebajosNeto = rebajosNeto
                        pagoTutorias = 0

                    self._calculosPlanilla(deduccionTotal, deduccionAusencia,deduccionOmisionMarca,deduccionSalidaTemprana,deduccionEntradaTardia,contratoDocente,dataDocenteCursos.cursos_lines_ids,self.miembrosPlanilla_id )

    def get_url(self):
        return self.urlEmail

    def get_docenteNombre(self):
        return self.docenteNombre

    def action_create_report(self):
        """
            Crea los datos nesesarios para poder crear el reporte de preplanilla y lo envia por correo
        :return: retorna el correo para pdoer se enviado
        """
        self.id
        ICPSudo = self.env['ir.config_parameter'].sudo()
        for data in self.miembrosPlanilla_id:
            if data.totalDocente > 0 and data.correoDocente != False and data.correoEnviado == False:
                datas = {
                    'lineaPlanilla': data,
                    'planillaPago': self,
                }
                report_template_id = self.env.ref('nomina.report_detalles_pago_docente')._render_qweb_pdf(self,data=datas)
                data_record = base64.b64encode(report_template_id[0])
                ir_values = {
                    'name': "Pre Planilla "+data.nombreDocente+".pdf",
                    'type': 'binary',
                    'datas': data_record,
                    'store_fname': data_record,
                    'mimetype': 'application/x-pdf',
                }
                datosCorreo = {
                    'docenteNombre': data.nombreDocente,
                    'fechaInicioPago': str(self.fechaInicioPago),
                    'fechaFinalPago': self.fechaFinalPago,
                }
                data_id = self.env['ir.attachment'].create(ir_values)
                template_id = self.env.ref('nomina.email_docente_preplanilla').id
                template = self.env['mail.template'].browse(template_id)
                template.attachment_ids = [(6, 0, [data_id.id])]
                email_values = {'email_to': data.correoDocente,
                                'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                                'subject': data.nombreDocente+' Pre Planilla del: '+str(self.fechaInicioPago)+" a "+str(self.fechaFinalPago)
                                }
                template.with_context(datosCorreo=datosCorreo).send_mail(self.id, email_values=email_values,force_send=True)
                template.attachment_ids = [(3, data_id.id)]
                data.correoEnviado = True

    def createXLSXReport(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/sale/excel_report/%s' % (self.id),
            'target': 'new',
        }

    def createXLSXReportDetallado(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/nomina/excel_pago_docente_detallado_report/%s' % (self.id),
            'target': 'new',
        }

    def createXLSXReportPrediccion(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/nomina/excel_prediccion_pago_docente_report/%s' % (self.id),
            'target': 'new',
        }

    def createXLSXReportJustificacionMarcas(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/nomina/excel_reporte_marcas_justificadas/%s' % (self.id),
            'target': 'new',
        }

    def createXLSXReportComparativoPago(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/nomina/excel_comparativo_pago/%s' % (self.id),
            'target': 'new',
        }

    def descargar_reporte_asistencia(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'nomina.generar.reporte.marcas.wizard',
            'target': 'new',
        }

    def descargar_reporte_docentes_falta_pago(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/nomina/excel_docentes_falta_pago/%s' % (self.id),
            'target': 'new',
        }

    def reenvio_descarga_colilla(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'nomina.reenvio.descarga.reporte.pago.docente.wizard',
            'context': {
                'default_planillaCuatrimestre_id': self.id,
            },
            'target': 'new',
        }

    def get_reporte_pago_UC(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/nomina/get_reporte_pago_UC_report/%s' % (self.id),
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
        if vals['warning'] != True:
            datos = self.env['periodo.cuatrimestre'].search([('id', '=', vals['cuatrimestrePlanilla_id'])])
            vals['name'] = 'Planilla del Cuatrimestre :' + datos.name + " " + vals['pago']
            res = super(PlanillaCuatrimestre, self).create(vals)
            return res
        else:
            raise ValidationError(" No se puede guardar el registro ya que esta cuatrimestre tiene todos los pagos asignados")

    @api.onchange('cuatrimestrePlanilla_id')
    def _onchangeCuatrimestrePlanillaID(self):
        """
         Al detectar un cambio en el field cuatrimestrePlanilla_id para poder asignar el pago al cuatrimestre
        :return:
        """
        datoCuatrimestre = self.env['periodo.cuatrimestre'].search([('id', '=', self.cuatrimestrePlanilla_id.id)])
        datoPago = self.env['planilla.cuatrimestre'].search([('cuatrimestrePlanilla_id','=',self.cuatrimestrePlanilla_id.id)])
        if self.cuatrimestrePlanilla_id.id != False:
            if self.env['planilla.cuatrimestre'].search(['&',('cuatrimestrePlanilla_id','=',self.cuatrimestrePlanilla_id.id),('pago','=','Primer Pago')]) \
                    and not self.env['planilla.cuatrimestre'].search(['&',('cuatrimestrePlanilla_id','=',self.cuatrimestrePlanilla_id.id),('pago','=','Segundo Pago')]):
                self.pago = "Segundo Pago"
                self.fechaInicioPago = datoCuatrimestre.fechaInicioSegundoPago
                self.fechaFinalPago = datoCuatrimestre.fechaFinSegundoPago
                self.semanasPago = str(((self.fechaFinalPago - self.fechaInicioPago).days) / 7)
                self.warning = False
            elif self.env['planilla.cuatrimestre'].search(['&',('cuatrimestrePlanilla_id','=',self.cuatrimestrePlanilla_id.id),('pago','=','Segundo Pago')]) \
                    and not self.env['planilla.cuatrimestre'].search(['&',('cuatrimestrePlanilla_id','=',self.cuatrimestrePlanilla_id.id),('pago','=','Tercer Pago')]) :
                self.pago = "Tercer Pago"
                self.fechaInicioPago = datoCuatrimestre.fechaInicioTercerPago
                self.fechaFinalPago = datoCuatrimestre.fechaFinTercerPago
                self.semanasPago = str(((self.fechaFinalPago - self.fechaInicioPago).days) / 7)
                self.warning = False
            else:
                self.pago = "Primer Pago"
                self.fechaInicioPago = datoCuatrimestre.fechaInicioPrimerPago
                self.fechaFinalPago = datoCuatrimestre.fechaFinPrimerPago
                self.semanasPago = str(((self.fechaFinalPago - self.fechaInicioPago).days) / 7)
                self.warning = False

    @api.onchange('filtroNombre')
    def onchangefiltroNombre(self):
        res = {}
        res['domain'] = [('id','=',7904)]
        return res

    def _calculosPlanilla(self,deduccionTotal, deduccionAusencia,deduccionOmisionMarca,deduccionSalidaTemprana,deduccionEntradaTardia,contratoDocente,cursosDocente,miembrosPlanilla_id):
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
        lineaPlanilla = miembrosPlanilla_id.search(['&',('docente_id','=',contratoDocente.empleado_id.id),('pago','=',self.pago),('docentesLinea_id','=',self.id)])
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
            # cesantia = (calculo) * calculosPlanilla.cesantia
            # preaviso = (calculo) * calculosPlanilla.preaviso
            vacaciones = (calculo) * calculosPlanilla.vacaciones
            calculo = (calculo + aguinaldo + vacaciones) - totalDeducciones

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
    _name="planilla.cuatrimestre.line"
    _description = "Docente Planilla Line"


    docentesLinea_id = fields.Many2one(
        string='Docentes Linea',
        comodel_name='planilla.cuatrimestre',
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





