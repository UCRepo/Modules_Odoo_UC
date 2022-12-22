from datetime import *
from odoo.http import request
import requests
import math
import pytz
import json
import logging
from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)



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

    def generar_asistencia(self):
        res = any
        cantiadadHoras = any
        cantiadadHorasSemana = any
        planillaActual = any
        ICPSudo = self.env['ir.config_parameter'].sudo()
        # url = ICPSudo.get_param('nomina.urlWSOdoo')+'/api/CursosDocente/getAsistenciaDocente'
        url = ICPSudo.get_param('nomina.urlWSOdoo')+'/api/CursosDocente/getAsistenciaDocente'
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)

        ausencia = True

        fechaActual = anno.date()
        desde = any
        hasta = any
        inicioCuatrimestre = self.cuatrimestre_id.fechaInicioCuatrimestre
        if self.pago == 'Primer Pago':
            desde = self.cuatrimestre_id.fechaInicioPrimerPago
            hasta = self.cuatrimestre_id.fechaFinPrimerPago
        elif self.pago == 'Segundo Pago':
            desde = self.cuatrimestre_id.fechaInicioSegundoPago
            hasta = self.cuatrimestre_id.fechaFinSegundoPago
        elif self.pago == 'Tercer Pago':
            desde = self.cuatrimestre_id.fechaInicioTercerPago
            hasta = self.cuatrimestre_id.fechaFinTercerPago


        while desde <= hasta:

            cantidadDias = ((desde - inicioCuatrimestre).days + 7)
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

                    if (cantidadDias / 7) > (hastaSemana.semanasTutoria + 1) :
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
                                        'tiempoClases': timepoClase,
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

            desde += timedelta(days=1)
