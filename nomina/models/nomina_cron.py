# -*- coding: utf-8 -*-
from datetime import date, timedelta, datetime
from odoo.http import request
from odoo.tools.misc import xlsxwriter
import requests
import pytz
import json
import math
import base64
import io
from odoo import api, fields, models, _
class CronsNomina(models.Model):
    _name = "nomina.cron"
    _inherit = 'mail.thread'

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

    @api.model
    def _envio_correo_marca_tardia_docente(self):
        """
            Cron para poder evaluar segun el dia actual si existen docentes que no marcaran la entrada a clases y si es asi se manda un correo
                a sobre el reporte de dichas marcas faltantes
        :return:
        """
        today = date.today()
        user_tz = pytz.timezone(self.env.user.tz)
        ICPSudo = self.env['ir.config_parameter'].sudo()
        listDocentes = []

        if today.weekday() == 0:
            dia = 'L'
        elif today.weekday() == 1:
            dia = 'K'
        elif today.weekday() == 2:
            dia = 'M'
        elif today.weekday() == 3:
            dia = 'K'
        elif today.weekday() == 4:
            dia = 'K'
        elif today.weekday() == 5:
            dia = 'S'
        elif today.weekday() == 6:
            dia = 'D'

        cuatrimestreClases = self.env['periodo.cuatrimestre'].search(['&',('fechaInicioCuatrimestre','<=',today),('fechaFinCuatrimestre','>=',today)])

        docentesClases = self.env['cursos.docente.line'].search([('cuatrimestre_id','=',cuatrimestreClases.id)])

        for dataCursos in docentesClases:
            if dataCursos.dia1 == dia or dataCursos.dia2 == dia or dataCursos.dia3 == dia:

                fechaActual = (datetime.strptime(str(today-timedelta(2)) + " " + str(dataCursos.horaInicio) + ":" + str(dataCursos.minutoInicio) + ":00", "%Y-%m-%d %H:%M:%S"))+timedelta(hours=7)
                datosMarcasVirtuales = self.env['hr.attendance'].search([('employee_id', '=', dataCursos.idDocente),('check_in','=',fechaActual)])

                if not datosMarcasVirtuales :
                    hora = datetime.today()
                    marcaEntrada = pytz.utc.localize(datetime.today()).astimezone(user_tz)
                    entradaHora = marcaEntrada.hour - int(dataCursos.horaInicio)
                    entradaMinuto = marcaEntrada.minute - int(dataCursos.minutoInicio)
                    totalAtraso = ((entradaHora * 60) + entradaMinuto)
                    if totalAtraso >= 15:
                        dic = {
                            'curso' : dataCursos.name,
                            'horario' : dataCursos.horario,
                            'docente': dataCursos.cursos_id.docente_id.name,
                        }
                        listDocentes.append(dic)

        if len(listDocentes) != 0:
            template_id = self.env.ref('nomina.email_irregularidad_marcas_docentes').id
            template = self.env['mail.template'].browse(template_id)
            email_values = {'email_to': "Greivin Andrey Gamboa Flores "+"<ggamboaf@uia.ac.cr>",
                            'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                            'subject': 'Reporte de Cursos del dia '+str(today)
                            }
            self.correoEnviado = True
            template.with_context(listDocentes=listDocentes).send_mail(self.id, email_values=email_values, force_send=True)

    @api.model
    def _get_cambio_curso(self):
        user_tz = pytz.timezone(self.env.user.tz)
        indexDia = pytz.utc.localize(datetime.today()).astimezone(user_tz).weekday()
        fechaActual = pytz.utc.localize(datetime.today()).astimezone(user_tz).date() + timedelta(days=(6 - indexDia))
        return  fechaActual

    @api.model
    def _agregar_cursos_docente(self):
        periodo = any
        res = any
        cantiadadHoras = any
        cantiadadHorasSemana = any
        cursosDict = {}
        cursosList = []
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('nomina.urlWSOdoo')+'/api/CursosDocenteUC/getCursosDocente'
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)

        if anno.month >= 1 and anno.month <= 4:
            periodo = 1
        elif anno.month >= 5 and anno.month <= 8:
            periodo = 2
        elif anno.month >= 9 and anno.month <= 12:
            periodo = 3

        cuatrimestre = self.env['periodo.cuatrimestre'].search(['&',('year','=',str(anno.year)),('decripcion','=',str(periodo)+"Q")])

        if cuatrimestre:
            for dataDocente in self.env['hr.employee'].search([('department_id.name', '=', "Docentes")]):

                cursosDocente = self.env['cursos.docente'].search(
                    ['&', ('docente_id', '=', dataDocente.id), ('cuatrimestre_id', '=', cuatrimestre.id)])
                dataJSon = {
                    'DocenteCedula': dataDocente.identification_id,
                    'Anno': self.cuatrimestre_id.year,
                    'Periodo': self.cuatrimestre_id.decripcion.replace('Q', ''),
                }
                header = {
                    'Content-Type': 'application/json',
                    'Accept': 'text/plain'
                }
                response = requests.post(url, headers=header, json=dataJSon, verify=False)

                if not cursosDocente:
                    if response.status_code == 200:
                        if 2 > 1:
                            vals = {
                                'docente_id': dataDocente.id,
                                'cuatrimestre_id': cuatrimestre.id,
                                'warning': False,
                                'name': dataDocente.name + " " + cuatrimestre.name
                            }
                            res = self.env['cursos.docente'].sudo().create(vals)
                            for data in response.json()['data']:
                                cursoActivo = True
                                if (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext") and data[
                                    'matriculados'] <= 3:
                                    cantiadadHoras = 0
                                    cantiadadHorasSemana = 0
                                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext") and \
                                        data['matriculados'] == 4:
                                    cantiadadHoras = 2
                                    cantiadadHorasSemana = 2
                                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext") and \
                                        data['matriculados'] == 5:
                                    cantiadadHoras = 2
                                    cantiadadHorasSemana = 2
                                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext") and \
                                        data['matriculados'] == 6:
                                    cantiadadHoras = 3
                                    cantiadadHorasSemana = 3
                                else:
                                    cantiadadHoras = data['horasCurso']
                                    cantiadadHorasSemana = data['horasCurso']

                                if data['estadoCurso'] == 'TRASLADAR' or data['estadoCurso'] == 'No Impartido':
                                    cursoActivo = False

                                if self.env['configuraciones.cursos.medicina'].search(
                                        [('codigoCurso', '=', data['codigoCurso'])]):
                                    cursoActivo = False

                                res.cursos_lines_ids = [(0, 0, {'cursos_id': res.id,
                                                                'docente_id': dataDocente.id,
                                                                'cuatrimestre_id': cuatrimestre.id,
                                                                'name': self.env['configuraciones.cursos'].search(
                                                                    [('codigoCurso', '=', data['codigoCurso'])]).name,
                                                                'descripcion': self.env[
                                                                    'configuraciones.cursos'].search([('codigoCurso',
                                                                                                       '=', data[
                                                                                                           'codigoCurso'])]).descripcion,
                                                                'codigoCurso': data['codigoCurso'],
                                                                'cantiadadHoras': cantiadadHoras,
                                                                'cantiadadHorasSemana': cantiadadHorasSemana,
                                                                'horario': data['horario'],
                                                                'dia1': data['dia1'],
                                                                'dia2': "N/A",
                                                                'dia3': "N/A",
                                                                'horaInicio': data['horaInicio'],
                                                                'minutoInicio': data['minutoInicio'],
                                                                'ampmInicio': data['ampmInicio'],
                                                                'horaFinal': data['horaFinal'],
                                                                'minutoFinal': data['minutoFinal'],
                                                                'ampmFinal': data['ampmFinal'],
                                                                'alumnos': data['matriculados'],
                                                                'estadoCurso': data['estadoCurso'],
                                                                'estadoActa': data['estadoActa'],
                                                                'cursoActivo': cursoActivo,
                                                                })]

                else:
                    self._actualizar_cursos_docente(cursosDocente, response, cuatrimestre)

            self._envio_correo_horarios_erroneos()
            self._envio_correo_cursos_deshabilitados()
            self._envio_correo_cursos_choques()

    @api.model
    def _actualizar_cursos_docente(self,cursosDocente,response):
        cantiadadHoras = any
        cantiadadHorasSemana = any
        cursosDict = {}
        cursosList = []
        ICPSudo = self.env['ir.config_parameter'].sudo()
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)

        if response.status_code == 200:

            for curso in cursosDocente.cursos_lines_ids:
                if curso.fechaCambioCurso ==  False:
                    curso.fechaCambioCurso = self._get_cambio_curso()

            for data in response.json()['data']:
                cursoActivo = True

                if (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext" ) and data['matriculados'] <=3:
                    cantiadadHoras = 0
                    cantiadadHorasSemana = 0
                    cursoActivo = False
                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext" ) and data['matriculados'] == 4:
                    cantiadadHoras = 2
                    cantiadadHorasSemana = 2
                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext" ) and data['matriculados'] == 5:
                    cantiadadHoras = 2
                    cantiadadHorasSemana = 2
                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext" )and data['matriculados'] == 6:
                    cantiadadHoras = 3
                    cantiadadHorasSemana = 3
                else:
                    cantiadadHoras = data['horasCurso']
                    cantiadadHorasSemana = data['horasCurso']

                curso = list(filter(lambda  x: (x.dia1 == data['dia1']) and
                                               (x.horario == data['horario']),cursosDocente.cursos_lines_ids))

                if curso:
                    curso[0].estadoActa = data['estadoActa']
                    curso[0].cantiadadHoras = cantiadadHoras
                    curso[0].cantiadadHorasSemana = cantiadadHorasSemana
                    curso[0].cursoActivo = True
                    curso[0].fechaCambioCurso = None
                    if curso[0].estadoCurso != data['estadoCurso']:
                        curso[0].estadoCurso = data['estadoCurso']
                        if data['estadoCurso'] == 'TRASLADAR':
                            curso[0].cursoActivo = False
                    elif data['estadoCurso'] == 'TRASLADAR':
                        curso[0].cursoActivo = False
                    elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext" ) and data['matriculados'] < 4:
                        curso[0].cursoActivo = False
                else:
                    cursosDocente.cursos_lines_ids = [(0, 0, {'cursos_id': cursosDocente.id,
                                                              'docente_id': cursosDocente.docente_id.id,
                                                              'cuatrimestre_id': cursosDocente.cuatrimestre_id.id,
                                                              'name': self.env['configuraciones.cursos'].search([('codigoCurso', '=', data['codigoCurso'])]).name,
                                                              'descripcion': self.env['configuraciones.cursos'].search([('codigoCurso','=',data['codigoCurso'])]).descripcion,
                                                              'codigoCurso': data['codigoCurso'],
                                                              'cantiadadHoras': cantiadadHoras,
                                                              'cantiadadHorasSemana': cantiadadHorasSemana,
                                                              'horario': data['horario'],
                                                              'dia1': data['dia1'],
                                                              'dia2': "N/A",
                                                              'dia3': "N/A",
                                                              'horaInicio': data['horaInicio'],
                                                              'minutoInicio': data['minutoInicio'],
                                                              'ampmInicio': data['ampmInicio'],
                                                              'horaFinal': data['horaFinal'],
                                                              'minutoFinal': data['minutoFinal'],
                                                              'ampmFinal': data['ampmFinal'],
                                                              'alumnos': data['matriculados'],
                                                              'estadoCurso': data['estadoCurso'],
                                                              'estadoActa': data['estadoActa'],
                                                              'cursoActivo': cursoActivo,
                                                              'fechaInicioPago': self._get_cambio_curso(),
                                                              })]

    @api.model
    def _agregar_adicionales_docente(self):
        periodo = any
        res = any
        cantiadadHoras = any
        cantiadadHorasSemana = any
        planillaActual = any
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('nomina.urlWSOdoo')+'/api/CursosDocenteUC/getAdicionalesDocente'
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)

        if anno.month >= 1 and anno.month <= 4:
            periodo = 1
        elif anno.month >= 5 and anno.month <= 8:
            periodo = 2
        elif anno.month >= 9 and anno.month <= 12:
            periodo = 3

        cuatrimestre = self.env['periodo.cuatrimestre'].search(['&',('year','=',str(anno.year)),('decripcion','=',str(periodo)+"Q")])

        fechaActual = anno.date()
        planilla = self.env['planilla.cuatrimestre'].search(['&',('cuatrimestrePlanilla_id', '=', cuatrimestre.id),('fechaInicioPago','<',fechaActual),('fechaFinalPago','>',fechaActual)])

        if cuatrimestre:
            for dataDocente in self.env['hr.employee'].search([('department_id','=',"Docentes")]):

                cursosDocente = self.env['cursos.docente'].search(['&',('docente_id','=',dataDocente.id),('cuatrimestre_id','=',cuatrimestre.id)])

                dataJSon = {
                    'DocenteCedula': dataDocente.identification_id,
                    'Anno': anno.year,
                    'Periodo': periodo,
                    'FechaInicioPago': str(planilla.fechaInicioPago),
                    'FechaFinPago': str(planilla.fechaFinalPago),
                }
                header = {
                    'Content-Type': 'application/json',
                    'Accept': 'text/plain'
                }
                response = requests.post(url, headers=header, json=dataJSon, verify=False)

                if response.status_code == 200:
                    if response.json()['data']:
                        for data in response.json()['data']:
                            adicional = self.env['configuraciones.adicionales.line'].search([('name','=',data['tipoAdicional'])])
                            cursosDocente.adicionales_lines_ids = [(0, 0, {'adicionalId': adicional.id,
                                                                           'name': data['tipoAdicional'],
                                                                           'sinPrestaciones': adicional.montoSinPrestaciones,
                                                                           'cantidad': data['cantidad'],
                                                                           'totalAdicionales': data['monto'],
                                                                           'cuatrimestre_id': cursosDocente.cuatrimestre_id.id,
                                                                           'docente_id': cursosDocente.docente_id.id,
                                                                           'pagoEfectuado': False,
                                                                           'fechaAdicional': data['fechaAdicional']
                                                                           })]

    @api.model
    def _cargar_asistencia_docente(self):
        periodo = any
        res = any
        cantiadadHoras = any
        cantiadadHorasSemana = any
        planillaActual = any
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('nomina.urlWSOdoo')+'/api/CursosDocenteUC/getAsistenciaDocente'
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)


        ausencia = True


        if anno.month >= 1 and anno.month <= 4:
            periodo = 1
        elif anno.month >= 5 and anno.month <= 8:
            periodo = 2
        elif anno.month >= 9 and anno.month <= 12:
            periodo = 3

        cuatrimestre = self.env['periodo.cuatrimestre'].search(['&',('year','=',str(anno.year)),('decripcion','=',str(periodo)+"Q")])



        fechaActual = anno.date()
        planilla = self.env['planilla.cuatrimestre'].search(['&',('cuatrimestrePlanilla_id', '=', cuatrimestre.id),('fechaInicioPago','<=',fechaActual),('fechaFinalPago','>=',fechaActual)])

        if cuatrimestre:
            for dataDocente in self.env['hr.employee'].search([('department_id','=',"Docentes")]):

                if not planilla:
                    continue

                contrato = self.env['contrato.empleado'].search([('empleado_id','=',dataDocente.id)])
                cursosDocente = self.env['cursos.docente'].search(['&',('docente_id','=',dataDocente.id),('cuatrimestre_id','=',cuatrimestre.id)])
                for dataCursos in cursosDocente.cursos_lines_ids:


                    if dataCursos.cursoActivo == True:

                        if self.env['configuraciones.cursos.taller.graduacion'].search([('codigoCurso', '=', dataCursos.codigoCurso)]):
                            if planilla.pago == 'Segundo Pago':
                                fechaCalculoAsistencia = planilla.fechaInicioPago + timedelta(weeks=2)
                                if fechaActual >= fechaCalculoAsistencia:
                                    continue

                        tipoDeduccion = ""
                        deduccionEntradaTardia = 0
                        deduccionSalidaTemprana = 0
                        deduccionOmisionMarca = 0
                        deduccionAusencia = 0
                        deduccionTotal = 0
                        tiempoClases = 0

                        dia: 0
                        if dataCursos.dia1 == 'L':
                            dia = 0
                        elif dataCursos.dia1 == 'K':
                            dia = 1
                        elif dataCursos.dia1 == 'M':
                            dia = 2
                        elif dataCursos.dia1 == 'J':
                            dia = 3
                        elif dataCursos.dia1 == 'V':
                            dia = 4
                        elif dataCursos.dia1 == 'S':
                            dia = 5
                        elif dataCursos.dia1 == 'D':
                            dia = 6

                        if dia == anno.weekday():
                            fechaClasesEntrada : any
                            fechaClasesSalida : any
                            if dataCursos.ampmInicio == 'pm' :
                                if dataCursos.minutoInicio.strip() == '30':
                                    if dataCursos.horaInicio == '12 ':
                                        fechaClasesEntrada = str(anno.date()) + 'T' +'00'+ ':00:' + '00'
                                    else:
                                        fechaClasesEntrada = str(anno.date()) + 'T' + str((int(dataCursos.horaInicio) + 12)) + ':00:' + '00'
                                else:
                                    fechaClasesEntrada = str(anno.date()) + 'T' + str((int(dataCursos.horaInicio) + 11)) + ':30:' + '00'

                            else:
                                if dataCursos.minutoInicio.strip() == '30':
                                    fechaClasesEntrada = str(anno.date())+'T'+ str((int(dataCursos.horaInicio)-1))+':00:'+'00'
                                else:
                                    fechaClasesEntrada = str(anno.date()) + 'T' + str((int(dataCursos.horaInicio) - 1)) + ':30:' + '00'

                            if dataCursos.ampmFinal == 'pm' :
                                if dataCursos.minutoFinal.strip() == '30':
                                    if dataCursos.horaFinal == '12 ':
                                        fechaClasesSalida = str(anno.date()) + 'T' + '00' + ':00:' + '00'
                                    else:
                                        fechaClasesSalida = str(anno.date()) + 'T' + str((int(dataCursos.horaFinal) + 13)) + ':00:' + '00'
                                else:
                                    fechaClasesSalida = str(anno.date()) + 'T' + str( (int(dataCursos.horaFinal) + 12)) + ':30:' + '00'

                            else:
                                if dataCursos.minutoFinal.strip() == '30':
                                    fechaClasesSalida = str(anno.date()) + 'T' + str((int(dataCursos.horaFinal) + 1)) + ':00:' + '00'
                                else:
                                    fechaClasesSalida = str(anno.date()) + 'T' + str((int(dataCursos.horaFinal))) + ':30:' + '00'

                            fechaInicial = datetime.strptime(fechaClasesEntrada, "%Y-%m-%dT%H:%M:%S")
                            fechaFinal = datetime.strptime(fechaClasesSalida, "%Y-%m-%dT%H:%M:%S")

                            datosMarcasVirtuales = self.env['hr.attendance'].search(['&', ('employee_id', '=', dataDocente.id), ('check_in', '>=',fechaInicial+timedelta(hours=5)),('check_out', '<=',fechaFinal+timedelta(hours=8))])



                            if datosMarcasVirtuales:
                                ausencia = False

                                marcaEntrada = pytz.utc.localize(datosMarcasVirtuales.check_in).astimezone(user_tz)
                                marcaSalida = pytz.utc.localize(datosMarcasVirtuales.check_out).astimezone(user_tz)

                                marcaEntradaSistema = datetime.strptime(marcaEntrada.strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')
                                marcaSalidaSistema = datetime.strptime(marcaSalida.strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S')

                                if datosMarcasVirtuales.worked_hours >= dataCursos.cantiadadHoras:

                                    if marcaSalidaSistema.hour == 0:
                                        tipoDeduccion += 'Omision de marca'
                                        deduccionOmisionMarca += contrato.salario * 1.5
                                        horas += dataCurso.cantiadadHoras
                                    else:
                                        tipoDeduccion += 'OK'
                                        tiempoClases = (marcaSalidaSistema.hour - marcaEntradaSistema.hour) + ((marcaSalidaSistema.minute - marcaEntradaSistema.minute) / 60)
                                else:
                                    entradaHora = marcaEntradaSistema.hour - int(dataCursos.horaInicio)
                                    entradaMinuto = marcaEntradaSistema.minute - int(dataCursos.minutoInicio)
                                    totalEntrada = ((entradaHora * 60) + entradaMinuto)

                                    salidaHora = (int(dataCursos.horaFinal) + 12) - marcaSalidaSistema.hour
                                    salidaMinuto = int(dataCursos.minutoFinal) - marcaSalidaSistema.minute
                                    totalSalida = ((salidaHora * 60) + salidaMinuto)

                                    if totalEntrada > 1:
                                        tipoDeduccion += '-Entrada Tardia'
                                        deduccionEntradaTardia += contrato.salario * 0.5
                                    elif totalEntrada > 35:
                                        tipoDeduccion += '-Entrada Tardia'
                                        deduccionEntradaTardia += contrato.salario

                                    if totalSalida > 1:
                                        tipoDeduccion += '-Salida Temprana'
                                        deduccionSalidaTemprana += contrato.salario * 0.5
                                    elif totalSalida > 35:
                                        tipoDeduccion += '-Salida Temprana'
                                        deduccionSalidaTemprana += contrato.salario

                                if ausencia == True:
                                    tipoDeduccion += 'Ausencia'
                                    deduccionAusencia += contrato.salario * dataCursos.cantiadadHoras

                                deduccionTotal = deduccionEntradaTardia+deduccionSalidaTemprana+deduccionOmisionMarca+deduccionAusencia
                                cursosDocente.asistencia_line_ids = [(0, 0, {'docente_id': dataDocente.id,
                                                                             'cuatrimestre_id': cuatrimestre.id,
                                                                             'asistencia_id': cursosDocente.id,
                                                                             'aplicar': True,
                                                                             'cursoMarca': dataCursos.codigoCurso,
                                                                             'entradaClases': marcaEntradaSistema + timedelta(hours=6),
                                                                             'salidaClases': marcaSalidaSistema + timedelta(hours=6),
                                                                             'tiempoClases': tiempoClases,
                                                                             'estado': tipoDeduccion,
                                                                             'deduccionEntradaTardia': deduccionEntradaTardia,
                                                                             'deduccionSalidaTemprana': deduccionSalidaTemprana,
                                                                             'deduccionOmisionMarca': deduccionOmisionMarca,
                                                                             'deduccionAusencia': deduccionAusencia,
                                                                             'deduccionTotal': deduccionTotal,
                                                                             })]

                            else:
                                dataJSon = {
                                    'DocenteCedula': dataDocente.identification_id,
                                    'Anno': anno.year,
                                    'Periodo': periodo,
                                    'CodigoMarca': contrato.codigoMarca,
                                    'DiaMarcaEntrada': str(fechaInicial.date())+'T'+str(fechaInicial.time()),
                                    'DiaMarcaSalida': str(fechaFinal.date())+'T'+str(fechaFinal.time()),
                                    #'FechaInicioPago': str(planilla.fechaInicioPago),
                                    #'FechaFinPago': str(planilla.fechaFinalPago),
                                }
                                header = {
                                    'Content-Type': 'application/json',
                                    'Accept': 'text/plain'
                                }

                                response = requests.post(url, headers=header, json=dataJSon, verify=False)

                                if response.status_code == 200:

                                    if response.json()['data']:

                                        marcasList = []
                                        inicioClases = datetime.strptime( str(anno.date()) + ' ' + dataCursos.horaInicio.strip() + ':' + dataCursos.minutoInicio.strip() + ':' + '00',"%Y-%m-%d %H:%M:%S")
                                        finCalses = datetime.strptime(str(anno.date()) + ' ' + dataCursos.horaFinal.strip() + ':' + dataCursos.minutoFinal.strip() + ':' + '00',"%Y-%m-%d %H:%M:%S")
                                        if dataCursos.ampmInicio == 'pm':
                                            inicioClases += timedelta(hours=12)
                                        if dataCursos.ampmFinal == 'pm':
                                            finCalses += timedelta(hours=12)

                                        for dataMarca in response.json()['data']:
                                            marca  = datetime.strptime(dataMarca['datetime'],"%Y-%m-%dT%H:%M:%S")
                                            marcasList.append(marca)

                                        marcaSalida = max(marcasList)
                                        marcaEntrada = min(marcasList)

                                        nomarca = datetime.strptime(str(anno.year)+'-'+str(anno.month)+'-'+str(anno.day)+'T'+'00:00:00',"%Y-%m-%dT%H:%M:%S")
                                        if marcaEntrada == marcaSalida:
                                            if marcaEntrada <= inicioClases and marcaEntrada < (finCalses + timedelta(hours=1.5)):
                                                marcaEntrada = nomarca
                                                tipoDeduccion += '-Omision de marca'
                                                deduccionOmisionMarca += contrato.salario * 1.5
                                            else:
                                                marcaSalida = nomarca
                                                tipoDeduccion += '-Omision de marca'
                                                deduccionOmisionMarca += contrato.salario * 1.5
                                        else:
                                            tiempoClases = (marcaSalida.hour - marcaEntrada.hour) + ((marcaSalida.minute - marcaEntrada.minute) / 60)


                                        if marcaEntrada.hour != 0:

                                            if marcaEntrada <= inicioClases or marcaEntrada <= inicioClases - timedelta(minutes=5):
                                                tipoDeduccion = 'OK'
                                                deduccionTotal += 0

                                            elif marcaEntrada >= inicioClases + timedelta(minutes=6) and marcaEntrada <= inicioClases + timedelta(minutes=34):
                                                tipoDeduccion += '-Entrada Tardia'
                                                deduccionEntradaTardia += contrato.salario * 0.5

                                            elif marcaEntrada >= inicioClases + timedelta(minutes=35):
                                                tipoDeduccion += '-Entrada Tardia'
                                                deduccionEntradaTardia += contrato.salario

                                        if marcaSalida.hour != 0:
                                            if marcaSalida >= finCalses:
                                                tipoDeduccion = 'OK'
                                                deduccionTotal += 0

                                            elif marcaSalida <= finCalses and marcaSalida > finCalses - timedelta(minutes=35):
                                                tipoDeduccion += '-Salida Temprana'
                                                deduccionSalidaTemprana += contrato.salario * 0.5

                                            elif marca <= finCalses - timedelta(minutes=35):
                                                tipoDeduccion += '-Salida Temprana'
                                                deduccionSalidaTemprana += contrato.salario

                                        deduccionTotal += deduccionEntradaTardia + deduccionSalidaTemprana + deduccionOmisionMarca + deduccionAusencia
                                        cursosDocente.asistencia_line_ids = [(0, 0, {'docente_id': dataDocente.id,
                                                                                     'cuatrimestre_id': cuatrimestre.id,
                                                                                     'asistencia_id': cursosDocente.id,
                                                                                     'aplicar': True,
                                                                                     'cursoMarca': dataCursos.codigoCurso,
                                                                                     'entradaClases': marcaEntrada + timedelta(hours=6),
                                                                                     'salidaClases': marcaSalida + timedelta(hours=6),
                                                                                     'tiempoClases': tiempoClases,
                                                                                     'estado': tipoDeduccion,
                                                                                     'deduccionEntradaTardia': deduccionEntradaTardia,
                                                                                     'deduccionSalidaTemprana': deduccionSalidaTemprana,
                                                                                     'deduccionOmisionMarca': deduccionOmisionMarca,
                                                                                     'deduccionAusencia': deduccionAusencia,
                                                                                     'deduccionTotal': deduccionTotal,
                                                                                     })]

                                    else:
                                        tipoDeduccion += 'Ausencia'
                                        deduccionAusencia += contrato.salario * dataCursos.cantiadadHoras

                                        nomarca = datetime.strptime(str(anno.year) + '-' + str(anno.month) + '-' + str(anno.day) + 'T' + '00:00:00',"%Y-%m-%dT%H:%M:%S")

                                        deduccionTotal = deduccionEntradaTardia + deduccionSalidaTemprana + deduccionOmisionMarca + deduccionAusencia
                                        cursosDocente.asistencia_line_ids = [(0, 0, {'docente_id': dataDocente.id,
                                                                                     'cuatrimestre_id': cuatrimestre.id,
                                                                                     'asistencia_id': cursosDocente.id,
                                                                                     'aplicar': True,
                                                                                     'cursoMarca': dataCursos.codigoCurso,
                                                                                     'entradaClases': nomarca,
                                                                                     'salidaClases':nomarca,
                                                                                     'tiempoClases': 0,
                                                                                     'estado': tipoDeduccion,
                                                                                     'deduccionEntradaTardia': deduccionEntradaTardia,
                                                                                     'deduccionSalidaTemprana': deduccionSalidaTemprana,
                                                                                     'deduccionOmisionMarca': deduccionOmisionMarca,
                                                                                     'deduccionAusencia': deduccionAusencia,
                                                                                     'deduccionTotal': deduccionTotal,
                                                                                     })]

    @api.model
    def _set_horario_omision(self):
        for marcas in  self.env['hr.attendance'].search([('check_out','=',False)]):
            hoy = marcas.check_in - timedelta(hours=6)
            marcas.check_out = (datetime.strptime(str(hoy.date())+' '+'23'+':'+'50', "%Y-%m-%d %H:%M") + timedelta(hours=6))

    @api.model
    def _get_cambio_curso(self):
        user_tz = pytz.timezone(self.env.user.tz)
        indexDia = pytz.utc.localize(datetime.today()).astimezone(user_tz).weekday()
        fechaActual = pytz.utc.localize(datetime.today()).astimezone(user_tz).date() - timedelta(days=(5 - indexDia))
        return  fechaActual

    @api.model
    def _envio_correo_horarios_erroneos(self):
        cursosDict = {}
        cursosList = []
        ICPSudo = self.env['ir.config_parameter'].sudo()
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)

        if self.cuatrimestre_id:
            cursosDocente = self.env['cursos.docente.line'].search(
                [('cuatrimestre_id', '=', self.cuatrimestre_id.id), '|', ('cantiadadHoras', '<', 0),
                 ('cantiadadHoras', '>', 6)])
            for data in cursosDocente:
                cursosDict = {
                    'docente': data.docente_id.name,
                    'curso': data.descripcion,
                    'codigo': data.codigoCurso,
                    'horasCurso': data.cantiadadHoras,
                    'horarioCurso': data.horario,
                }
                cursosList.append(cursosDict)
                data.unlink()
            if len(cursosList) != 0:
                template_id = self.env.ref('nomina.email_cursos_horario_erroneo').id
                template = self.env['mail.template'].browse(template_id)
                email_values = {'email_to': ICPSudo.get_param('nomina.correoEnvioHorarioErroneo'),
                                'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                                'subject': 'Reporte de cursos horario erroneo ' + str(anno.date())
                                }
                template.with_context(listCursos=cursosList).send_mail(self.id, email_values=email_values,
                                                                       force_send=True)

    @api.model
    def _envio_correo_cursos_deshabilitados(self):
        cursosDict = {}
        cursosList = []
        ICPSudo = self.env['ir.config_parameter'].sudo()
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)

        if self.cuatrimestre_id:
            cursosDocente = self.env['cursos.docente.line'].search(
                [('fechaCambioCurso', '=', pytz.utc.localize(datetime.today()).astimezone(user_tz).date())])
            for data in cursosDocente:
                cursosDict = {
                    'docente': data.docente_id.name,
                    'curso': data.descripcion,
                    'codigo': data.codigoCurso,
                    'horasCurso': data.cantiadadHoras,
                    'horarioCurso': data.horario,
                }
                cursosList.append(cursosDict)
            if len(cursosList) != 0:
                template_id = self.env.ref('nomina.email_cursos_cursos_deshabilitados').id
                template = self.env['mail.template'].browse(template_id)
                email_values = {'email_to': ICPSudo.get_param('nomina.correoEnvioHorarioErroneo'),
                                'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                                'subject': 'Reporte de cursos deshabilitados ' + str(anno.date())
                                }
                template.with_context(listCursos=cursosList).send_mail(self.id, email_values=email_values,
                                                                       force_send=True)

    @api.model
    def _envio_correo_cursos_choques(self):
        cursosDict = {}
        cursosList = []
        ICPSudo = self.env['ir.config_parameter'].sudo()
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)

        if self.cuatrimestre_id:
            cursosDocente = self.env['cursos.docente.line'].search([('cuatrimestre_id', '=', self.cuatrimestre_id.id)])
            for data in cursosDocente:
                if data.cursoActivo:
                    cursoChoque = list(filter(lambda x: (x.dia1 == data.dia1) and
                                                        (int(data.horaInicio) >= int(x.horaInicio)) and
                                                        (x.docente_id == data.docente_id) and
                                                        (x.id != data.id) and
                                                        (x.cursoActivo == True) and
                                                        (x.cuatrimestre_id == data.cuatrimestre_id) and
                                                        (int(data.horaInicio) < int(x.horaFinal)), cursosDocente))

                    for dataCurso in cursoChoque:
                        dataCurso.cursoActivo = False
                        cursosDict = {
                            'docente': data.docente_id.name,
                            'curso': data.descripcion,
                            'codigo': data.codigoCurso,
                            'horasCurso': data.cantiadadHoras,
                            'horarioCurso': data.horario,
                        }
                        cursosList.append(cursosDict)

        if len(cursosList) != 0:
            template_id = self.env.ref('nomina.email_cursos_cursos_choques').id
            template = self.env['mail.template'].browse(template_id)
            email_values = {'email_to': 'ggamboaf@uia.ac.cr',
                            'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                            'subject': 'Cursos con Choques de Horario ' + str(anno.date())
                            }
            template.with_context(listCursos=cursosList).send_mail(self.id, email_values=email_values, force_send=True)

    @api.model
    def _get_cambio_curso(self):
        user_tz = pytz.timezone(self.env.user.tz)
        indexDia = pytz.utc.localize(datetime.today()).astimezone(user_tz).weekday()
        fechaActual = pytz.utc.localize(datetime.today()).astimezone(user_tz).date() - timedelta(days=(5 - indexDia))
        return fechaActual

    @api.model
    def _generar_asistencia_diaria(self):
        res = any
        cantiadadHoras = any
        cantiadadHorasSemana = any
        planillaActual = any
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('nomina.urlWSOdoo')+'/api/CursosDocenteUC/getAsistenciaDocente'

        hoy = datetime.now() - timedelta(hours=6)
        periodo = 0
        if hoy.month >= 1 and hoy.month <= 4:
            periodo = 1
        elif hoy.month >= 5 and hoy.month <= 8:
            periodo = 2
        elif hoy.month >= 9 and hoy.month <= 12:
            periodo = 3

        cuatrimestre = self.env['periodo.cuatrimestre'].search(['&',('year','=',str(hoy.year)),('decripcion','=',str(periodo)+"Q")])

        dia = any
        if hoy.weekday() == 0:
            dia = 'L'
        elif hoy.weekday() == 1:
            dia = 'K'
        elif hoy.weekday() == 2:
            dia = 'M'
        elif hoy.weekday() == 3:
            dia = 'J'
        elif hoy.weekday() == 4:
            dia = 'V'
        elif hoy.weekday() == 5:
            dia = 'S'
        elif hoy.weekday() == 6:
            dia = 'D'

        semana = int(math.ceil((((hoy.date() - cuatrimestre.fechaInicioPrimerPago).days + 1) / 7)))
        pago =""
        if semana <= 4:
            pago = "Primer Pago"
        elif semana > 4 and semana <= 9:
            pago = "Segundo Pago"
        elif semana > 9:
            pago = "Tercer Pago"

        cursosDia = self.env['cursos.docente.line'].search(['&', ('cuatrimestre_id', '=', cuatrimestre.id), ('dia1', '=', dia), ('cursoActivo', '=', True)])
        correoAusencias_list = []
        for curso in cursosDia:

            if self.env['asistencia.docente.line'].search(['&', ('cursoMarca', '=', curso.codigoCurso),
                                                           ('cuatrimestre_id', '=', cuatrimestre.id),
                                                           ('docente_id', '=', curso.docente_id.id),
                                                           ('horarioCurso', '=', curso.horario),
                                                           ('fechaCurso', '=', hoy.date()),
                                                           ('marcaJustificada', '=', True)]):
                continue

            if (curso.estadoCurso == "Tutoria" or curso.estadoCurso == "Tutoria Ext"):
                hastaSemana = self.env['configuraciones.tutorias.line'].search([('numeroEstudiantes', '=', curso.alumnos)])
                generaMarca = self.env['configuraciones.tutorias.semana.line'].sudo().search(['&', ('tutoria_id', '=', hastaSemana.id), ('semanaMarca', '=', semana)])
                if not generaMarca:
                    continue

            if curso.fechaCambioCurso != False:
                if hoy.date() > curso.fechaCambioCurso:
                    continue

            if curso.fechaInicioPago != False:
                if hoy.date() < curso.fechaInicioPago:
                    continue

            if self.env['configuraciones.cursos.taller.graduacion'].search([('codigoCurso', '=', curso.codigoCurso)]):
                if semana > 6:
                    continue

            if self.env['configuraciones.cursos.medicina'].search([('codigoCurso', '=', curso.codigoCurso)]).planillaExterna:
                continue

            cursosDocente = self.env['cursos.docente'].search(['&', ('docente_id', '=', curso.docente_id.id), ('cuatrimestre_id', '=', cuatrimestre.id)])
            contrato = self.env['contrato.empleado'].search([('empleado_id', '=', curso.docente_id.id)])
            tipoDeduccion = ''
            deduccionTotal = 0

            vals = {
                'docente_id': curso.docente_id.id,
                'cuatrimestre_id': cuatrimestre.id,
                'asistencia_id': cursosDocente.id,
                'aplicar': True,
                'cursoMarca': curso.codigoCurso,
                'fechaCurso': hoy.date(),
                'horarioCurso': curso.horario,
                'deduccionEntradaTardia': 0,
                'deduccionSalidaTemprana': 0,
                'deduccionOmisionMarca': 0,
                'deduccionAusencia': 0,
                'deduccionTotal': 0,
                'marcaJustificada': False,
                'pagoMarca': pago,
                'estado': 'OK'
            }

            entradaClasesDB = any
            salidaClasesDB = any

            entradaClasesDB = datetime.strptime(str(hoy.date()) + ' ' + curso.horaInicio + ':' + curso.minutoInicio,"%Y-%m-%d %H:%M")
            salidaClasesDB = datetime.strptime(str(hoy.date()) + ' ' + curso.horaFinal + ':' + curso.minutoFinal,"%Y-%m-%d %H:%M")
            salidaClasesDBOmision = datetime.strptime(str(hoy.date()) + ' ' + '23' + ':' + '50', "%Y-%m-%d %H:%M")

            if contrato.marca == False:
                vals.update({
                    'entradaClases': entradaClasesDB + timedelta(hours=6),
                    'salidaClases': salidaClasesDB + timedelta(hours=6),
                    'tiempoClases': curso.cantiadadHoras,
                    'estado': 'OK'
                })
                asistenciaDocente = cursosDocente.asistencia_line_ids

                asistencia = list(filter(lambda x: (x.docente_id.id == vals['docente_id']) and
                                                   (x.cuatrimestre_id.id == vals['cuatrimestre_id']) and
                                                   (x.cursoMarca == vals['cursoMarca']) and
                                                   (x.horarioCurso == vals['horarioCurso']) and
                                                   (x.fechaCurso == vals['fechaCurso']), asistenciaDocente))
                if asistencia:
                    cursosDocente.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                else:
                    cursosDocente.asistencia_line_ids = [(0, 0, vals)]
                continue

            datosMarcasVirtuales = self.env['hr.attendance'].search(['&', ('employee_id', '=', curso.docente_id.id),
                                                                     ('check_in', '>=', ((entradaClasesDB + timedelta(hours=6)) - timedelta(hours=2))),
                                                                     ('check_out', '<=',((salidaClasesDB + timedelta(hours=8))))])

            if not datosMarcasVirtuales:
                datosMarcasVirtuales = self.env['hr.attendance'].search(['&', ('employee_id', '=', curso.docente_id.id),
                                                                         ('check_in', '>=', ((entradaClasesDB + timedelta(hours=6)) - timedelta(hours=2))),
                                                                         ('check_out', '=',((salidaClasesDBOmision + timedelta(hours=6))))])

            timezone = pytz.timezone(curso.docente_id.resource_id.tz)
            marcasList = []
            if datosMarcasVirtuales:
                for marca in datosMarcasVirtuales:
                    marcaEntarda = pytz.utc.localize(marca.check_in).astimezone(timezone).replace(tzinfo=None)
                    marcaSalida = pytz.utc.localize(marca.check_out).astimezone(timezone).replace(tzinfo=None)
                    if marcaEntarda >= entradaClasesDB - timedelta(hours=2) and marcaEntarda <= entradaClasesDB + timedelta(hours=2):
                        marcasList.append(marcaEntarda)
                        marcasList.append(marcaSalida)
            else:
                dataJSon = {
                    'DocenteCedula': curso.docente_id.identification_id,
                    'Anno': hoy.year,
                    'CodigoMarca': contrato.codigoMarca,
                    'DiaMarcaEntrada': str(entradaClasesDB.date()) + 'T' + str(entradaClasesDB.time()),
                    'DiaMarcaSalida': str(salidaClasesDB.date()) + 'T' + str(salidaClasesDB.time()),
                }
                header = {
                    'Content-Type': 'application/json',
                    'Accept': 'text/plain'
                }

                response = requests.post(url, headers=header, json=dataJSon, verify=False)

                if response.status_code == 200:
                    for data in response.json()['data']:
                        marcasList.append(datetime.strptime(data['datetime'], "%Y-%m-%d %H:%M"))

            if marcasList:
                marcaEntrada = datetime.today()
                marcaSalida = datetime.today()
                if len(marcasList) == 1:
                    if marcasList[0] <= entradaClasesDB + timedelta(hours=curso.cantiadadHoras / 2):
                        marcaEntrada = marcasList[0]
                        marcaSalida = datetime.strptime(str(datetime.today().date()) + ' ' + '23' + ':' + '50',
                                                        "%Y-%m-%d %H:%M")
                    elif marcasList[0] >= salidaClasesDB - timedelta(hours=curso.cantiadadHoras / 2):
                        marcaSalida = marcasList[0]
                        marcaEntrada = entradaClasesDB - timedelta(hours=3)

                else:
                    marcaEntrada = min(marcasList)
                    marcaSalida = max(marcasList)

                if marcaEntrada >= entradaClasesDB - timedelta(hours=2) and marcaEntrada <= entradaClasesDB + timedelta(minutes=10):
                    vals.update({
                        'entradaClases': marcaEntrada + timedelta(hours=6),
                    })
                else:

                    diferenciaEntrada = marcaEntrada.hour - entradaClasesDB.hour
                    diferenciaSalida = marcaEntrada.hour - salidaClasesDB.hour

                    if (marcaEntrada.hour - entradaClasesDB.hour) > 1:
                        tipoDeduccion += 'Omision Marca Entrada, '
                        deduccionOmisionMarca = contrato.salario * 1.5
                        deduccionTotal += deduccionOmisionMarca
                        vals.update({
                            'entradaClases': marcaEntrada + timedelta(hours=6),
                            'deduccionOmisionMarca': deduccionOmisionMarca,
                            'tiempoClases': curso.cantiadadHoras,
                        })
                    else:
                        deduccionEntradaTardia = 0
                        entradaHora = marcaEntrada.hour - entradaClasesDB.hour
                        entradaMinuto = marcaEntrada.minute - entradaClasesDB.minute
                        totalEntrada = ((entradaHora * 60) + entradaMinuto)
                        tipoDeduccion += 'Entrada Tardia, '

                        if (marcaSalida.hour + (marcaSalida.minute / 60)) - (
                                marcaEntrada.hour + (marcaEntrada.minute / 60)) >= 1:
                            if totalEntrada > 1 and totalEntrada < 35:
                                deduccionEntradaTardia = contrato.salario * 0.5

                            elif totalEntrada > 35:
                                deduccionEntradaTardia = contrato.salario

                        deduccionTotal += deduccionEntradaTardia
                        vals.update({
                            'entradaClases': marcaEntrada + timedelta(hours=6),
                            'deduccionEntradaTardia': deduccionEntradaTardia,
                        })

                if marcaSalida >= salidaClasesDB - timedelta(minutes=10) and marcaSalida <= salidaClasesDB + timedelta(hours=2):
                    vals.update({
                        'salidaClases': marcaSalida + timedelta(hours=6),
                    })
                else:
                    if (marcaSalida.hour - salidaClasesDB.hour) > 1:
                        tipoDeduccion += 'Omision Marca Salida, '
                        deduccionOmisionMarca = contrato.salario * 1.5
                        deduccionTotal += deduccionOmisionMarca
                        vals.update({
                            'salidaClases': marcaSalida + timedelta(hours=6),
                            'deduccionOmisionMarca': deduccionOmisionMarca,
                            'tiempoClases': curso.cantiadadHoras,
                        })
                    else:
                        deduccionSalidaTemprana = 0
                        salidaHora = salidaClasesDB.hour - marcaSalida.hour
                        saldiaMinuto = salidaClasesDB.minute - marcaSalida.minute
                        totalSalida = ((salidaHora * 60) + saldiaMinuto)
                        tipoDeduccion += 'Salida Temprana, '

                        if (marcaSalida.hour + (marcaSalida.minute / 60)) - (
                                marcaEntrada.hour + (marcaEntrada.minute / 60)) >= 1:

                            if totalSalida > 1 and totalSalida < 35:
                                deduccionSalidaTemprana += contrato.salario * 0.5
                            elif totalSalida > 35:
                                deduccionSalidaTemprana += contrato.salario

                        deduccionTotal += deduccionSalidaTemprana

                        vals.update({
                            'salidaClases': marcaSalida + timedelta(hours=6),
                            'deduccionSalidaTemprana': deduccionSalidaTemprana,
                        })

                if deduccionTotal <= 0 and (tipoDeduccion == 'Ok' or tipoDeduccion == 'OK'):
                    tipoDeduccion = 'OK'
                vals.update({
                    'deduccionTotal': deduccionTotal,
                    'estado': tipoDeduccion,
                })

                if 'tiempoClases' not in vals:
                    timepoClase = (marcaSalida.hour + (marcaSalida.minute / 60)) - (
                                marcaEntrada.hour + (marcaEntrada.minute / 60))
                    if timepoClase > curso.cantiadadHoras:
                        vals.update({
                            'tiempoClases': curso.cantiadadHoras,
                        })
                    else:
                        if vals['estado'] == 'OK':
                            vals.update({
                                'tiempoClases': curso.cantiadadHoras,
                            })
                        else:
                            vals.update({
                                'tiempoClases': curso.cantiadadHoras,
                            })
                asistenciaDocente = cursosDocente.asistencia_line_ids

                asistencia = list(filter(lambda x: (x.docente_id.id == vals['docente_id']) and
                                                   (x.cuatrimestre_id.id == vals['cuatrimestre_id']) and
                                                   (x.cursoMarca == vals['cursoMarca']) and
                                                   (x.horarioCurso == vals['horarioCurso']) and
                                                   (x.fechaCurso == vals['fechaCurso']), asistenciaDocente))
                if asistencia:
                    cursosDocente.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                else:
                    cursosDocente.asistencia_line_ids = [(0, 0, vals)]

            else:
                vals.update({
                    'estado': 'Ausencia',
                    'deduccionTotal': deduccionTotal,
                    'tiempoClases': 0,
                    'entradaClases': False,
                    'salidaClases': False,
                })
                asistenciaDocente = cursosDocente.asistencia_line_ids

                asistencia = list(filter(lambda x: (x.docente_id.id == vals['docente_id']) and
                                                   (x.cuatrimestre_id.id == vals['cuatrimestre_id']) and
                                                   (x.cursoMarca == vals['cursoMarca']) and
                                                   (x.horarioCurso == vals['horarioCurso']) and
                                                   (x.fechaCurso == vals['fechaCurso']), asistenciaDocente))
                if asistencia:
                    cursosDocente.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                else:
                    cursosDocente.asistencia_line_ids = [(0, 0, vals)]


            if vals['estado'] not in ['OK','Ok',''] :
                dict = {
                    'identificacion': curso.docente_id.identification_id,
                    'anno': str(hoy.year),
                    'periodo': str(periodo),
                    'diaCurso': dia,
                    'fechaCurso': str(hoy.date()),
                    'horaInicio': curso.horaInicio,
                    'minutoInicio': curso.minutoInicio,
                    'horaFinal': curso.horaFinal,
                    'minutoFinal': curso.minutoFinal,
                    'docente': curso.docente_id.name,
                    'curso': curso.codigoCurso,
                    'horario': curso.horario,
                    'sede': curso.sede,
                    'tipo': curso.estadoCurso,
                    'estado': vals['estado'],
                }
                correoAusencias_list.append(dict)
        if len(correoAusencias_list) > 0:
            data_record = base64.b64encode(self.generar_excel_justificaciones(correoAusencias_list))
            ir_values = {
                'name': "Justificaciones.xlsx",
                'type': 'binary',
                'datas': data_record,
                'store_fname': data_record,
                'mimetype': 'application/vnd.ms-excel',
            }
            datosCorreo = {
                'hoy': hoy.date(),
            }
            data_id = self.env['ir.attachment'].create(ir_values)
            template_id = self.env.ref('nomina.email_correo_cursos_ausencia').id
            template = self.env['mail.template'].browse(template_id)
            template.attachment_ids = [(6, 0, [data_id.id])]
            email_values = {'email_to': ICPSudo.get_param('nomina.correoAusencias'),
                            'subject': 'Reporte de Ausencias del '+str(hoy.date())
                            }
            template.with_context(datosCorreo=datosCorreo).send_mail(self.id, email_values=email_values, force_send=True)
            template.attachment_ids = [(3, data_id.id)]

    def generar_excel_justificaciones(self,dataAsistencia):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 14, 'bold': True, 'align': 'center'})
        header_style = workbook.add_format(
            {'font_name': 'Times', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center'})
        text_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'left'})
        number_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right'})

        sheet = workbook.add_worksheet('Planilla')
        sheet.write(0, 0, 'Cedula')
        sheet.write(0, 1, 'Año')
        sheet.write(0, 2, 'Periodo')
        sheet.write(0, 3, 'Dia curso')
        sheet.write(0, 4, 'Fecha curso')
        sheet.write(0, 5, 'Hora Inicio')
        sheet.write(0, 6, 'Minuto Inicio')
        sheet.write(0, 7, 'Hora Final')
        sheet.write(0, 8, 'Minuto Final')
        sheet.write(0, 9, 'Sede')
        sheet.write(0, 10, 'Nombre')
        sheet.write(0, 11, 'Curso')
        sheet.write(0, 12, 'Horario')
        sheet.write(0, 13, 'Tipo')
        sheet.write(0, 14, 'Estado')

        row = 1
        # search the sales order

        for data in dataAsistencia:
            sheet.write(row, 0, data['identificacion'])
            sheet.write(row, 1, data['anno'])
            sheet.write(row, 2, data['periodo'])
            sheet.write(row, 3, data['diaCurso'])
            sheet.write(row, 4, data['fechaCurso'])
            sheet.write(row, 5, data['horaInicio'])
            sheet.write(row, 6, data['minutoInicio'])
            sheet.write(row, 7, data['horaFinal'])
            sheet.write(row, 8, data['minutoFinal'])
            sheet.write(row, 9, data['sede'])
            sheet.write(row, 10, data['docente'])
            sheet.write(row, 11, data['curso'])
            sheet.write(row, 12, data['horario'])
            sheet.write(row, 13, data['tipo'])
            sheet.write(row, 14, data['estado'])


            row += 1

        workbook.close()
        output.seek(0)
        datas = output.read()
        output.close()

        return datas
