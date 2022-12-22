# -*- coding: utf-8 -*-
import pytz
from datetime import date, timedelta, datetime
from odoo import api, fields, models, _

class PlanillaDocenteReport(models.AbstractModel):
    _name='report.nomina.report_detalles_pago_docente_id'

    @api.model
    def _get_report_values(self, docids, data):
        docente_pago_report = self.env['ir.actions.report']._get_report_from_name('nomina.report_detalles_pago_docente_id')
        holidays = self.env['cursos.docente'].browse(self.ids)

        if isinstance(data['lineaPlanilla'],str):
            data['lineaPlanilla'] = self.env['planilla.cuatrimestre.line'].search([('id','=',data['lineaPlanillaid'])])

            data['planillaPago'] = self.env['planilla.cuatrimestre'].search([('id','=',data['planillaPagoid'])])

        return {
            'doc_ids': self.ids,
            'doc_model': docente_pago_report.model,
            'docs': holidays,
            'get_docente_info': self.get_docente_info(data['lineaPlanilla']),
            'get_docente_pago_general': self.get_docente_pago_general(data['planillaPago'],data['lineaPlanilla']),
            'get_docente_info_planilla': self.get_docente_info_planilla(data['planillaPago']),
            'get_docente_cursos': self.get_docente_cursos(data['lineaPlanilla'],data['planillaPago']),
            'get_marcas_cursos':self.get_marcas_cursos(data['lineaPlanilla'],data['planillaPago']),
        }

    def get_docente_info(self,lineaPlanilla):
        return {
            'nombreDocente': lineaPlanilla.docente_id.name,
            'correoDocente': lineaPlanilla.docente_id.work_email,
            'cedulaDocente': lineaPlanilla.docente_id.identification_id,
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
        totalAlumnos = 0

        cursosDocente = self.env['cursos.docente'].search(['&',('cuatrimestre_id','=',planillaPago.cuatrimestrePlanilla_id.id),('docente_id','=',lineaPlanilla.docente_id.id)])
        configuraciones = self.env['configuraciones'].search([])
        for adicionales in cursosDocente.adicionales_lines_ids:
            if adicionales.fechaAdicional >= planillaPago.fechaInicioPago and adicionales.fechaAdicional <= planillaPago.fechaFinalPago:
                subtotal2 += adicionales.totalAdicionales
                adicionalesDic = {
                    'nombre': "Pago de "+adicionales.name + " / "+ str(adicionales.cantidad),
                    'total': "{:,}".format(adicionales.totalAdicionales),
                }
                adicionalesList.append(adicionalesDic)

        for tiposAjuste in self.env['configuraciones.ajuste.pago.line'].search([]):
            totalTipoAjuste = cursosDocente.ajustes_lines_ids.search(['&',('name','=',tiposAjuste.name),
                                                                      ('docente_id','=',lineaPlanilla.docente_id.id),
                                                                      ('fechaAjuste','>=',planillaPago.fechaInicioPago),
                                                                      ('fechaAjuste','<=',planillaPago.fechaFinalPago)])
            total = 0
            for data in totalTipoAjuste:
                total += data.total

            ajustesDic = {
                'nombre': tiposAjuste.name,
                'total': "{:,}".format(float("{:.2f}".format(total))),
            }
            ajustesList.append(ajustesDic)
            subtotal2 += total

        for tiposReposicion in self.env['configuraciones.reposiciones.line'].search([]):
            totalTipoReposicion = cursosDocente.reposiciones_lines_ids.search(['&',('name','=',tiposAjuste.name),
                                                                      ('docente_id','=',lineaPlanilla.docente_id.id),
                                                                      ('fechaRepocicion','>=',planillaPago.fechaInicioPago),
                                                                      ('fechaRepocicion','<=',planillaPago.fechaFinalPago)])
            total = 0
            for data in totalTipoReposicion:
                total += data.total
            reposicionesDic = {
                'nombre': tiposReposicion.name,
                'total': "{:,}".format(total),
            }
            reposicionesList.append(reposicionesDic)
            subtotal2 += total


        for tiposRebajo in cursosDocente.rebajos_lines_ids:
            total = 0
            subtotal2 -= tiposRebajo.monto
            rebajosDic = {
                'nombre': tiposRebajo.name,
                'total': "{:,}".format(tiposRebajo.monto),
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
        semanas = 0
        minutoPagar = 0
        horasPagar = 0
        for dataCurso in cursosDocente.cursos_lines_ids:
            pagoHasta = ''
            if dataCurso.cursoActivo == True:
                horasRealizar = 0
                if dataCurso.fechaCambioCurso != False:
                    pagoHasta =  'Pago hasta semana '+str(((dataCurso.fechaCambioCurso - cursosDocente.cuatrimestre_id.fechaInicioCuatrimestre).days) / 7)
                    semanas = str(((dataCurso.fechaCambioCurso - planillaPago.fechaInicioPago).days) / 7)

                elif dataCurso.fechaInicioPago != False:
                    pagoHasta = 'Pago desde semana ' + str((((dataCurso.fechaInicioPago - cursosDocente.cuatrimestre_id.fechaInicioCuatrimestre).days) / 7)+1)
                    semanas = str((((dataCurso.fechaInicioPago - planillaPago.fechaInicioPago).days) / 7) - 1)
                else:
                    if (dataCurso.estadoCurso == "Tutoria" or dataCurso.estadoCurso == "Tutoria Ext"):
                        hastaSemana = self.env['configuraciones.tutorias.line'].search([('numeroEstudiantes', '=', dataCurso.alumnos)])
                        if planillaPago.pago == "Primer Pago":
                            semanas = str(((planillaPago.fechaFinalPago - planillaPago.fechaInicioPago).days) / 7)

                        elif planillaPago.pago == "Segundo Pago":
                            semanas =  (hastaSemana.semanasTutoria - 4)

                        elif planillaPago.pago == "Tercer Pago" and hastaSemana.semanasTutoria > 9:
                            semanas =  (hastaSemana.semanasTutoria - 9)
                        else:
                            semanas = 0
                    else:
                        semanas = str(((planillaPago.fechaFinalPago - planillaPago.fechaInicioPago).days) / 7)



                diasCurso = []
                if dataCurso.dia1 != 'N/A':
                    diasCurso.append(dataCurso.dia1)
                if dataCurso.dia2 != 'N/A':
                    diasCurso.append(dataCurso.dia2)
                if dataCurso.dia3 != 'N/A':
                    diasCurso.append(dataCurso.dia3)

                horasRealizadas = 0
                listHorasRealizadas = list(filter(lambda x: (x.cursoMarca == dataCurso.codigoCurso) and
                                                            (x.horarioCurso == dataCurso.horario) and
                                                            (x.fechaCurso >= planillaPago.fechaInicioPago) and
                                                            (x.fechaCurso <= planillaPago.fechaFinalPago), cursosDocente.asistencia_line_ids))

                for data in listHorasRealizadas:
                    horasRealizadas += data.tiempoClases
                    horasRealizar += dataCurso.cantiadadHoras
                curso = {
                    'descripcion': dataCurso.descripcion,
                    'horario': dataCurso.horario,
                    'cantiadadHoras': dataCurso.cantiadadHoras,
                    'horasRealizar': horasRealizar,
                    'horasRealizadas': "{:.2f}".format(horasRealizadas),
                    'semanas' : round(float(semanas)),
                    'pagoHasta' : pagoHasta,
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
            if asistencia.aplicar == True and asistencia.fechaCurso >= planillaPago.fechaInicioPago and asistencia.fechaCurso <= planillaPago.fechaFinalPago:
                marcas = {
                    'marcaEntrada': asistencia.entradaClases   - timedelta(hours=6) if asistencia.entradaClases else asistencia.entradaClases,
                    'marcaSalida': asistencia.salidaClases   - timedelta(hours=6) if asistencia.salidaClases else asistencia.salidaClases,
                    'codigo': asistencia.cursoMarca,
                    'fechaCurso': asistencia.fechaCurso,
                    'horarioCurso': asistencia.horarioCurso,
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
