from datetime import date, timedelta, datetime,timezone,time
from odoo.http import request
import requests
import math
import pytz
import json
from odoo import api, fields, models, _

class PlanillaAdministrativaGenerarAsistenciaWizard(models.TransientModel):
    _name = "planilla.administrativa.generar.asistencia.wizard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Generar Asistencia"

    periodoPago_id = fields.Many2one(
        comodel_name="planilla.personal.periodo.pago",
        string="Periodo de Pago",
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
        ]
    )
    desde = fields.Date(
        string="Desde",
        required=False,
    )

    hasta = fields.Date(
        string="Hasta",
        required=False,
    )

    administrativo_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Administrativo Especifico",
        readonly=False
    )

    def _get_horario_DB(self,empleado,fechaInicio,horarioDia):
        marcaEntradaDB = any
        marcaSalidaDB = any
        vals = {}

        timezone = pytz.timezone(empleado.empleado_id.resource_id.tz)

        if fechaInicio.weekday() == 0:
            if horarioDia.horaInicioLunes != False:
                marcaEntradaDB = pytz.utc.localize(horarioDia.horaInicioLunes).astimezone(timezone).replace(tzinfo=None)
                marcaSalidaDB = pytz.utc.localize(horarioDia.horaFinalLunes).astimezone(timezone).replace(tzinfo=None)
                return {
                    'horario': str(marcaEntradaDB.time()) + ' - ' + str(marcaSalidaDB.time()),
                    'marcaEntradaDB': marcaEntradaDB,
                    'marcaSalidaDB': marcaSalidaDB,
                }
            else:
                fechaInicio += timedelta(days=1)
        elif fechaInicio.weekday() == 1:
            if horarioDia.horaInicioMartes != False:
                marcaEntradaDB = pytz.utc.localize(horarioDia.horaInicioMartes).astimezone(timezone).replace(tzinfo=None)
                marcaSalidaDB = pytz.utc.localize(horarioDia.horaFinalMartes).astimezone(timezone).replace(tzinfo=None)
                return {
                    'horario': str(marcaEntradaDB.time()) + ' - ' + str(marcaSalidaDB.time()),
                    'marcaEntradaDB': marcaEntradaDB,
                    'marcaSalidaDB': marcaSalidaDB,
                }
            else:
                return None

        elif fechaInicio.weekday() == 2:
            if horarioDia.horaInicioMiercoles != False:
                marcaEntradaDB = pytz.utc.localize(horarioDia.horaInicioMiercoles).astimezone(timezone).replace(tzinfo=None)
                marcaSalidaDB = pytz.utc.localize(horarioDia.horaFinalMiercoles).astimezone(timezone).replace(tzinfo=None)
                return {
                    'horario': str(marcaEntradaDB.time()) + ' - ' + str(marcaSalidaDB.time()),
                    'marcaEntradaDB': marcaEntradaDB,
                    'marcaSalidaDB': marcaSalidaDB,
                }
            else:
                return None

        elif fechaInicio.weekday() == 3:
            if horarioDia.horaInicioJueves != False:
                marcaEntradaDB = pytz.utc.localize(horarioDia.horaInicioJueves).astimezone(timezone).replace(tzinfo=None)
                marcaSalidaDB = pytz.utc.localize(horarioDia.horaFinalJueves).astimezone(timezone).replace(tzinfo=None)
                return {
                    'horario': str(marcaEntradaDB.time()) + ' - ' + str(marcaSalidaDB.time()),
                    'marcaEntradaDB': marcaEntradaDB,
                    'marcaSalidaDB': marcaSalidaDB,
                }
            else:
                return None

        elif fechaInicio.weekday() == 4:
            if horarioDia.horaInicioViernes != False:
                marcaEntradaDB = pytz.utc.localize(horarioDia.horaInicioViernes).astimezone(timezone).replace(tzinfo=None)
                marcaSalidaDB = pytz.utc.localize(horarioDia.horaFinalViernes).astimezone( timezone).replace(tzinfo=None)
                return {
                    'horario': str(marcaEntradaDB.time()) + ' - ' + str(marcaSalidaDB.time()),
                    'marcaEntradaDB': marcaEntradaDB,
                    'marcaSalidaDB': marcaSalidaDB,
                }
            else:
                return None

        elif fechaInicio.weekday() == 5:
            if horarioDia.horaInicioSabado != False:
                marcaEntradaDB = pytz.utc.localize(horarioDia.horaInicioSabado).astimezone(timezone).replace(tzinfo=None)
                marcaSalidaDB = pytz.utc.localize(horarioDia.horaFinalSabado).astimezone(timezone).replace(tzinfo=None)
                return {
                    'horario': str(marcaEntradaDB.time()) + ' - ' + str(marcaSalidaDB.time()),
                    'marcaEntradaDB': marcaEntradaDB,
                    'marcaSalidaDB': marcaSalidaDB,
                }
            else:
                return None

        elif fechaInicio.weekday() == 6:
            if horarioDia.horaInicioDomingo != False:
                marcaEntradaDB = pytz.utc.localize(horarioDia.horaInicioDomingo).astimezone(timezone).replace(tzinfo=None)
                marcaSalidaDB = pytz.utc.localize(horarioDia.horaFinalDomingo).astimezone(timezone).replace(tzinfo=None)
                return {
                    'horario': str(marcaEntradaDB.time()) + ' - ' + str(marcaSalidaDB.time()),
                    'marcaEntradaDB': marcaEntradaDB,
                    'marcaSalidaDB': marcaSalidaDB,
                }
            else:
                return None

    def _get_dias_laborales(self,empleado,fechaInicio,horarioDia):
        dias = 0
        horarioEmpleado = self.env['horario.empleado'].search([('empleado_id', '=', empleado.empleado_id.id)])
        if horarioEmpleado:
            horarioDia = self.env['horario.empleado.line'].search(['&', ('fechaDesde', '<=', fechaInicio), ('fechaHasta', '>=', fechaInicio),('horarioEmpleado_id', '=', horarioEmpleado.id)])
        else:
            return 0

        if horarioDia.horaInicioLunes != False:
            dias += 1

        if horarioDia.horaInicioMartes != False:
            dias += 1

        if horarioDia.horaInicioMiercoles != False:
            dias += 1

        if horarioDia.horaInicioJueves != False:
            dias += 1

        if horarioDia.horaInicioViernes != False:
            dias += 1

        if horarioDia.horaInicioSabado != False:
            dias += 1

        if horarioDia.horaInicioDomingo != False:
            dias += 1

        return dias

    def generarr_asistencia(self):
        asistenciaList = []
        vals = {}
        tiempoAcumuladolist = []
        horarioDia = any
        diaslaborales = 0
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('nomina.urlWSOdoo')+'/api/AsistenciaAdministrativaUIA/getAsistenciaEmpleado'

        for dataEmpleado in self.env['planilla.personal.empleados.planilla'].search(['&',('pago', '=',self.pago),('peridoPago_id','=',self.periodoPago_id.id)]):
            tiempoAcumuladolist = []
            cantidadIncapacidadesMAT = 0
            cantidadIncapacidadesSEM = 0
            fechaInicio = self.desde
            dataEmpleado.desde = self.desde
            dataEmpleado.hasta = self.hasta
            contrato = self.env['contrato.empleado'].search([('empleado_id', '=', dataEmpleado.empleado_id.id)])
            incapacidadesEmpleado = self.env['contrato.empleado.incapacidad.line'].search(['&',('fechaInicioIncapacidad', '>=', self.desde),
                                                                                           ('fechaFinIncapacidad','<=',self.hasta),
                                                                                           ('empleado_id','=',dataEmpleado.empleado_id.id)])
            vacacionesEmpleado = self.env['contrato.empleado.vacaciones.line'].search(['&',('fechaInicioVacaciones', '>=', self.desde),
                                                                                       ('fechaFinVacaciones','<=',self.hasta),
                                                                                       ('empleado_id','=',dataEmpleado.empleado_id.id),
                                                                                       ('estado', '=','Aprobada')])

            diasLibresEmpleado = self.env['planilla.personal.periodo.pago.dias.libres'].search(['&',('fecha', '>=', self.desde),
                                                                                       ('fecha','<=',self.hasta)])

            licenciasEmpleado = self.env['contrato.empleado.licencias.line'].search(['&',('fechaInicioLicencia', '>=', self.desde),
                                                                                       ('fechaFinLicencia','<=',self.hasta),
                                                                                       ('empleado_id','=',dataEmpleado.empleado_id.id),
                                                                                       ('estadoRH', '=','Aceptado')])

            for vacaciones in vacacionesEmpleado:
                dataEmpleado.vacaciones_ids =  [[ 4, vacaciones.id]]

            for incapacidad in incapacidadesEmpleado:
                dataEmpleado.incapacidades_ids =  [[ 4, incapacidad.id]]

            for licencias in licenciasEmpleado:
                dataEmpleado.licecnias_ids =  [[ 4, licencias.id]]

            while fechaInicio <= self.hasta:
                tipoDeduccion = ''
                if fechaInicio.weekday() == 0:
                    diaslaborales = self._get_dias_laborales(dataEmpleado, fechaInicio, horarioDia)

                if 2>1:
                    deduccionTotal = 0
                    horarioEmpleado = self.env['horario.empleado'].search([('empleado_id', '=', dataEmpleado.empleado_id.id)])
                    if horarioEmpleado:
                        horarioDia = self.env['horario.empleado.line'].search(['&', ('fechaDesde', '<=', fechaInicio), ('fechaHasta', '>=', fechaInicio),('horarioEmpleado_id', '=', horarioEmpleado.id)])
                    else:
                        fechaInicio += timedelta(days=1)
                        continue

                    vals = {
                        'asistencia_id': dataEmpleado.id,
                        'empleado_id': dataEmpleado.empleado_id.id,
                        'diaMarca': fechaInicio,
                        'deduccionOmisionMarca': 0,
                        'aplicar': True
                    }

                    horarioDB = self._get_horario_DB(dataEmpleado, fechaInicio, horarioDia)

                    if not horarioDB:
                        fechaInicio += timedelta(days=1)
                        continue

                    vals.update({
                        'horario': horarioDB['horario'],
                    })

                    marcaSalidaDB = horarioDB['marcaSalidaDB']
                    marcaEntradaDB = horarioDB['marcaEntradaDB']


                    dataJSon = {
                        'codigoMarca': self.env['contrato.empleado'].search([('empleado_id', '=', dataEmpleado.empleado_id.id)]).codigoMarca,
                        'fechaMarca': str(fechaInicio),
                    }
                    header = {
                        'Content-Type': 'application/json',
                        'Accept': 'text/plain'
                    }
                    response = requests.post(url, headers=header, json=dataJSon, verify=False)

                    if response.status_code == 200:
                        tiempoAcumuladoDict = {
                            'dia' : fechaInicio,
                            'diasTrabajo': diaslaborales,
                            'tiempoExtra': 0,
                            'tiempoLaboral':0,
                        }

                        if len(response.json()['data']) > 0:

                            asistenciaList = []
                            asistenciaListB = []
                            for data in response.json()['data']:
                                asistenciaList.append(datetime.strptime(data['datetime'], "%Y-%m-%d %H:%M"))
                                asistenciaListB.append(datetime.strptime(data['datetime'], "%Y-%m-%d %H:%M"))

                            if len(asistenciaList) >= 2:
                                marcaSalida = max(asistenciaList)
                                marcaEntrada = min(asistenciaList)
                            else:
                                salario = 0
                                if diaslaborales >= 5:
                                    salario = contrato.salario / 30
                                else:
                                    salario = contrato.salario / (diaslaborales * 4)
                                vals.update({
                                    'entradaLaboral': False,
                                    'salidaLaboral': False,
                                    'estado': 'Ausencia',
                                    'deduccionTotal': salario,
                                })
                                asistencia = list(filter(lambda x: (x.asistencia_id.id == dataEmpleado.id) and
                                                                   (x.empleado_id.id == dataEmpleado.empleado_id.id) and
                                                                   (x.diaMarca == fechaInicio),dataEmpleado.asistencia_line_ids))

                                if asistencia:
                                    dataEmpleado.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                                else:
                                    dataEmpleado.asistencia_line_ids = [(0, 0, vals)]

                                fechaInicio += timedelta(days=1)
                                continue
                            tiempoLaboralDB = marcaSalidaDB - marcaEntradaDB
                            tiempoLaboralMarcas = marcaSalida - marcaEntradaDB

                            tiempoAcumuladoDict.update({
                                'tiempoLaborralHorario': (tiempoLaboralDB.seconds / 3600) - 1,
                            })

                            if tiempoLaboralMarcas >= tiempoLaboralDB:
                                asistenciaList.remove(marcaEntrada)
                                asistenciaList.remove(marcaSalida)
                                asistenciaListB.remove(marcaEntrada)
                                asistenciaListB.remove(marcaSalida)
                            else:
                                if marcaEntrada >= (marcaEntradaDB - timedelta(hours=1)) and marcaEntrada <= ( marcaEntradaDB + timedelta(minutes=30)):
                                    asistenciaList.remove(marcaEntrada)
                                else:
                                    for marca in asistenciaList:
                                        if marca >= (marcaEntradaDB - timedelta(hours=1)) and marca <= (marcaEntradaDB + timedelta(minutes=30)):
                                            marcaEntrada = marca
                                            asistenciaList.remove(marcaEntrada)
                                        else:
                                            marcaEntrada = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                                if marcaSalida >= marcaSalidaDB - timedelta(minutes=15):
                                    asistenciaList.remove(marcaSalida)

                                else:
                                    for marca in asistenciaList:
                                        if marca >= (marcaSalidaDB - timedelta(minutes=15)):
                                            marcaSalida = marca
                                            asistenciaList.remove(marcaSalida)
                                        else:
                                            marcaSalida = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")

                            tiempoCafeM = False
                            tiempoCafeT = False
                            tiempoAlmuerzo = False
                            marcaEntradaCafeM = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                            marcaSalidaCafeM = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                            marcaEntradaA = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                            marcaSalidaA = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                            marcaEntradaCafeT = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                            marcaSalidaCafeT = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                            for marca in asistenciaList:

                                for marcaB in asistenciaListB:

                                    tiempomarca = math.trunc(((marca.hour + (marca.minute / 60)) - (
                                            marcaB.hour + (marcaB.minute / 60))) * 60)

                                    if tiempomarca > 0 and tiempomarca <= 20 and tiempoCafeM == False and marcaB != marca and marcaB.hour < 11:
                                        marcaEntradaCafeM = marcaB
                                        marcaSalidaCafeM = marca
                                        tiempoCafeM = True

                                for marcaB in asistenciaListB:

                                    tiempomarca = math.trunc(((marca.hour + (marca.minute / 60)) - (
                                            marcaB.hour + (marcaB.minute / 60))) * 60)

                                    if tiempomarca > 0 and tiempomarca <= 65 and tiempoAlmuerzo == False and marcaB != marcaEntradaCafeM and marca != marcaSalidaCafeM and marcaB.hour >= 11:
                                        marcaEntradaA = marcaB
                                        marcaSalidaA = marca
                                        tiempoAlmuerzo = True

                                for marcaB in asistenciaListB:

                                    tiempomarca = math.trunc(((marca.hour + (marca.minute / 60)) - (
                                            marcaB.hour + (marcaB.minute / 60))) * 60)

                                    if tiempomarca > 0 and tiempomarca <= 15 and tiempoCafeT == False and tiempoAlmuerzo == True and marcaB != marca and marcaB.hour > 12:
                                        marcaEntradaCafeT = marcaB
                                        marcaSalidaCafeT = marca
                                        tiempoCafeT = True

                            if marcaEntradaCafeM > datetime.strptime(str(fechaInicio) + ' 12:00', "%Y-%m-%d %H:%M"):
                                marcaEntradaCafeM = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                                if marcaSalidaCafeM > datetime.strptime(str(fechaInicio) + ' 12:00', "%Y-%m-%d %H:%M"):
                                    marcaSalidaCafeM = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")

                            if marcaEntradaCafeT < datetime.strptime(str(fechaInicio) + ' 12:00', "%Y-%m-%d %H:%M"):
                                marcaEntradaCafeT = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                                if marcaSalidaCafeT < datetime.strptime(str(fechaInicio) + ' 12:00', "%Y-%m-%d %H:%M"):
                                    marcaSalidaCafeT = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")

                            if marcaEntrada != datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M"):
                                if marcaEntrada >= (marcaEntradaDB - timedelta(hours=1)) and marcaEntrada <= (marcaEntradaDB + timedelta(minutes=5)):
                                    vals.update({
                                        'entradaLaboral': marcaEntrada + timedelta(hours=6),
                                    })

                                else:
                                    horaEntradaDB = (marcaEntradaDB + timedelta(minutes=5))
                                    entrada = (marcaEntrada - marcaEntradaDB)
                                    totalAtraso = math.trunc((entrada.total_seconds()) / 60)
                                    salario = contrato.salario / 4
                                    salario /= diaslaborales
                                    salario /= (contrato.jornadaLaboral / 2)
                                    salario /= 60
                                    deduccionTotal += salario * totalAtraso
                                    tipoDeduccion = 'Entrada Tardia \n'
                                    vals.update({
                                        'entradaLaboral': marcaEntrada + timedelta(hours=6),
                                        'deduccionEntradaTardia': salario * totalAtraso,
                                    })
                            else:
                                salario = contrato.salario / 4
                                salario /= diaslaborales
                                salario /= (contrato.jornadaLaboral / 2)
                                salario /= 60
                                deduccionTotal += salario * 15
                                tipoDeduccion += 'Omision de Marca Entrada \n '
                                vals.update({
                                    'entradaLaboral': False,
                                    'deduccionOmisionMarca': salario * 15,
                                })
                            if marcaSalida != datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M"):
                                if marcaSalida >= marcaSalidaDB:
                                    vals.update({
                                        'salidaLaboral': marcaSalida + timedelta(hours=6),
                                    })
                                else:
                                    entrada = (marcaSalidaDB - marcaSalida)
                                    totalAtraso = round((entrada.total_seconds()) / 60)
                                    salario = contrato.salario / 4
                                    salario /= diaslaborales
                                    salario /= (contrato.jornadaLaboral / 2)
                                    salario /= 60
                                    tipoDeduccion += 'Salida Temprana, '
                                    deduccionTotal += salario * totalAtraso
                                    vals.update({
                                        'salidaLaboral': marcaSalida + timedelta(hours=6),
                                        'deduccionSalidaTemprana': salario * totalAtraso,
                                    })
                            else:
                                salario = contrato.salario / 4
                                salario /= diaslaborales
                                salario /= (contrato.jornadaLaboral / 2)
                                salario /= 60
                                deduccionTotal += salario * 15
                                tipoDeduccion += 'Omision de Marca Salida, \n'
                                vals.update({
                                    'salidaLaboral': False,
                                    'deduccionOmisionMarca': salario * 15 + vals['deduccionOmisionMarca'],
                                })

                            salida = marcaSalida - marcaSalidaDB

                            totalTiempoExtra = (salida.total_seconds()) / 60

                            if totalTiempoExtra >= 30 and totalTiempoExtra <= 44:
                                horas = 1
                                tiempoLaboral = 0
                                if tiempoLaboralMarcas >= tiempoLaboralDB:
                                    if fechaInicio.weekday() != 5:
                                        tiempoLaboral = ((tiempoLaboralDB - timedelta(minutes=float(contrato.tiempoAlmuerzo))).seconds  / 3600)
                                    else:
                                        tiempoLaboral = (tiempoLaboralDB.seconds / 3600)
                                else:
                                    tiempoLaboral = ((tiempoLaboralMarcas - timedelta(minutes=float(contrato.tiempoAlmuerzo))).seconds  / 3600)
                                tiempoAcumuladoDict.update({
                                    'tiempoLaboral': tiempoLaboral,
                                    'tiempoExtra': horas * 60,
                                })
                                tiempoAcumuladolist.append(tiempoAcumuladoDict)
                                vals.update({
                                    'tiempoLaboral': tiempoLaboral,
                                    'tiempoExtra': 30,
                                    'estado': tipoDeduccion,
                                    'deduccionOmisionMarca': 0,
                                    'deduccionAusencia': 0,
                                    'deduccionTotal': 0,
                                })
                            elif totalTiempoExtra > 45:
                                horas = 1
                                if totalTiempoExtra > 60:
                                    horas = math.trunc(totalTiempoExtra / 60)
                                tiempoLaboral = 0
                                if tiempoLaboralMarcas >= tiempoLaboralDB:
                                    if fechaInicio.weekday() != 5:
                                        tiempoLaboral = ((tiempoLaboralDB - timedelta(minutes=float(contrato.tiempoAlmuerzo))).seconds  / 3600)
                                    else:
                                        tiempoLaboral = (tiempoLaboralDB.seconds / 3600)
                                else:
                                    tiempoLaboral = ((tiempoLaboralMarcas - timedelta(minutes=float(contrato.tiempoAlmuerzo))).seconds  / 3600)

                                tiempoAcumuladoDict.update({
                                    'tiempoLaboral': tiempoLaboral,
                                    'tiempoExtra': horas * 60,
                                })
                                tiempoAcumuladolist.append(tiempoAcumuladoDict)
                                vals.update({
                                    'tiempoLaboral': tiempoLaboral,
                                    'tiempoExtra': horas * 60,
                                    'estado': tipoDeduccion,
                                    'deduccionOmisionMarca': 0,
                                    'deduccionAusencia': 0,
                                    'deduccionTotal': 0,
                                })
                            else:
                                tiempoLaboral = 0
                                if tiempoLaboralMarcas >= tiempoLaboralDB:
                                    if fechaInicio.weekday() != 5:
                                        tiempoLaboral = ((tiempoLaboralDB - timedelta(minutes=float(contrato.tiempoAlmuerzo))).seconds  / 3600)
                                    else:
                                        tiempoLaboral = (tiempoLaboralDB.seconds / 3600)
                                else:
                                    tiempoLaboral = ((tiempoLaboralMarcas - timedelta(minutes=float(contrato.tiempoAlmuerzo))).seconds  / 3600)

                                tiempoAcumuladoDict.update({
                                    'tiempoLaboral': tiempoLaboral,
                                })
                                tiempoAcumuladolist.append(tiempoAcumuladoDict)
                                vals.update({
                                    'tiempoLaboral': tiempoLaboral,
                                    'tiempoExtra': 0,
                                    'estado': tipoDeduccion,
                                })

                            tiempoCafeM = math.trunc(((marcaSalidaCafeM.hour + (marcaSalidaCafeM.minute / 60)) - (
                                    marcaEntradaCafeM.hour + (marcaEntradaCafeM.minute / 60))) * 60)
                            if marcaSalidaCafeM != datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M"):
                                if tiempoCafeM > 15:
                                    salario = contrato.salario / 4
                                    salario /= diaslaborales
                                    salario /= (contrato.jornadaLaboral / 2)
                                    salario /= 60
                                    deduccionTotal += salario * (tiempoCafeM - 15)
                                    tipoDeduccion += 'Tiempo no laborado cafe mañana ' + str(tiempoCafeM - 15) + ' , \n'
                                    vals.update({
                                        'deduccionCafeM': salario * (tiempoCafeM - 15),
                                    })
                                else:
                                    vals.update({
                                        'deduccionCafeM': 0,
                                    })

                            tiempoCafeT = math.trunc(((marcaSalidaCafeT.hour + (marcaSalidaCafeT.minute / 60)) - (
                                    marcaEntradaCafeT.hour + (marcaEntradaCafeT.minute / 60))) * 60)
                            if marcaSalidaCafeT != datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M"):
                                if tiempoCafeT > 15:
                                    salario = contrato.salario / 4
                                    salario /= diaslaborales
                                    salario /= (contrato.jornadaLaboral / 2)
                                    salario /= 60
                                    deduccionTotal += salario * (tiempoCafeT - 15)
                                    tipoDeduccion += 'Tiempo no laborado cafe tarde ' + str(tiempoCafeT - 15) + ' , \n'
                                    vals.update({
                                        'deduccionCafeT': salario * (tiempoCafeT - 15),
                                    })

                                else:
                                    vals.update({
                                        'deduccionCafeT': 0,
                                    })

                                tiempoAlmuerzo = math.trunc(((marcaSalidaA.hour + (marcaSalidaA.minute / 60)) - (marcaEntradaA.hour + (marcaEntradaA.minute / 60))) * 60)
                            if marcaEntradaA != datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M"):
                                if tiempoAlmuerzo > 60:
                                    salario = contrato.salario / 4
                                    salario /= diaslaborales
                                    salario /= (contrato.jornadaLaboral / 2)
                                    salario /= 60
                                    deduccionTotal += salario * (tiempoAlmuerzo - 60)
                                    tipoDeduccion += 'Tiempo no laborado almuerzo ' + str(tiempoAlmuerzo - 60) + ' , \n'
                                    vals.update({
                                        'deduccionAlmuerzo': salario * (tiempoAlmuerzo - 60),
                                    })
                                else:
                                    vals.update({
                                        'deduccionAlmuerzo': 0,
                                    })
                            else:
                                vals.update({
                                    'deduccionAlmuerzo': 0,
                                })

                            vals.update({
                                'deduccionTotal': deduccionTotal,
                                'deduccionOmisionMarca': 0,
                                'deduccionAusencia': 0,
                                'estado': tipoDeduccion,
                            })

                            asistencia = list(filter(lambda x: (x.asistencia_id.id == dataEmpleado.id) and
                                                               (x.empleado_id.id == dataEmpleado.empleado_id.id) and
                                                               (x.diaMarca == fechaInicio),
                                                     dataEmpleado.asistencia_line_ids))

                            if asistencia:
                                dataEmpleado.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                            else:
                                dataEmpleado.asistencia_line_ids = [(0, 0, vals)]

                            fechaInicio += timedelta(days=1)
                            continue
                        else:
                            vacaciones = list(filter(lambda x: (x.fechaInicioVacaciones <= fechaInicio) and (x.fechaFinVacaciones >= fechaInicio), vacacionesEmpleado))
                            incapacidad = list(filter(lambda x: (x.fechaInicioIncapacidad <= fechaInicio) and (x.fechaFinIncapacidad >= fechaInicio), incapacidadesEmpleado))
                            diasLibres = list(filter(lambda x: (x.fecha <= fechaInicio) and (x.fecha >= fechaInicio), diasLibresEmpleado))
                            licencias = list(filter(lambda x: (x.fechaInicioLicencia <= fechaInicio) and (x.fechaFinLicencia >= fechaInicio) and (x.tipoLicencia != 'Paternidad'), licenciasEmpleado))
                            licenciasPaternidad = list(filter(lambda x: (x.fechaPaternidad_1 == fechaInicio) or
                                                                        (x.fechaPaternidad_2 == fechaInicio) or
                                                                        (x.fechaPaternidad_3 == fechaInicio) or
                                                                        (x.fechaPaternidad_4 == fechaInicio) or
                                                                        (x.fechaPaternidad_5 == fechaInicio) or
                                                                        (x.fechaPaternidad_6 == fechaInicio) or
                                                                        (x.fechaPaternidad_7 == fechaInicio) or
                                                                        (x.fechaPaternidad_8 == fechaInicio), licenciasEmpleado))

                            if vacaciones:
                                vals.update({
                                    'entradaLaboral': marcaEntradaDB,
                                    'salidaLaboral': marcaSalidaDB,
                                    'estado': 'Vacaciones',
                                    'deduccionTotal': 0,
                                })
                                asistencia = list(filter(lambda x: (x.asistencia_id.id == dataEmpleado.id) and
                                                                   (x.empleado_id.id == dataEmpleado.empleado_id.id) and
                                                                   (x.diaMarca == fechaInicio),
                                                         dataEmpleado.asistencia_line_ids))

                                if asistencia:
                                    dataEmpleado.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                                else:
                                    dataEmpleado.asistencia_line_ids = [(0, 0, vals)]
                            elif incapacidad:
                                if incapacidad[0].tipoIncapacidad == 'SEM':
                                    if cantidadIncapacidadesSEM > 3:
                                        salario = contrato.salario / 4
                                        salario /= diaslaborales
                                        vals.update({

                                            'entradaLaboral': marcaEntradaDB,
                                            'salidaLaboral': marcaSalidaDB,
                                            'estado': 'Incapacidad SEM',
                                            'deduccionTotal': salario,
                                        })
                                        asistencia = list(filter(lambda x: (x.asistencia_id.id == dataEmpleado.id) and
                                                                           (x.empleado_id.id == dataEmpleado.empleado_id.id) and
                                                                           (x.diaMarca == fechaInicio),
                                                                 dataEmpleado.asistencia_line_ids))

                                        if asistencia:
                                            dataEmpleado.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                                        else:
                                            dataEmpleado.asistencia_line_ids = [(0, 0, vals)]
                                        cantidadIncapacidadesSEM += 1
                                        dataEmpleado.diasPagoCompleto -= 1
                                        dataEmpleado.diasSinPago -= 1
                                    else:
                                        salario = contrato.salario / 4
                                        salario /= diaslaborales
                                        vals.update({
                                            'entradaLaboral': marcaEntradaDB,
                                            'salidaLaboral': marcaSalidaDB,
                                            'estado': 'Incapacidad SEM',
                                            'deduccionTotal': salario / 2,
                                        })
                                        asistencia = list(filter(lambda x: (x.asistencia_id.id == dataEmpleado.id) and
                                                                           (x.empleado_id.id == dataEmpleado.empleado_id.id) and
                                                                           (x.diaMarca == fechaInicio),
                                                                 dataEmpleado.asistencia_line_ids))

                                        if asistencia:
                                            dataEmpleado.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                                        else:
                                            dataEmpleado.asistencia_line_ids = [(0, 0, vals)]
                                        cantidadIncapacidadesSEM += 1
                                        dataEmpleado.diasPagoMitad += 1
                                        dataEmpleado.diasPagoCompleto -= 1
                                elif incapacidad[0].tipoIncapacidad == 'INS':
                                    salario = contrato.salario / 4
                                    salario /= diaslaborales
                                    vals.update({

                                        'entradaLaboral': marcaEntradaDB,
                                        'salidaLaboral': marcaSalidaDB,
                                        'estado': 'Incapacidad INS',
                                        'deduccionTotal': salario,
                                    })
                                    asistencia = list(filter(lambda x: (x.asistencia_id.id == dataEmpleado.id) and
                                                                       (x.empleado_id.id == dataEmpleado.empleado_id.id) and
                                                                       (x.diaMarca == fechaInicio),
                                                             dataEmpleado.asistencia_line_ids))

                                    if asistencia:
                                        dataEmpleado.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                                    else:
                                        dataEmpleado.asistencia_line_ids = [(0, 0, vals)]
                                elif incapacidad[0].tipoIncapacidad == 'MAT':
                                    salario = contrato.salario / 4
                                    salario /= diaslaborales
                                    salario /= (contrato.jornadaLaboral / 2)
                                    salario /= 60
                                    vals.update({

                                        'entradaLaboral': marcaEntradaDB,
                                        'salidaLaboral': marcaSalidaDB,
                                        'estado': 'Incapacidad MAT',
                                        'deduccionTotal': 0,
                                    })
                                    asistencia = list(filter(lambda x: (x.asistencia_id.id== dataEmpleado.id) and
                                                                       (x.empleado_id.id == dataEmpleado.empleado_id.id) and
                                                                       (x.diaMarca == fechaInicio),
                                                             dataEmpleado.asistencia_line_ids))

                                    if asistencia:
                                        dataEmpleado.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                                    else:
                                        dataEmpleado.asistencia_line_ids = [(0, 0, vals)]
                            elif diasLibres:
                                vals.update({
                                    'entradaLaboral': marcaEntradaDB,
                                    'salidaLaboral': marcaSalidaDB,
                                    'estado': diasLibres[0].razon,
                                    'deduccionTotal': 0,
                                })
                                asistencia = list(filter(lambda x: (x.asistencia_id.id == dataEmpleado.id) and
                                                                   (x.empleado_id.id == dataEmpleado.empleado_id.id) and
                                                                   (x.diaMarca == fechaInicio),
                                                         dataEmpleado.asistencia_line_ids))

                                if asistencia:
                                    dataEmpleado.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                                else:
                                    dataEmpleado.asistencia_line_ids = [(0, 0, vals)]
                            elif licencias:
                                vals = {}
                                salario = contrato.salario / 4
                                salario /= diaslaborales
                                if licencias[0].tipoPago == "Sin pago":
                                    vals.update({
                                        'entradaLaboral': False,
                                        'salidaLaboral': False,
                                        'estado': 'Ausencia',
                                        'deduccionTotal': salario,
                                    })
                                elif licencias[0].tipoPago == "Pago medio":
                                    vals.update({
                                        'entradaLaboral': marcaEntradaDB,
                                        'salidaLaboral': marcaSalidaDB,
                                        'estado': 'Incapacidad SEM',
                                        'deduccionTotal': salario / 2,
                                    })
                                else:
                                    vals.update({
                                        'entradaLaboral': marcaEntradaDB,
                                        'salidaLaboral': marcaSalidaDB,
                                        'estado': 'Vacaciones',
                                        'deduccionTotal': 0,
                                    })
                                asistencia = list(filter(lambda x: (x.asistencia_id.id == dataEmpleado.id) and
                                                                   (x.empleado_id.id == dataEmpleado.empleado_id.id) and
                                                                   (x.diaMarca == fechaInicio),
                                                         dataEmpleado.asistencia_line_ids))

                                if asistencia:
                                    dataEmpleado.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                                else:
                                    dataEmpleado.asistencia_line_ids = [(0, 0, vals)]
                            else:
                                salario = contrato.salario / 4
                                salario /= diaslaborales
                                vals.update({
                                    'entradaLaboral': False,
                                    'salidaLaboral': False,
                                    'estado': 'Ausencia',
                                    'deduccionTotal': salario,
                                })
                                asistencia = list(filter(lambda x: (x.asistencia_id.id == dataEmpleado.id) and
                                                                   (x.empleado_id.id == dataEmpleado.empleado_id.id) and
                                                                   (x.diaMarca == fechaInicio),dataEmpleado.asistencia_line_ids))

                                if asistencia:
                                    dataEmpleado.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                                else:
                                    dataEmpleado.asistencia_line_ids = [(0, 0, vals)]

                            fechaInicio += timedelta(days=1)
                            continue

                else:
                    fechaInicio += timedelta(days=1)
                    continue

                fechaInicio += timedelta(days=1)


            # tiempoContrato = self.env['contrato.empleado.add.tiempo.acumulado.line'].search(['&', ('contratoEmpleado_id', '=', contrato.id), ('periodoPago', '=', dataEmpleado.name)])
            # vals = {}
            # inicioSemana1 = self.desde
            # finsemana1 = self.desde + timedelta(days=6)
            # inicioSemana2 = finsemana1 + timedelta(days=1)
            # finsemana2 = inicioSemana2 + timedelta(days=6)
            # tiempolaboradosemana1 = 0
            # tiempolaboradosemana2 = 0
            # tiempoAcumuladosemana1 = 0
            # tiempoAcumuladosemana2 = 0
            # tiempoLaborralHorario1 = 0
            # tiempoLaborralHorario2 = 0
            # index = 0
            # if len(tiempoAcumuladolist) > 0:
            #     while inicioSemana1 <= finsemana1:
            #         for dia in tiempoAcumuladolist:
            #             if dia['dia'] == inicioSemana1:
            #                 tiempolaboradosemana1 += dia['tiempoLaboral']
            #                 tiempoAcumuladosemana1 += dia['tiempoExtra']
            #                 tiempoLaborralHorario1 += dia['tiempoLaborralHorario']
            #         inicioSemana1 += timedelta(days=1)
            #
            #     while inicioSemana2 <= finsemana2:
            #         for dia in tiempoAcumuladolist:
            #             if dia['dia'] == inicioSemana2:
            #                 tiempolaboradosemana2 += dia['tiempoLaboral']
            #                 tiempoAcumuladosemana2 += dia['tiempoExtra']
            #                 tiempoLaborralHorario2 += dia['tiempoLaborralHorario']
            #         inicioSemana2 += timedelta(days=1)
            #
            #     if tiempolaboradosemana1 >= tiempoLaborralHorario1:
            #         if tiempoAcumuladosemana1 > 0:
            #             vals = {
            #                 'contratoEmpleado_id': contrato.id,
            #                 'empleado_id': dataEmpleado.empleado_id.id,
            #                 'fechaCorteAcumulacion': self.desde,
            #                 'periodoPago': dataEmpleado.name,
            #                 'tiempoAcumulado': tiempoAcumuladosemana1,
            #             }
            #
            #     if tiempolaboradosemana2 >= tiempoLaborralHorario2:
            #         if tiempoAcumuladosemana2 > 0:
            #             vals = {
            #                 'contratoEmpleado_id': contrato.id,
            #                 'empleado_id': dataEmpleado.empleado_id.id,
            #                 'fechaCorteAcumulacion': self.desde,
            #                 'periodoPago': dataEmpleado.name,
            #                 'tiempoAcumulado': tiempoAcumuladosemana2,
            #             }
            #
            #     tiempoTotalAcumular = tiempoAcumuladosemana1 + tiempoAcumuladosemana2
            #
            #     if tiempoTotalAcumular > 0 and vals:
            #
            #         if tiempoContrato:
            #             contrato.timepoAcumuladoAdd_ids = [(1, tiempoContrato.id, vals)]
            #             contrato.tiempoAcumuladoTotal += tiempoTotalAcumular
            #             contrato.tiempoAcumuladoRestante += tiempoTotalAcumular
            #         else:
            #             contrato.timepoAcumuladoAdd_ids = [(0, 0, vals)]
            #             contrato.tiempoAcumuladoTotal += tiempoTotalAcumular
            #             contrato.tiempoAcumuladoRestante += tiempoTotalAcumular

    def generar_asistencia(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('nomina.urlWSOdoo') + '/api/AsistenciaAdministrativaUIA/getAsistenciaEmpleado'
        horarioDia = any
        tiempoAcumuladolist = []

        empleadosPlanilla =  self.env['planilla.personal.empleados.planilla'].search(['&', ('pago', '=', self.pago), ('peridoPago_id', '=', self.periodoPago_id.id)])

        if self.administrativo_id:
            empleadosPlanilla = self.env['planilla.personal.empleados.planilla'].search(['&',('empleado_id','=',self.administrativo_id.id), ('pago', '=', self.pago), ('peridoPago_id', '=', self.periodoPago_id.id)])

        for dataEmpleado in empleadosPlanilla:
            fechaInicio = self.desde
            dataEmpleado.desde = self.desde
            dataEmpleado.hasta = self.hasta
            contrato = self.env['contrato.empleado'].search([('empleado_id', '=', dataEmpleado.empleado_id.id)])

            incapacidadesEmpleado = list(filter(lambda x: (x.fechaFinIncapacidad >= self.desde) and
                                                          (x.empleado_id.id == dataEmpleado.empleado_id.id),contrato.incapacidades_ids))

            vacacionesEmpleado = list(filter(lambda x: (x.fechaFinVacaciones >= self.desde) and
                                                       (x.empleado_id.id == dataEmpleado.empleado_id.id),contrato.vacaciones_ids))

            licenciasEmpleado = list(filter(lambda x: (x.fechaFinLicencia >= self.desde) and
                                                      (x.empleado_id.id == dataEmpleado.empleado_id.id) and
                                                      (x.estadoRH == 'Aceptado'),contrato.licencias_ids))

            diasLibresEmpleado = list(filter(lambda x: (x.fecha >= self.desde), self.periodoPago_id.diasLibres_ids))

            for vacaciones in vacacionesEmpleado:
                dataEmpleado.vacaciones_ids = [[4, vacaciones.id]]

            for incapacidad in incapacidadesEmpleado:
                dataEmpleado.incapacidades_ids = [[4, incapacidad.id]]

            for licencias in licenciasEmpleado:
                dataEmpleado.licecnias_ids = [[4, licencias.id]]

            deduccionTotal = 0
            diaslaborales = 0
            while fechaInicio <= self.hasta:
                tipoDeduccion = ''
                if fechaInicio.weekday() == 0:
                    diaslaborales = self._get_dias_laborales(dataEmpleado, fechaInicio, horarioDia)

                deduccionTotal = 0
                horarioEmpleado = self.env['horario.empleado'].search([('empleado_id', '=', dataEmpleado.empleado_id.id)])

                if horarioEmpleado:
                    horarioDia = self.env['horario.empleado.line'].search(['&', ('fechaDesde', '<=', fechaInicio), ('fechaHasta', '>=', fechaInicio),('horarioEmpleado_id', '=', horarioEmpleado.id)])
                else:
                    fechaInicio += timedelta(days=1)
                    continue

                vals = {
                    'asistencia_id': dataEmpleado.id,
                    'empleado_id': dataEmpleado.empleado_id.id,
                    'diaMarca': fechaInicio,
                    'deduccionOmisionMarca': 0,
                    'aplicar': True
                }

                horarioDB = self._get_horario_DB(dataEmpleado, fechaInicio, horarioDia)

                if not horarioDB:
                    fechaInicio += timedelta(days=1)
                    continue

                vals.update({
                    'horario': horarioDB['horario'],
                })

                marcaSalidaDB = horarioDB['marcaSalidaDB']
                marcaEntradaDB = horarioDB['marcaEntradaDB']

                dataJSon = {
                    'codigoMarca': contrato.codigoMarca,
                    'fechaMarca': str(fechaInicio),
                }
                header = {
                    'Content-Type': 'application/json',
                    'Accept': 'text/plain'
                }
                response = requests.post(url, headers=header, json=dataJSon, verify=False)

                if response.status_code == 200:
                    tiempoAcumuladoDict = {
                        'dia': fechaInicio,
                        'diasTrabajo': diaslaborales,
                        'tiempoExtra': 0,
                        'tiempoLaboral': 0,
                    }

                    if len(response.json()['data']) > 0:

                        asistenciaList = []
                        asistenciaListB = []
                        for data in response.json()['data']:
                            asistenciaList.append(datetime.strptime(data['datetime'], "%Y-%m-%d %H:%M"))
                            asistenciaListB.append(datetime.strptime(data['datetime'], "%Y-%m-%d %H:%M"))

                        if len(asistenciaList) >= 2:
                            marcaSalida = max(asistenciaList)
                            marcaEntrada = min(asistenciaList)
                        else:
                            salario = 0
                            if diaslaborales >= 5:
                                salario = contrato.salario / 30
                            else:
                                salario = contrato.salario / (diaslaborales * 4)
                            vals.update({
                                'entradaLaboral': False,
                                'salidaLaboral': False,
                                'estado': 'Ausencia',
                                'deduccionTotal': salario,
                            })
                            asistencia = list(filter(lambda x: (x.asistencia_id.id == dataEmpleado.id) and
                                                               (x.empleado_id.id == dataEmpleado.empleado_id.id) and
                                                               (x.diaMarca == fechaInicio),dataEmpleado.asistencia_line_ids))

                            if asistencia:
                                dataEmpleado.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                            else:
                                dataEmpleado.asistencia_line_ids = [(0, 0, vals)]

                            fechaInicio += timedelta(days=1)
                            continue

                        tiempoLaboralDB = marcaSalidaDB - marcaEntradaDB
                        tiempoLaboralMarcas = marcaSalida - marcaEntradaDB

                        tiempoAcumuladoDict.update({
                            'tiempoLaborralHorario': (tiempoLaboralDB.seconds / 3600) - 1,
                        })

                        if tiempoLaboralMarcas >= tiempoLaboralDB:
                            asistenciaList.remove(marcaEntrada)
                            asistenciaList.remove(marcaSalida)
                            asistenciaListB.remove(marcaEntrada)
                            asistenciaListB.remove(marcaSalida)

                        else:
                            if marcaEntrada >= (marcaEntradaDB - timedelta(hours=1)) and marcaEntrada <= (
                                    marcaEntradaDB + timedelta(minutes=30)):
                                asistenciaList.remove(marcaEntrada)
                            else:
                                for marca in asistenciaList:
                                    if marca >= (marcaEntradaDB - timedelta(hours=1)) and marca <= (
                                            marcaEntradaDB + timedelta(minutes=30)):
                                        marcaEntrada = marca
                                        asistenciaList.remove(marcaEntrada)
                                    else:
                                        marcaEntrada = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                            if marcaSalida >= marcaSalidaDB - timedelta(minutes=15):
                                asistenciaList.remove(marcaSalida)

                            else:
                                for marca in asistenciaList:
                                    if marca >= (marcaSalidaDB - timedelta(minutes=15)):
                                        marcaSalida = marca
                                        asistenciaList.remove(marcaSalida)
                                    else:
                                        marcaSalida = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")

                        tiempoCafeM = False
                        tiempoCafeT = False
                        tiempoAlmuerzo = False
                        marcaEntradaCafeM = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                        marcaSalidaCafeM = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                        marcaEntradaA = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                        marcaSalidaA = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                        marcaEntradaCafeT = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                        marcaSalidaCafeT = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                        for marca in asistenciaList:
                            for marcaB in asistenciaListB:
                                tiempomarca = math.trunc(((marca.hour + (marca.minute / 60)) - (
                                        marcaB.hour + (marcaB.minute / 60))) * 60)

                                if tiempomarca > 0 and tiempomarca <= 20 and tiempoCafeM == False and marcaB != marca and marcaB.hour < 11:
                                    marcaEntradaCafeM = marcaB
                                    marcaSalidaCafeM = marca
                                    tiempoCafeM = True

                            for marcaB in asistenciaListB:

                                tiempomarca = math.trunc(((marca.hour + (marca.minute / 60)) - (
                                        marcaB.hour + (marcaB.minute / 60))) * 60)

                                if tiempomarca > 0 and tiempomarca <= 65 and tiempoAlmuerzo == False and marcaB != marcaEntradaCafeM and marca != marcaSalidaCafeM and marcaB.hour >= 11:
                                    marcaEntradaA = marcaB
                                    marcaSalidaA = marca
                                    tiempoAlmuerzo = True

                            for marcaB in asistenciaListB:

                                tiempomarca = math.trunc(((marca.hour + (marca.minute / 60)) - (
                                        marcaB.hour + (marcaB.minute / 60))) * 60)

                                if tiempomarca > 0 and tiempomarca <= 15 and tiempoCafeT == False and tiempoAlmuerzo == True and marcaB != marca and marcaB.hour > 12:
                                    marcaEntradaCafeT = marcaB
                                    marcaSalidaCafeT = marca
                                    tiempoCafeT = True

                        if marcaEntradaCafeM > datetime.strptime(str(fechaInicio) + ' 12:00', "%Y-%m-%d %H:%M"):
                            marcaEntradaCafeM = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                            if marcaSalidaCafeM > datetime.strptime(str(fechaInicio) + ' 12:00', "%Y-%m-%d %H:%M"):
                                marcaSalidaCafeM = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")

                        if marcaEntradaCafeT < datetime.strptime(str(fechaInicio) + ' 12:00', "%Y-%m-%d %H:%M"):
                            marcaEntradaCafeT = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")
                            if marcaSalidaCafeT < datetime.strptime(str(fechaInicio) + ' 12:00', "%Y-%m-%d %H:%M"):
                                marcaSalidaCafeT = datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M")

                        if marcaEntrada != datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M"):
                            if marcaEntrada >= (marcaEntradaDB - timedelta(hours=1)) and marcaEntrada <= (
                                    marcaEntradaDB + timedelta(minutes=5)):
                                vals.update({
                                    'entradaLaboral': marcaEntrada + timedelta(hours=6),
                                })

                            else:
                                horaEntradaDB = (marcaEntradaDB + timedelta(minutes=5))
                                entrada = (marcaEntrada - marcaEntradaDB)
                                totalAtraso = math.trunc((entrada.total_seconds()) / 60)
                                salario = contrato.salario / 4
                                salario /= diaslaborales
                                salario /= (contrato.jornadaLaboral / 2)
                                salario /= 60
                                deduccionTotal += salario * totalAtraso
                                tipoDeduccion = 'Entrada Tardia \n'
                                vals.update({
                                    'entradaLaboral': marcaEntrada + timedelta(hours=6),
                                    'deduccionEntradaTardia': salario * totalAtraso,
                                })
                        else:
                            salario = contrato.salario / 4
                            salario /= diaslaborales
                            salario /= (contrato.jornadaLaboral / 2)
                            salario /= 60
                            deduccionTotal += salario * 15
                            tipoDeduccion += 'Omision de Marca Entrada \n '
                            vals.update({
                                'entradaLaboral': False,
                                'deduccionOmisionMarca': salario * 15,
                            })

                        if marcaSalida != datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M"):
                            if marcaSalida >= marcaSalidaDB:
                                vals.update({
                                    'salidaLaboral': marcaSalida + timedelta(hours=6),
                                })
                            else:
                                entrada = (marcaSalidaDB - marcaSalida)
                                totalAtraso = round((entrada.total_seconds()) / 60)
                                salario = contrato.salario / 4
                                salario /= diaslaborales
                                salario /= (contrato.jornadaLaboral / 2)
                                salario /= 60
                                tipoDeduccion += 'Salida Temprana, '
                                deduccionTotal += salario * totalAtraso
                                vals.update({
                                    'salidaLaboral': marcaSalida + timedelta(hours=6),
                                    'deduccionSalidaTemprana': salario * totalAtraso,
                                })
                        else:
                            salario = contrato.salario / 4
                            salario /= diaslaborales
                            salario /= (contrato.jornadaLaboral / 2)
                            salario /= 60
                            deduccionTotal += salario * 15
                            tipoDeduccion += 'Omision de Marca Salida, \n'
                            vals.update({
                                'salidaLaboral': False,
                                'deduccionOmisionMarca': salario * 15 + vals['deduccionOmisionMarca'],
                            })

                        salida = marcaSalida - marcaSalidaDB

                        totalTiempoExtra = (salida.total_seconds()) / 60

                        if totalTiempoExtra >= 30 and totalTiempoExtra <= 44:
                            horas = 1
                            tiempoLaboral = 0
                            if tiempoLaboralMarcas >= tiempoLaboralDB:
                                if fechaInicio.weekday() != 5:
                                    tiempoLaboral = ((tiempoLaboralDB - timedelta(
                                        minutes=float(contrato.tiempoAlmuerzo))).seconds / 3600)
                                else:
                                    tiempoLaboral = (tiempoLaboralDB.seconds / 3600)
                            else:
                                tiempoLaboral = ((tiempoLaboralMarcas - timedelta(
                                    minutes=float(contrato.tiempoAlmuerzo))).seconds / 3600)
                            tiempoAcumuladoDict.update({
                                'tiempoLaboral': tiempoLaboral,
                                'tiempoExtra': horas * 60,
                            })
                            tiempoAcumuladolist.append(tiempoAcumuladoDict)
                            vals.update({
                                'tiempoLaboral': tiempoLaboral,
                                'tiempoExtra': 30,
                                'estado': tipoDeduccion,
                                'deduccionOmisionMarca': 0,
                                'deduccionAusencia': 0,
                                'deduccionTotal': 0,
                            })
                        elif totalTiempoExtra >= 45:
                            horas = 1
                            if totalTiempoExtra > 60:
                                horas = math.trunc(totalTiempoExtra / 60)
                            tiempoLaboral = 0
                            if tiempoLaboralMarcas >= tiempoLaboralDB:
                                if fechaInicio.weekday() != 5:
                                    tiempoLaboral = ((tiempoLaboralDB - timedelta(
                                        minutes=float(contrato.tiempoAlmuerzo))).seconds / 3600)
                                else:
                                    tiempoLaboral = (tiempoLaboralDB.seconds / 3600)
                            else:
                                tiempoLaboral = ((tiempoLaboralMarcas - timedelta(
                                    minutes=float(contrato.tiempoAlmuerzo))).seconds / 3600)

                            tiempoAcumuladoDict.update({
                                'tiempoLaboral': tiempoLaboral,
                                'tiempoExtra': horas * 60,
                            })
                            tiempoAcumuladolist.append(tiempoAcumuladoDict)
                            vals.update({
                                'tiempoLaboral': tiempoLaboral,
                                'tiempoExtra': horas * 60,
                                'estado': tipoDeduccion,
                                'deduccionOmisionMarca': 0,
                                'deduccionAusencia': 0,
                                'deduccionTotal': 0,
                            })
                        else:
                            tiempoLaboral = 0
                            if tiempoLaboralMarcas >= tiempoLaboralDB:
                                if fechaInicio.weekday() != 5:
                                    tiempoLaboral = ((tiempoLaboralDB - timedelta(
                                        minutes=float(contrato.tiempoAlmuerzo))).seconds / 3600)
                                else:
                                    tiempoLaboral = (tiempoLaboralDB.seconds / 3600)
                            else:
                                tiempoLaboral = ((tiempoLaboralMarcas - timedelta(
                                    minutes=float(contrato.tiempoAlmuerzo))).seconds / 3600)

                            tiempoAcumuladoDict.update({
                                'tiempoLaboral': tiempoLaboral,
                            })
                            tiempoAcumuladolist.append(tiempoAcumuladoDict)
                            vals.update({
                                'tiempoLaboral': tiempoLaboral,
                                'tiempoExtra': 0,
                                'estado': tipoDeduccion,
                            })

                        tiempoCafeM = math.trunc(((marcaSalidaCafeM.hour + (marcaSalidaCafeM.minute / 60)) - (marcaEntradaCafeM.hour + (marcaEntradaCafeM.minute / 60))) * 60)
                        if marcaSalidaCafeM != datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M"):
                            if tiempoCafeM > 15:
                                salario = contrato.salario / 4
                                salario /= diaslaborales
                                salario /= (contrato.jornadaLaboral / 2)
                                salario /= 60
                                deduccionTotal += salario * (tiempoCafeM - 15)
                                tipoDeduccion += 'Tiempo no laborado cafe mañana ' + str(
                                    tiempoCafeM - 15) + ' , \n'
                                vals.update({
                                    'deduccionCafeM': salario * (tiempoCafeM - 15),
                                })
                            else:
                                vals.update({
                                    'deduccionCafeM': 0,
                                })

                        tiempoCafeT = math.trunc(((marcaSalidaCafeT.hour + (marcaSalidaCafeT.minute / 60)) - (marcaEntradaCafeT.hour + (marcaEntradaCafeT.minute / 60))) * 60)
                        if marcaSalidaCafeT != datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M"):
                            if tiempoCafeT > 15:
                                salario = contrato.salario / 4
                                salario /= diaslaborales
                                salario /= (contrato.jornadaLaboral / 2)
                                salario /= 60
                                deduccionTotal += salario * (tiempoCafeT - 15)
                                tipoDeduccion += 'Tiempo no laborado cafe tarde ' + str(tiempoCafeT - 15) + ' , \n'
                                vals.update({
                                    'deduccionCafeT': salario * (tiempoCafeT - 15),
                                })

                            else:
                                vals.update({
                                    'deduccionCafeT': 0,
                                })

                            tiempoAlmuerzo = math.trunc(((marcaSalidaA.hour + (marcaSalidaA.minute / 60)) - (marcaEntradaA.hour + (marcaEntradaA.minute / 60))) * 60)
                        if marcaEntradaA != datetime.strptime('1993-10-07 00:00', "%Y-%m-%d %H:%M"):
                            if tiempoAlmuerzo > int(contrato.tiempoAlmuerzo):
                                salario = contrato.salario / 4
                                salario /= diaslaborales
                                salario /= (contrato.jornadaLaboral / 2)
                                salario /= 60
                                deduccionTotal += salario * (tiempoAlmuerzo - int(contrato.tiempoAlmuerzo))
                                tipoDeduccion += 'Tiempo no laborado almuerzo ' + str(
                                    tiempoAlmuerzo - int(contrato.tiempoAlmuerzo)) + ' , \n'
                                vals.update({
                                    'deduccionAlmuerzo': salario * (tiempoAlmuerzo - int(contrato.tiempoAlmuerzo)),
                                })
                            else:
                                vals.update({
                                    'deduccionAlmuerzo': 0,
                                })
                        else:
                            vals.update({
                                'deduccionAlmuerzo': 0,
                            })

                        vals.update({
                            'deduccionTotal': deduccionTotal,
                            'deduccionOmisionMarca': 0,
                            'deduccionAusencia': 0,
                            'estado': tipoDeduccion,
                        })

                        asistencia = list(filter(lambda x: (x.asistencia_id.id == dataEmpleado.id) and
                                                           (x.empleado_id.id == dataEmpleado.empleado_id.id) and
                                                           (x.diaMarca == fechaInicio),
                                                 dataEmpleado.asistencia_line_ids))

                        if asistencia:
                            dataEmpleado.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                        else:
                            dataEmpleado.asistencia_line_ids = [(0, 0, vals)]

                        fechaInicio += timedelta(days=1)
                        continue


                    else:
                        vacaciones = list(filter(lambda x: (x.fechaInicioVacaciones <= fechaInicio) and
                                                           ( x.fechaFinVacaciones >= fechaInicio), vacacionesEmpleado))

                        incapacidad = list(filter(lambda x: (x.fechaInicioIncapacidad <= fechaInicio) and
                                                            (x.fechaFinIncapacidad >= fechaInicio), incapacidadesEmpleado))
                        diasLibres = list(filter(lambda x: (x.fecha <= fechaInicio) and
                                                           (x.fecha >= fechaInicio), diasLibresEmpleado))

                        licencias = list(filter(lambda x: (x.fechaInicioLicencia <= fechaInicio) and
                                                          (x.fechaFinLicencia >= fechaInicio) and
                                                          (x.tipoLicencia != 'Paternidad'),licenciasEmpleado))

                        licenciasPaternidad = list(filter(lambda x: (x.fechaPaternidad_1 == fechaInicio) or
                                                                    (x.fechaPaternidad_2 == fechaInicio) or
                                                                    (x.fechaPaternidad_3 == fechaInicio) or
                                                                    (x.fechaPaternidad_4 == fechaInicio) or
                                                                    (x.fechaPaternidad_5 == fechaInicio) or
                                                                    (x.fechaPaternidad_6 == fechaInicio) or
                                                                    (x.fechaPaternidad_7 == fechaInicio) or
                                                                    (x.fechaPaternidad_8 == fechaInicio),licenciasEmpleado))

                        if vacaciones:
                            vals.update({
                                'entradaLaboral': marcaEntradaDB + timedelta(hours=6),
                                'salidaLaboral': marcaSalidaDB + timedelta(hours=6),
                                'estado': 'Vacaciones',
                                'deduccionTotal': 0,
                            })
                        elif incapacidad:
                            if incapacidad[0].tipoIncapacidad == 'SEM':
                                if cantidadIncapacidadesSEM > 3:
                                    salario = contrato.salario / 4
                                    salario /= diaslaborales
                                    vals.update({

                                        'entradaLaboral': marcaEntradaDB + timedelta(hours=6),
                                        'salidaLaboral': marcaSalidaDB + timedelta(hours=6),
                                        'estado': 'Incapacidad SEM',
                                        'deduccionTotal': salario,
                                    })
                                    cantidadIncapacidadesSEM += 1
                                    dataEmpleado.diasPagoCompleto -= 1
                                    dataEmpleado.diasSinPago -= 1
                                else:
                                    salario = contrato.salario / 4
                                    salario /= diaslaborales
                                    vals.update({
                                        'entradaLaboral': marcaEntradaDB + timedelta(hours=6),
                                        'salidaLaboral': marcaSalidaDB + timedelta(hours=6),
                                        'estado': 'Incapacidad SEM',
                                        'deduccionTotal': salario / 2,
                                    })
                                    cantidadIncapacidadesSEM += 1
                                    dataEmpleado.diasPagoMitad += 1
                                    dataEmpleado.diasPagoCompleto -= 1
                            elif incapacidad[0].tipoIncapacidad == 'INS':
                                salario = contrato.salario / 4
                                salario /= diaslaborales
                                vals.update({

                                    'entradaLaboral': marcaEntradaDB + timedelta(hours=6),
                                    'salidaLaboral': marcaSalidaDB + timedelta(hours=6),
                                    'estado': 'Incapacidad INS',
                                    'deduccionTotal': salario,
                                })
                            elif incapacidad[0].tipoIncapacidad == 'MAT':
                                salario = contrato.salario / 4
                                salario /= diaslaborales
                                salario /= (contrato.jornadaLaboral / 2)
                                salario /= 60
                                vals.update({

                                    'entradaLaboral': marcaEntradaDB + timedelta(hours=6),
                                    'salidaLaboral': marcaSalidaDB + timedelta(hours=6),
                                    'estado': 'Incapacidad MAT',
                                    'deduccionTotal': 0,
                                })

                        elif diasLibres:
                            vals.update({
                                'entradaLaboral': marcaEntradaDB + timedelta(hours=6),
                                'salidaLaboral': marcaSalidaDB + timedelta(hours=6),
                                'estado': diasLibres[0].razon,
                                'deduccionTotal': 0,
                            })
                        elif licencias:
                            vals = {}
                            salario = contrato.salario / 4
                            salario /= diaslaborales
                            if licencias[0].tipoPago == "Sin pago":
                                vals.update({
                                    'entradaLaboral': False,
                                    'salidaLaboral': False,
                                    'estado': 'Ausencia',
                                    'deduccionTotal': salario,
                                })
                            elif licencias[0].tipoPago == "Pago medio":
                                vals.update({
                                    'entradaLaboral': marcaEntradaDB + timedelta(hours=6),
                                    'salidaLaboral': marcaSalidaDB + timedelta(hours=6),
                                    'estado': 'Incapacidad SEM',
                                    'deduccionTotal': salario / 2,
                                })
                            else:
                                vals.update({
                                    'entradaLaboral': marcaEntradaDB + timedelta(hours=6),
                                    'salidaLaboral': marcaSalidaDB + timedelta(hours=6),
                                    'estado': 'Vacaciones',
                                    'deduccionTotal': 0,
                                })
                        else:
                            salario = contrato.salario / 4
                            salario /= diaslaborales
                            vals.update({
                                'entradaLaboral': False,
                                'salidaLaboral': False,
                                'estado': 'Ausencia',
                                'deduccionTotal': salario,
                            })

                        asistencia = list(filter(lambda x: (x.asistencia_id.id == dataEmpleado.id) and
                                                           (x.empleado_id.id == dataEmpleado.empleado_id.id) and
                                                           (x.diaMarca == fechaInicio),
                                                 dataEmpleado.asistencia_line_ids))

                        if asistencia:
                            dataEmpleado.asistencia_line_ids = [(1, asistencia[0].id, vals)]
                        else:
                            dataEmpleado.asistencia_line_ids = [(0, 0, vals)]

                        fechaInicio += timedelta(days=1)
                        continue

                fechaInicio += timedelta(days=1)