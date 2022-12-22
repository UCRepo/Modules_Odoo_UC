# -*- coding: utf-8 -*-
import pytz
from datetime import date, timedelta, datetime
from odoo import api, fields, models, _

class AccionPersonalReport(models.AbstractModel):
    _name='report.uia_portal.report_accion_personal_tiempo_acumulado_id'

    @api.model
    def _get_report_values(self, docids, data):
        docente_pago_report = self.env['ir.actions.report']._get_report_from_name('uia_portal.report_accion_personal_tiempo_acumulado_id')
        return {
            'get_accion_personal_tiempo_acumulado': self.get_accion_personal_tiempo_acumulado(data['idTiempoAcumulado']),
        }

    def get_accion_personal_tiempo_acumulado(self,solicitudTiempoAcumulado):
        jefaturaRH = self.env['hr.employee'].search([('id', '=', int(self.env['ir.config_parameter'].sudo().get_param('uia_portal.empleado_id')))])
        timezoneEmeplado = pytz.timezone(solicitudTiempoAcumulado.empleado_id.resource_id.tz)
        timezoneJefatura = pytz.timezone(solicitudTiempoAcumulado.empleado_id.department_id.manager_id.resource_id.tz)
        timezoneRH = pytz.timezone(jefaturaRH.resource_id.tz)
        firmaEmpleadoFecha = pytz.utc.localize(solicitudTiempoAcumulado.fechaFirmaEmpleado).astimezone(timezoneEmeplado).replace(tzinfo=None)
        firmaJefaturaFecha = pytz.utc.localize(solicitudTiempoAcumulado.fechaFirmaJefatura).astimezone(timezoneJefatura).replace(tzinfo=None)
        firmaRHFecha = pytz.utc.localize(solicitudTiempoAcumulado.fechaFirmaRH).astimezone(timezoneRH).replace(tzinfo=None)
        entradaSalida = 'INICIANDO LABORES '+str(solicitudTiempoAcumulado.tiempoAcumuladoTomado/60)+'h DESPUES DE SU HORARIO DE ENTRADA'
        if solicitudTiempoAcumulado.inicioFinJornada == 'finJornada':
            entradaSalida = 'FINALIZANDO LABORES '+str(solicitudTiempoAcumulado.tiempoAcumuladoTomado/60)+'h DESPUES DE SU HORARIO DE SALIDA'

        return {
            'fechaEmision': date.today(),
            'nombreAdministrativo': solicitudTiempoAcumulado.empleado_id.name,
            'cedulaAdministrativo': solicitudTiempoAcumulado.empleado_id.identification_id,
            'departamentoAdministrativo': solicitudTiempoAcumulado.empleado_id.department_id.name,
            'puestoAdministrativo': solicitudTiempoAcumulado.empleado_id.job_title,
            'jefatura': solicitudTiempoAcumulado.empleado_id.department_id.manager_id.name,
            'fecha':  str(solicitudTiempoAcumulado.fechaTiempoAcumulado),
            'entradaSalida':  entradaSalida,
            'tiempoAcumuladoRestante': solicitudTiempoAcumulado.contratoEmpleado_id.tiempoAcumuladoRestante/60,
            'tiempoTomado': solicitudTiempoAcumulado.tiempoAcumuladoTomado/60,
            'firmaEmpleadoNombre': solicitudTiempoAcumulado.empleado_id.name,
            'firmaEmpleadoUsuario': solicitudTiempoAcumulado.empleado_id.work_email,
            'firmaEmpleadoFecha': datetime.strftime(firmaEmpleadoFecha,"%Y-%m-%d %H:%M"),
            'firmaJefaturaNombre': solicitudTiempoAcumulado.empleado_id.department_id.manager_id.name,
            'firmaJefaturaUsuario': solicitudTiempoAcumulado.empleado_id.department_id.manager_id.work_email,
            'firmaJefaturaFecha': datetime.strftime(firmaJefaturaFecha,"%Y-%m-%d %H:%M"),
            'firmaRHNombre': jefaturaRH.name,
            'firmaRHUsuario': jefaturaRH.work_email,
            'firmaRHFecha': datetime.strftime(firmaRHFecha,"%Y-%m-%d %H:%M"),
        }

    def get_docente_pago_general(self,planillaPago,lineaPlanilla):
        ampliacion = []
        reposicion = []
        suficiencia = []
        ajusteMontoFijo = 0
        ajusteHoras = 0
        reposicionMontoFijo = 0
        reposicionHoras = 0
        ampliacionCantidad = 0
        reposicionCantidad = 0
        suficienciaCantidad = 0
        subtotal = 0
        subtotal2 = 0
        adicionalesList =[]
        ajustesList =[]
        reposicionesList =[]
        deducionesDic = {}
        deducionesList = []
        totalTipoAjuste = 0
        totalTipoReposicion = 0
        totalTipoRebajo = 0
        rebajosList = []
        rebajosDic= {}
        rebajosNeto = 0

        cursosDocente = self.env['cursos.docente'].search(['&',('cuatrimestre_id','=',planillaPago.cuatrimestrePlanilla_id.id),('docente_id','=',lineaPlanilla.docente_id.id)])

        for adicionales in cursosDocente.adicionales_lines_ids:
            subtotal2 += adicionales.totalAdicionales
            adicionalesDic = {
                'nombre': "Pago de "+adicionales.name + " / "+ str(adicionales.cantidad),
                'total': "{:,}".format(adicionales.totalAdicionales),
            }
            adicionalesList.append(adicionalesDic)

        for tiposAjuste in self.env['configuraciones.ajuste.pago.line'].search([]):
            totalTipoAjuste = cursosDocente.ajustes_lines_ids.search(['&',('name','=',tiposAjuste.name),('docente_id','=',lineaPlanilla.docente_id.id)])
            total = 0
            for data in totalTipoAjuste:
                total += data.total
                ajustesDic = {
                    'nombre': tiposAjuste.name,
                    'total': "{:,}".format(total),
                }
                ajustesList.append(ajustesDic)
                subtotal2 += total

        for tiposReposicion in self.env['configuraciones.reposiciones.line'].search([]):
            totalTipoReposicion = cursosDocente.reposiciones_lines_ids.search(['&',('name','=',tiposReposicion.name),('docente_id','=',lineaPlanilla.docente_id.id)])
            total = 0
            for data in totalTipoReposicion:
                total += data.total
            reposicionesDic = {
                'nombre': tiposReposicion.name,
                'total': "{:,}".format(total),
            }
            reposicionesList.append(reposicionesDic)
            subtotal2 += total


        for tiposRebajo in self.env['configuraciones.rebajos.line'].search([]):
            totalTipoRebajo = cursosDocente.rebajos_lines_ids.search(['&',('name','=',tiposRebajo.name),('docente_id','=',lineaPlanilla.docente_id.id)])
            total = 0
            for data in totalTipoRebajo:
                total += data.monto
            rebajosDic = {
                'nombre': tiposRebajo.name,
                'total': "{:,}".format(total),
            }
            rebajosList.append(rebajosDic)

        subtotal = "{:.2f}".format((lineaPlanilla.tarifaDocente * lineaPlanilla.horasDocente))
        subtotal2 = "{:.2f}".format((float(subtotal)+subtotal2)-(lineaPlanilla.deducionesEntradaTardia+lineaPlanilla.deducionesSalidaTemprana+lineaPlanilla.deducionesOmisionMarca+lineaPlanilla.deducionesAusencia))
        embargo = "{:.2f}".format(lineaPlanilla.embargo)
        return {
            'adicionalesList': adicionalesList,
            'ajustesList': ajustesList,
            'reposicionesList':reposicionesList,
            'vacacionesDocente': "{:,}".format(lineaPlanilla.vacacionesDocente),
            'preavisoDocente': "{:,}".format(lineaPlanilla.preavisoDocente),
            'cesantiaDocente': "{:,}".format(lineaPlanilla.cesantiaDocente),
            'aguinaldoDocente': "{:,}".format(lineaPlanilla.aguinaldoDocente),
            'totalDeduccionDocente': "{:,}".format(lineaPlanilla.totalDeduccionDocente),
            'totalDocente': "{:,}".format(lineaPlanilla.totalDocente),
            'subTotal': "{:,}".format(float(subtotal)),
            'subTotal2': "{:,}".format(float(subtotal2)),
            'CCSSDocente': "{:,}".format(lineaPlanilla.CCSSDocente),
            'renta': "{:,}".format(lineaPlanilla.rentaDocente),
            'deducionesEntradaTardia': "{:,}".format(lineaPlanilla.deducionesEntradaTardia),
            'deducionesSalidaTemprana': "{:,}".format(lineaPlanilla.deducionesSalidaTemprana),
            'deducionesOmisionMarca': "{:,}".format(lineaPlanilla.deducionesOmisionMarca),
            'deducionesAusencia': "{:,}".format(lineaPlanilla.deducionesAusencia),
            'embargo': "{:,}".format(float(embargo)),
            'rebajosNeto': rebajosList,
        }

    def get_docente_info_planilla(self, planillaPago):
        return {
            'cuatrimestre': planillaPago.cuatrimestrePlanilla_id.name,
            'fechaInicio': planillaPago.fechaInicioPago,
            'fechaFinal': planillaPago.fechaFinalPago,
        }

    def get_docente_cursos(self,lineaPlanilla,planillaPago):
        datosMarcasVirtuales = self.env['hr.attendance'].search([('employee_id','=',lineaPlanilla.docente_id.id)])
        cursosDocente = self.env['cursos.docente'].search(['&', ('cuatrimestre_id', '=', planillaPago.cuatrimestrePlanilla_id.id),('docente_id', '=', lineaPlanilla.docente_id.id)])
        user_tz = pytz.timezone(self.env.user.tz)

        curso = {}
        cursos = []
        semanas = any
        minutoPagar = 0
        horasPagar = 0
        for dataCurso in cursosDocente.cursos_lines_ids:
            diasCurso = []
            horasRealizadas : any
            horasRealizadas = 0
            if dataCurso.dia1 != 'N/A':
                diasCurso.append(dataCurso.dia1)
            if dataCurso.dia2 != 'N/A':
                diasCurso.append(dataCurso.dia2)
            if dataCurso.dia3 != 'N/A':
                diasCurso.append(dataCurso.dia3)
            semanas = str(((planillaPago.fechaFinalPago - planillaPago.fechaInicioPago).days) / 7)
            curso = {
                'descripcion': dataCurso.descripcion,
                'horario': dataCurso.horario,
                'cantiadadHoras': dataCurso.cantiadadHoras,
                'horasRealizadas': horasRealizadas,
                'semanas' : round(float(semanas)),
            }
            cursos.append(curso)
            horasPagar = 0
            minutoPagar = 0
        return  cursos

    def get_marcas_cursos(self,lineaPlanilla,planillaPago):
        asistencias = self.env['cursos.docente'].search(['&',('cuatrimestre_id','=',planillaPago.cuatrimestrePlanilla_id.id),('docente_id','=',lineaPlanilla.docente_id.id)])
        marcaslist = []
        marcas = {}
        for asistencia in asistencias.asistencia_line_ids:
            if asistencia.aplicar == True:
                marcas = {
                    'marcaEntrada': asistencia.entradaClases,
                    'marcaSalida': asistencia.salidaClases,
                    'codigo': asistencia.cursoMarca,
                    'horasCurso' : asistencia.tiempoClases,
                    'estado': asistencia.estado
                }
                marcaslist.append(marcas)

        return  marcaslist

    def get_fechas_curso_docente(self,fechaInicioPago,fechaFinalPago,diasCurso):

        curr = fechaInicioPago
        end = fechaFinalPago
        step = timedelta(1)
        fechasMarcas = []

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





