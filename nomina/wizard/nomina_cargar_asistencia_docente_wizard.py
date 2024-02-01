from datetime import *
from odoo.http import request
from odoo.tools.misc import xlsxwriter
import requests
import math
import pytz
import json
import logging
import base64
import io
import json
from odoo import api, fields, models, _

class NominaGenerarAsistenciaDocenteWizard(models.TransientModel):
    _name = "nomina.cargar.asistencia.docente.wizard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Generar Asistencia"

    cuatrimestre_id = fields.Many2one(
        comodel_name="periodo.cuatrimestre",
        string="Cuatrimestre",
        required=True,
        tracking=False,
    )
    pago = fields.Selection(
        string='Pago',
        tracking=False,
        required=True,
        selection=[
            ('Primer Pago', 'Primer Pago'),
            ('Segundo Pago', 'Segundo Pago'),
            ('Tercer Pago', 'Tercer Pago'),
        ]
    )
    docente_ids = fields.Many2one(
        comodel_name="hr.employee",
        string="Docente Especifico",
        readonly=False
    )

    desde = fields.Date(
        string="Desde",
        required=False,
    )
    hasta = fields.Date(
        string="Hasta",
        required=False,
    )
    incluirCursosPrecenciales = fields.Boolean(
        string="Incluir Cursos Presenciales",
        default=False,
    )

    def generar_asistencia(self):
        res = any
        cantiadadHoras = any
        cantiadadHorasSemana = any
        planillaActual = any
        ICPSudo = self.env['ir.config_parameter'].sudo()
        # url = ICPSudo.get_param('nomina.urlWSOdoo')+'/api/CursosDocente/getAsistenciaDocente'
        url = ICPSudo.get_param('nomina.urlWSOdoo')+'/api/CursosDocenteUC/getAsistenciaDocente'
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)

        ausencia = True

        fechaActual = anno.date()
        desde = any
        hasta = any
        inicioCuatrimestre = self.cuatrimestre_id.fechaInicioCuatrimestre
        if self.desde == False or self.hasta == False:
            if self.pago == 'Primer Pago':
                desde = self.cuatrimestre_id.fechaInicioPrimerPago
                hasta = self.cuatrimestre_id.fechaFinPrimerPago
            elif self.pago == 'Segundo Pago':
                desde = self.cuatrimestre_id.fechaInicioSegundoPago
                hasta = self.cuatrimestre_id.fechaFinSegundoPago
            elif self.pago == 'Tercer Pago':
                desde = self.cuatrimestre_id.fechaInicioTercerPago
                hasta = self.cuatrimestre_id.fechaFinTercerPago
        else:
            desde = self.desde
            hasta = self.hasta

        correoAusencias_list = []
        while desde <= hasta:

            cantidadDias = ((desde - inicioCuatrimestre).days + 7)
            semana = int(math.ceil((((desde - self.cuatrimestre_id.fechaInicioPrimerPago).days + 1) / 7)))
            dia = any
            if desde.weekday() == 0 :
                dia = 'L'
            elif desde.weekday() == 1 :
                dia = 'K'
            elif desde.weekday() == 2 :
                dia = 'M'
            elif desde.weekday() == 3 :
                dia = 'J'
            elif desde.weekday() == 4 :
                dia = 'V'
            elif desde.weekday() == 5 :
                dia = 'S'
            elif desde.weekday() == 6 :
                dia = 'D'


            cursosDia = self.env['cursos.docente.line'].search(['&',('cuatrimestre_id','=',self.cuatrimestre_id.id),('dia1','=',dia),('cursoActivo','=',True)])

            if self.docente_ids:
                cursosDia = self.env['cursos.docente.line'].search(['&',('docente_id' ,'=',self.docente_ids.id),('cuatrimestre_id','=',self.cuatrimestre_id.id),('dia1','=',dia),('cursoActivo','=',True)])

            for curso in cursosDia:

                if self.env['asistencia.docente.line'].search(['&', ('cursoMarca', '=', curso.codigoCurso),
                                                                   ('cuatrimestre_id', '=', self.cuatrimestre_id.id),
                                                                   ('docente_id', '=', curso.docente_id.id),
                                                                   ('horarioCurso', '=', curso.horario),
                                                                   ('fechaCurso', '=', desde),
                                                                   ('marcaJustificada','=',True)]):
                    continue

                if (curso.estadoCurso == "Tutoria" or curso.estadoCurso == "Tutoria Ext" ):
                    hastaSemana = self.env['configuraciones.tutorias.line'].search([('numeroEstudiantes','=',curso.alumnos)])
                    generaMarca = self.env['configuraciones.tutorias.semana.line'].sudo().search(['&',('tutoria_id','=',hastaSemana.id),('semanaMarca','=',semana)])
                    if not generaMarca:
                        continue

                if curso.fechaCambioCurso != False:
                    if desde > curso.fechaCambioCurso:
                        continue

                if curso.fechaInicioPago != False:
                    if desde < curso.fechaInicioPago:
                        continue

                if self.env['configuraciones.cursos.taller.graduacion'].search([('codigoCurso','=',curso.codigoCurso)]):
                    if self.pago != 'Primer Pago':
                        continue

                if self.env['configuraciones.cursos.medicina'].search([('codigoCurso', '=', curso.codigoCurso)]).planillaExterna:
                    continue

                cursosDocente = self.env['cursos.docente'].search(['&',('docente_id','=',curso.docente_id.id),('cuatrimestre_id','=',self.cuatrimestre_id.id)])
                contrato = self.env['contrato.empleado'].search([('empleado_id', '=', curso.docente_id.id)])
                tipoDeduccion = ''
                deduccionTotal = 0



                if 2 > 1:
                    vals = {
                        'docente_id': curso.docente_id.id,
                        'cuatrimestre_id': self.cuatrimestre_id.id,
                        'asistencia_id': cursosDocente.id,
                        'aplicar': True,
                        'cursoMarca': curso.codigoCurso,
                        'fechaCurso': desde,
                        'horarioCurso': curso.horario,
                        'deduccionEntradaTardia': 0,
                        'deduccionSalidaTemprana': 0,
                        'deduccionOmisionMarca': 0,
                        'deduccionAusencia': 0,
                        'deduccionTotal': 0,
                        'marcaJustificada': False,
                        'pagoMarca': self.pago,
                        'estado': 'OK',
                        'sede': curso.sede
                    }

                    entradaClasesDB = any
                    salidaClasesDB = any

                    entradaClasesDB = datetime.strptime(str(desde) + ' ' + curso.horaInicio + ':' + curso.minutoInicio,"%Y-%m-%d %H:%M")
                    salidaClasesDB = datetime.strptime(str(desde)+' '+curso.horaFinal+':'+curso.minutoFinal, "%Y-%m-%d %H:%M")
                    salidaClasesDBOmision = datetime.strptime(str(desde)+' '+'23'+':'+'50', "%Y-%m-%d %H:%M")

                    if contrato.marca == False:
                        vals.update({
                            'entradaClases': entradaClasesDB + timedelta(hours=6),
                            'salidaClases': salidaClasesDB + timedelta(hours=6),
                            'tiempoClases':curso.cantiadadHoras,
                            'estado':'OK'
                        })
                        asistenciaDocente = cursosDocente.asistencia_line_ids

                        asistencia = list(filter(lambda x: (x.docente_id.id == vals['docente_id']) and
                                                           (x.cuatrimestre_id.id == vals['cuatrimestre_id']) and
                                                           (x.cursoMarca == vals['cursoMarca']) and
                                                           (x.horarioCurso == vals['horarioCurso']) and
                                                           (x.fechaCurso == vals['fechaCurso']),asistenciaDocente))
                        if asistencia:
                            cursosDocente.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                        else:
                            cursosDocente.asistencia_line_ids = [(0, 0, vals)]
                        continue
                    datosMarcasVirtuales = self.env['hr.attendance'].search(['&',('employee_id', '=', curso.docente_id.id),
                                                                             ('check_in', '>=', ((entradaClasesDB + timedelta(hours=6)) - timedelta(hours=2))),
                                                                             ('check_out', '<=', ((salidaClasesDB + timedelta(hours=8))))])

                    if not datosMarcasVirtuales:
                        datosMarcasVirtuales = self.env['hr.attendance'].search(['&', ('employee_id', '=', curso.docente_id.id),
                                                                                 ('check_in', '>=', ((entradaClasesDB + timedelta(hours=6)) - timedelta(hours=2))),
                                                                                 ('check_out', '=', ((salidaClasesDBOmision + timedelta(hours=6))))])
                    timezone = pytz.timezone(curso.docente_id.resource_id.tz)
                    marcasList = []
                    if datosMarcasVirtuales:
                        for marca in  datosMarcasVirtuales:
                            marcaEntarda = pytz.utc.localize(marca.check_in).astimezone(timezone).replace(tzinfo=None)
                            marcaSalida = pytz.utc.localize(marca.check_out).astimezone(timezone).replace(tzinfo=None)
                            if marcaEntarda >= entradaClasesDB - timedelta(hours=2) and marcaEntarda <= entradaClasesDB + timedelta(hours=2):
                                marcasList.append(marcaEntarda)
                                marcasList.append(marcaSalida)


                    else:
                        dataJSon = {
                            'DocenteCedula': curso.docente_id.identification_id,
                            'Anno': fechaActual.year,
                            'CodigoMarca': contrato.codigoMarca,
                            'DiaMarcaEntrada': str(entradaClasesDB.date())+'T'+str(entradaClasesDB.time()),
                            'DiaMarcaSalida': str(salidaClasesDB.date())+'T'+str(salidaClasesDB.time()),
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
                        if len(marcasList) == 1 :
                                if  marcasList[0] <= entradaClasesDB + timedelta(hours = curso.cantiadadHoras/2):
                                    marcaEntrada = marcasList[0]
                                    marcaSalida = datetime.strptime(str(datetime.today().date())+' '+'23'+':'+'50', "%Y-%m-%d %H:%M")
                                elif marcasList[0] >= salidaClasesDB - timedelta(hours = curso.cantiadadHoras/2):
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

                                if (marcaSalida.hour + (marcaSalida.minute / 60)) - (marcaEntrada.hour + (marcaEntrada.minute / 60)) >= 1:
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

                                if (marcaSalida.hour + (marcaSalida.minute / 60)) - (marcaEntrada.hour + (marcaEntrada.minute / 60)) >= 1:

                                    if totalSalida > 1 and totalSalida < 35:
                                        deduccionSalidaTemprana += contrato.salario * 0.5
                                    elif totalSalida > 35:
                                        deduccionSalidaTemprana += contrato.salario

                                deduccionTotal += deduccionSalidaTemprana

                                vals.update({
                                    'salidaClases': marcaSalida + timedelta(hours=6),
                                    'deduccionSalidaTemprana': deduccionSalidaTemprana,
                                })

                        if deduccionTotal <= 0 and (tipoDeduccion == 'Ok' or tipoDeduccion == 'OK' ) :
                            tipoDeduccion = 'Ok'
                        vals.update({
                            'deduccionTotal': deduccionTotal,
                            'estado': tipoDeduccion,
                        })

                        if 'tiempoClases' not in vals:
                            timepoClase = (marcaSalida.hour + (marcaSalida.minute / 60)) - (marcaEntrada.hour + (marcaEntrada.minute / 60))
                            if timepoClase > curso.cantiadadHoras:
                                vals.update({
                                    'tiempoClases':curso.cantiadadHoras,
                                })
                            else:
                                if vals['estado'] == 'Ok':
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
                                                           (x.fechaCurso == vals['fechaCurso']) ,asistenciaDocente))
                        if asistencia:
                            cursosDocente.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                        else:
                            cursosDocente.asistencia_line_ids = [(0, 0, vals)]

                    else:
                        vals.update({
                            'estado' : 'Ausencia',
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

                    if vals['estado'] not in ['OK','Ok',''] and (curso.sede == "VT" or self.incluirCursosPrecenciales):
                        dict = {
                            'identificacion': curso.docente_id.identification_id,
                            'anno': str(desde.year),
                            'periodo': str(self.cuatrimestre_id.decripcion.replace('Q', '')),
                            'diaCurso': dia,
                            'fechaCurso': str(desde),
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

            desde += timedelta(days=1)

        hoy = datetime.today()
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
            email_values = {'email_to': self.env.user.email,
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