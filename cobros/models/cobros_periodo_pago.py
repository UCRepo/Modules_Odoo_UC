# -*- coding: utf-8 -*-
from datetime import datetime

import pytz
import requests
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CoborosPeriodoPago(models.Model):
    _name="cobros.periodo.pago"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Periodo de Pagos"

    activo = fields.Boolean(
        string="Activo",
        default=True
    )
    cuatrimestrePlanilla_id = fields.Many2one(
        string='Periodo',
        tracking=True,
        required=True,
        comodel_name='periodo.cuatrimestre',
    )
    fechaPago = fields.Date(
        string="Vencimiento de Letra",
        required=True,
    )
    fechaInicioBloqueo = fields.Date(
        string="Inicio de Bloqueo",
        required=True,
    )
    porcientoNoBloqueo = fields.Float(
        string="% Minino de Bloqueo",
        help="Pocentaje Minimo de Pago Para no Ser Bloqueado",
        required=False,
    )
    name = fields.Char(
        string="Nombre",
        required=False,
    )
    estudiantesCobro_ids = fields.One2many(
        comodel_name="cobros.periodo.pago.line",
        inverse_name="periodoCobro_id",
        string="Estudiantes",
        required=False,
    )

    estudiantesSearch = fields.Many2many(
        comodel_name="cobros.periodo.pago.line",
        domain="[('periodoCobro_id.id','=', id)]",
        string="Estudiantes",
    )

    estudiantesExcepcion= fields.Many2many(
        comodel_name="cobros.periodo.pago.line",
        relation="cobros_extudiantes_exepcion",
        string="Exepcion",
    )

    miembrosEquipo = fields.Selection(
        string="Ver Lista de",
        selection='_compue_team',
        required=False,
    )

    readonlyCobros = fields.Boolean(
        compute="_compue_readOnly",
        readonly=True,
    )

    def _compue_readOnly(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        empleadosList = []
        readOnly = False
        if ICPSudo.get_param('cobros.equipoTrabajo'):
            for data in ICPSudo.get_param('cobros.equipoTrabajo').split(','):
                if data == str(self.env.uid):
                    readOnly = True

        self.readonlyCobros = readOnly

    def get_datos_cobros(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('cobros.cobrosURLAPI')+'/api/CobrosUC/getCobrosInfo'

        dataJSon = {
            "fechaVencimientoLetra": str(self.fechaPago),
            "estudianteID": [],
            "anno": self.cuatrimestrePlanilla_id.year,
            "periodo": self.cuatrimestrePlanilla_id.decripcion.replace('Q', ''),
        }
        header = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain'
        }
        response = requests.post(url, headers=header, json=dataJSon, verify=False)
        # Caso 1 SJ22024056
        if response.status_code == 200:
            for data in  response.json()['data']:
                porcientoPago = 0
                estado = "LETRA VENCIDA"
                if data['montoPagar'] > 0:
                    porcientoPago = (data['montoPagado'] * 100) / data['montoPagar']
                if porcientoPago >= (self.porcientoNoBloqueo * 100):
                    estado = 'AL DIA SALDO MENOR'
                vals = {
                    'name': str(data['nombreEstudiante']) + ' - ' + str(data['carnetEstudiante']) + ' - ' + str(data['cedulaEstudiante'])  + ' - ' + str(data['correoEstudiante'] ) + ' - ' + str(data['correoInstitucionalEstudiante']) + ' - ' +str(data['numeroLetra']),
                    'nombreEstudiante': data['nombreEstudiante'],
                    'carnetEstudiante': data['carnetEstudiante'],
                    'cedulaEstudiante': data['cedulaEstudiante'],
                    'correoEstudiante': data['correoEstudiante'],
                    'correoInstitucionalEstudiante': data['correoInstitucionalEstudiante'],
                    'telefonoPrimarioEstudiante': data['telefonoPrimarioEstudiante'],
                    'telefonoSecundarioEstudiante': data['telefonoSecundarioEstudiante'],
                    'telefonoPrimarioTrabajoEstudiante': data['telefonoPrimarioTrabajoEstudiante'],
                    'telefonoSecundarioTrabajoEstudiante': data['telefonoSecundarioTrabajoEstudiante'],
                    'numeroLetra': data['numeroLetra'],
                    'montoPagar': data['montoPagar'],
                    'montoPagado': data['montoPagado'],
                    'montoDiferencia': data['montoDiferencia'],
                    'porcientoPago': porcientoPago,
                    'totalLetra': data['total'],
                    'estado': estado,
                    'inicioIntereses': data['inicioInteres'],
                    'categoria': data['categoria'],
                }
                estudiante = list(filter(lambda x: (x.carnetEstudiante == data['carnetEstudiante']) and
                                                   (x.numeroLetra == data['numeroLetra']), self.estudiantesCobro_ids))
                if estudiante:
                    self.estudiantesCobro_ids = [(1, estudiante[0].id, vals)]
                else:
                    self.estudiantesCobro_ids = [(0, 0, vals)]

    def get_datos_cobros_actualizados(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('cobros.cobrosURLAPI')+'/api/CobrosUC/getCobrosInfoID'

        letrasID = []
        listLetras =  list(filter(lambda x: (x.estado != 'AL DIA'), self.estudiantesCobro_ids))
        for data in listLetras:
            letrasID.append(data.numeroLetra)

        dataJSon = {
            "anno": "2022",
            "periodo": "2",
            "fechaVencimientoLetra": str(self.fechaPago),
            "letraID":letrasID
        }
        header = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain'
        }
        response = requests.post(url, headers=header, json=dataJSon, verify=False)

        if response.status_code == 200:
            for data in response.json()['data']:
                estudiante = next(filter(lambda x: x.numeroLetra == data['numeroLEtra'], self.estudiantesCobro_ids))
                estudiante.montoPagar = 0
                estudiante.montoPagado = 0
                estudiante.montoDiferencia = 0
                estudiante.montoDiferencia = 0
                estudiante.porcientoPago = 100
                estudiante.envioNotificacion = False
                estudiante.estado = 'AL DIA'

    def send_notificaciones(self):
        estudiantesList = []
        if len(self.estudiantesSearch) > 0:
            for data in self.estudiantesSearch:
                estudiante = list(filter(lambda x: x.cedulaEstudiante == data.cedulaEstudiante, self.estudiantesExcepcion))
                if not estudiante and data.estado != 'AL DIA':
                    estudiantesList.append(data)
        elif self.env.uid == 1:
            for data in self.estudiantesCobro_ids:
                estudiante = list(filter(lambda x: x.cedulaEstudiante == data.cedulaEstudiante, self.estudiantesExcepcion))
                if not estudiante and data.estado != 'AL DIA':
                    esta = list(filter(lambda x: x.cedulaEstudiante == data.cedulaEstudiante, estudiantesList))
                    if not esta:
                        estudiantesList.append(data)


        for data in estudiantesList:
            user_tz = pytz.timezone(self.env.user.tz)
            fechaActual = pytz.utc.localize(datetime.today()).astimezone(user_tz)
            letras = []
            for dataLetra in list(filter(lambda x: x.cedulaEstudiante == data.cedulaEstudiante, self.estudiantesCobro_ids)):
                # atrasoInteresesLetraPago = dataLetra.montoPagar * (2.75 / 30 / 100 * (fechaActual.date() - self.fechaPago).days)
                # atrasoInteresesLetraTotal = dataLetra.totalLetra * (2.75 / 30 / 100 * (fechaActual.date() - dataLetra.inicioIntereses).days)
                # montoDeuda = round((atrasoInteresesLetraPago + atrasoInteresesLetraTotal), 2)
                dict ={
                    'letra': dataLetra.numeroLetra,
                    # 'monto': ' ₡'+"{:,}".format(montoDeuda),
                }
                letras.append(dict)


            template_id = self.env.ref('cobros.email_notificacion_saldo_moroso').id
            template = self.env['mail.template'].browse(template_id)
            email_values = {'email_to': data.correoEstudiante,
                            'email_from': data.empleadoAsignadoInicial.login,
                            'subject':"Estado de Cuenta"
                            }
            datosCorreo = {
                'nombreEstudiante': data.nombreEstudiante,
                'letras':letras,
                'fechaVencimiento': str(self.fechaPago.day) + ' de '+ self.fechaPago.strftime("%B") + ' de ' + str(self.fechaPago.year),
                'extension': data.empleadoAsignadoInicial.phone,
                'correo': data.empleadoAsignadoInicial.login,
            }
            template.with_context(datosCorreo=datosCorreo).send_mail( self.id, email_values=email_values, force_send=True)

        self.estudiantesSearch = [(6, 0, [])]

    def notificacion_incumplimiento_arreglo(self):
        estudiantesList = []
        if len(self.estudiantesSearch) > 0:
            for data in self.estudiantesSearch:
                if data.fechaFinArreglo <= datetime.today().date():
                    estudiantesList.append(data)
        elif self.env.uid == 1:
            for data in self.estudiantesCobro_ids:
                if data.fechaFinArreglo <= datetime.today().date():
                    esta = list(filter(lambda x: x.cedulaEstudiante == data.cedulaEstudiante, estudiantesList))
                    if not esta:
                        estudiantesList.append(data)


        for data in estudiantesList:
            template_id = self.env.ref('cobros.email_notificacion_incumplimineto_arreglo').id
            template = self.env['mail.template'].browse(template_id)
            email_values = {'email_to': data.correoEstudiante,
                            'email_from': data.empleadoAsignadoInicial.login,
                            'subject': "Incumplimiento de arreglo de pago"
                            }
            datosCorreo = {
                'nombreEstudiante': data.nombreEstudiante,
                'fechaFinArreglo': data.fechaFinArreglo,
                'fechaPago': data.periodoCobro_id.fechaPago,
                'extension': data.empleadoAsignadoInicial.phone,
                'correo': data.empleadoAsignadoInicial.login,
            }
            template.with_context(datosCorreo=datosCorreo).send_mail(self.id, email_values=email_values,force_send=True)
            data.fechaFinArreglo = False
            self.estudiantesExcepcion = [(3, data.id)]

    def set_bloqueo_estudiantes(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('cobros.cobrosURLAPI')+'/api/CobrosUC/setBloqueoUsuarios'

        estudiantesList = []
        if len(self.estudiantesSearch) > 0:
            for data in self.estudiantesSearch:
                estudiante = list(filter(lambda x: x.cedulaEstudiante == data.cedulaEstudiante, self.estudiantesExcepcion))
                if not estudiante and data.estado == 'LETRA VENCIDA':
                    estudiantesList.append(data.cedulaEstudiante)
        elif self.env.uid == 1:
            for data in self.estudiantesCobro_ids:
                estudiante = list(filter(lambda x: x.cedulaEstudiante == data.cedulaEstudiante, self.estudiantesExcepcion))

                if not estudiante and data.estado == 'LETRA VENCIDA':
                    if not data.estudianteBloqueado:
                        estudiantesList.append(data.cedulaEstudiante)

        estudiantesListF = estudiantesList[0:85]
        dataJSon = {
            "anno": "2022",
            "periodo": "2",
            "fechaVencimientoLetra": str(self.fechaPago),
            "estudianteID":estudiantesListF
        }
        header = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain'
        }
        response = requests.post(url, headers=header, json=dataJSon, verify=False)

        if response.status_code == 200:
            # for data in response.json()['data']:
            #     estudiante = list(filter(lambda x: x.cedulaEstudiante == data['estudiante'], self.estudiantesCobro_ids))
            #     message += estudiante[0].nombreEstudiante + "\n"

            for data in estudiantesListF:
                estudianteList = list(filter(lambda x: x.cedulaEstudiante == data, self.estudiantesCobro_ids))

                for estudiante in estudianteList:
                    estudiante.estudianteBloqueado = True

            self.estudiantesSearch = [(6, 0, [])]
        return True

    def set_desbloqueo_estudiantes(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('cobros.cobrosURLAPI')+'/api/CobrosUC/setDesloqueoUsuarios'

        estudiantesList = []
        if len(self.estudiantesSearch) > 0:
            for data in self.estudiantesSearch:
                estudiante = list(filter(lambda x: x.cedulaEstudiante == data.cedulaEstudiante, self.estudiantesExcepcion))
                if not estudiante:
                    estudiantesList.append(data.cedulaEstudiante)
        elif self.env.uid == 1:
            for data in self.estudiantesCobro_ids:
                estudiante = list(filter(lambda x: (x.cedulaEstudiante == data.cedulaEstudiante) and
                                                   (x.estudianteBloqueado == True), self.estudiantesExcepcion))
                if estudiante:
                    estudiantesList.append(data.cedulaEstudiante)
                elif data.estudianteBloqueado == True and (data.estado == 'AL DIA' or data.estado == 'AL DIA SALDO MENOR'):
                    estudiantesList.append(data.cedulaEstudiante)

        estudiantesListF = estudiantesList[0:85]
        if len(estudiantesListF) > 0:
            dataJSon = {
                "anno": "2022",
                "periodo": "2",
                "fechaVencimientoLetra": str(self.fechaPago),
                "estudianteID": estudiantesListF
            }
            header = {
                'Content-Type': 'application/json',
                'Accept': 'text/plain'
            }
            response = requests.post(url, headers=header, json=dataJSon, verify=False)

            if response.status_code == 200:
                # for data in response.json()['data']:
                #     estudiante = list(filter(lambda x: x.cedulaEstudiante == data['estudiante'], self.estudiantesCobro_ids))
                for data in estudiantesListF:
                    estudianteList = list(filter(lambda x: (x.cedulaEstudiante == data) and
                                                           (x.estado == 'AL DIA' ) or
                                                           (x.estado == 'AL DIA SALDO MENOR' ), self.estudiantesCobro_ids))

                    for estudiante in estudianteList:
                        estudiante.estudianteBloqueado = False

                self.estudiantesSearch = [(6, 0, [])]
        return True

    def set_division_estudiantes(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        miembrosEquipo = []
        for data in ICPSudo.get_param('cobros.equipoTrabajo').split(','):
            if data:
                miembrosEquipo.append(self.env['res.users'].search([('id', '=', data)]).id)

        listNuevo = list(filter(lambda  x: x.categoria == 'Nuevo Ingreso' , self.estudiantesCobro_ids))
        listMaestria = list(filter(lambda  x: x.categoria == 'Maestria' , self.estudiantesCobro_ids))
        listRegular = list(filter(lambda  x: x.categoria == 'Regular' , self.estudiantesCobro_ids))
        listReingreso = list(filter(lambda  x: x.categoria == 'Reingreso' , self.estudiantesCobro_ids))
        listRegreso = list(filter(lambda  x: x.categoria == 'Regreso' , self.estudiantesCobro_ids))
        listCL = list(filter(lambda  x: x.categoria == 'Curso Libre' , self.estudiantesCobro_ids))


        listOrderNuevos = sorted(listNuevo, key=lambda x: x.totalLetra,reverse=True)

        index = 0
        while index <= (len(listOrderNuevos)-1):
            for data in miembrosEquipo:
                if index <= (len(listOrderNuevos)-1):
                    miembroAsignado = list(filter(lambda  x: (x.carnetEstudiante == listOrderNuevos[index].carnetEstudiante) and
                                                             (x.empleadoAsignadoInicial != None), self.estudiantesCobro_ids))
                    if miembroAsignado:
                        if not miembroAsignado[0].empleadoAsignadoInicial:
                            listOrderNuevos[index].empleadoAsignado = data
                            listOrderNuevos[index].empleadoAsignadoInicial = data
                            index += 1
                        else:
                            listOrderNuevos[index].empleadoAsignado = miembroAsignado[0].empleadoAsignadoInicial
                            listOrderNuevos[index].empleadoAsignadoInicial = miembroAsignado[0].empleadoAsignadoInicial
                            index += 1
                    else:
                        listOrderNuevos[index].empleadoAsignado = data
                        listOrderNuevos[index].empleadoAsignadoInicial = data
                        index += 1

        # index = 0
        # while index <= (len(listRegular)-1):
        #     for data in miembrosEquipo:
        #         if index <= (len(listRegular)-1):
        #             listRegular[index].empleadoAsignado = data
        #             listRegular[index].empleadoAsignadoInicial = data
        #             index += 1


        # for data in estudiantesList:
        #     for estudiante in data:
        #         estudianteLetra = self.env['cobros.periodo.pago.line'].search([('id', '=', estudiante.id)])
        #         if estudianteLetra:
        #             estudianteLetra.empleadoAsignado = miembrosEquipo[i]
        #             estudianteLetra.empleadoAsignadoInicial = miembrosEquipo[i]
        #     i+=1

    def _compue_team(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        empleadosList = []

        if ICPSudo.get_param('cobros.equipoTrabajo'):
            for data in ICPSudo.get_param('cobros.equipoTrabajo').split(','):
                if data:
                    user = self.env['res.users'].search([('id','=',data)])
                    empleadosList.append((str(user.id), (str(user.name))))

        res = empleadosList
        return res

    def set_ver_lista(self):
        if self.miembrosEquipo:
            letraList = self.env['cobros.periodo.pago.line'].sudo().search(['&',('periodoCobro_id','=',self.id),('empleadoAsignadoInicial', '=', int(self.miembrosEquipo))])

            for letra in letraList:
                letra.empleadoAsignado = self.env.user.id

            self.miembrosEquipo = False

    def set_dejar_ver_lista(self):
        if self.miembrosEquipo:
            letraList = self.env['cobros.periodo.pago.line'].sudo().search(['&',('periodoCobro_id','=',self.id),('empleadoAsignadoInicial', '=', int(self.miembrosEquipo))])

            for letra in letraList:
                letra.empleadoAsignado = int(self.miembrosEquipo)

            self.miembrosEquipo = False

    def ope_form_view_letra(self):
        if len(self.estudiantesSearch) == 1:
            letraID = self.estudiantesSearch.id
            self.estudiantesSearch = False
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'cobros.periodo.pago.line',
                'res_id': letraID,
                'target': 'new',
                'context': {
                    'form_view_initial_mode':  'edit',
                },
            }
        else:
            raise ValidationError('Solo')

    def generar_excel_asignacion(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/cobros/excel_asignacion_administrativo/%s' % (self.id),
            'target': 'new',
        }

    def generar_excel_reporte_estado_pago(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'cobros.reporte.estado.letras.wizard',
            'context': {
                'default_periodoPago_id': self.id,
            },
            'target': 'new',
        }

    @api.onchange('annoSelect')
    def onchangeAnno(self):
        self.anno = self.annoSelect

    @api.model
    def create(self, vals):
        vals['name'] = 'Periodo ' + str(self.env['periodo.cuatrimestre'].browse(vals['cuatrimestrePlanilla_id']).name) + ' Vencimiento de Letra ' + str(vals['fechaPago'])
        res = super(CoborosPeriodoPago, self).create(vals)
        return res


class CobrosPeriodoPagoLine(models.Model):
    _name="cobros.periodo.pago.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Estudiantes Atrasados"

    periodoCobro_id = fields.Many2one(
        comodel_name="cobros.periodo.pago",
        ondelete="cascade"
    )

    name = fields.Char(
        string="Busqueda",
        required=False,
    )
    envioNotificacion = fields.Boolean(
        string="Envio de Notificación",
        default=True
    )
    nombreEstudiante = fields.Char(
        string="Nombre",
        required=False,
    )
    carnetEstudiante = fields.Char(
        string="Carnet",
        required=False,
    )
    cedulaEstudiante = fields.Char(
        string="Cédula",
        required=False,
    )
    correoEstudiante = fields.Char(
        string="Correo",
        required=False,
    )
    correoInstitucionalEstudiante = fields.Char(
        string="Correo Institucional",
        required=False,
    )
    telefonoPrimarioEstudiante = fields.Char(
        string="Telefono #1",
        required=False,
    )
    telefonoSecundarioEstudiante = fields.Char(
        string="Telefono #2",
        required=False,
    )
    telefonoPrimarioTrabajoEstudiante = fields.Char(
        string="Telefono Laboral #1",
        required=False,
    )
    telefonoSecundarioTrabajoEstudiante = fields.Char(
        string="Telefono Laboral #2",
        required=False,
    )
    numeroLetra = fields.Char(
        string="Numero de Letra",
        required=False,
    )
    montoPagar = fields.Float(
        string="Monto a Pagar",
        required=False,
        digits=(16,2),
    )
    montoPagado = fields.Float(
        string="Monto Pagado",
        required=False,
        digits=(16,2),
    )
    montoDiferencia = fields.Float(
        string="Diferencia",
        required=False,
        digits=(16,2),
    )
    porcientoPago = fields.Float(
        string="Porcentaje de Pago",
        required=False,
        digits=(16,2),
    )
    totalLetra = fields.Float(
        string="Total de Letra",
        required=False,
    )
    empleadoAsignado = fields.Many2one(
        comodel_name="res.users",
        string="Empleado Asignado",
        required=False,
    )
    empleadoAsignado = fields.Many2one(
        comodel_name="res.users",
        string="Empleado Asignado",
        required=False,
    )
    empleadoAsignadoInicial = fields.Many2one(
        comodel_name="res.users",
        string="Empleado Asignado Inicial",
        required=False,
    )
    inicioIntereses = fields.Date(
        string="Inicio Intereses",
        required=False,
    )
    categoria = fields.Char(
        string="Categoria",
        required=False,
    )
    estado = fields.Selection(
        string="Estado de Letra",
        selection=[
            ('LETRA VENCIDA', 'LETRA VENCIDA'),
            ('AL DIA', 'AL DIA'),
            ('AL DIA SALDO MENOR', 'AL DIA SALDO MENOR'),
        ],
        required=False,
    )
    estadoPago = fields.Selection(
        string="Estado de Pago",
        selection=[
            ('ARREGLO DE PAGO', 'ARREGLO DE PAGO'),
            ('CONAPE', 'CONAPE'),
            ('CONTACTADO SIN ARREGLO', 'CONTACTADO SIN ARREGLO'),
            ('INCUMPLIMIENTO DE ARREGLO DE PAGO', 'INCUMPLIMIENTO DE ARREGLO DE PAGO'),
            ('NO CONTESTA', 'NO CONTESTA'),
            ('NO VA A PAGAR', 'NO VA A PAGAR'),
            ('SIN STATUS', 'SIN STATUS'),
            ('TRAMITES INTERNOS PENDIENTES', 'TRAMITES INTERNOS PENDIENTES'),
        ],
        required=False,
    )
    fechaFinArreglo = fields.Date(
        string="Fecha Fin de Arreglo",
        required=False,
    )
    justificacion = fields.Char(
        string="Justificación",
        required=False,
    )

    estudianteBloqueado = fields.Boolean(
        string="Estudiante Bloqueado",
        default= False,
    )







