# -*- coding: utf-8 -*-
from datetime import date, timedelta, datetime,timezone,time
from odoo.http import request
import requests
import math
import pytz
import json
from odoo import api, fields, models, _

class PolizaDashboard(models.Model):
    _name = "poliza.dashboard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Poliza Dashboard"

    totalPolizas = fields.Integer(
        string="Total de Pólizas",
        required=False,
    )
    totalPolizasActualizadas = fields.Integer(
        string="Pólizas Completadas",
        required=False,
    )

    anno = fields.Selection(
        string="Año",
        tracking=True,
        selection='_get_years',
        required=True,
    )
    annoDescripcion = fields.Char(
        string="Año",
        required=False,
    )

    periodo = fields.Selection(
        string="Periodo",
        tracking=True,
        selection=[
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
        ],
        required=True,
    )

    progresoPoliza = fields.Float(
        string="Progreso",
        required=False,
        compute='_get_datos_poliza',
    )

    name = fields.Char(
        string="Nombre",
        required=False,
    )

    estudiantes_poliza_lines_ids = fields.One2many(
        comodel_name="poliza.informacion.line",
        inverse_name="poliza_id",
        string="Estudiantes",
        required=False,
    )

    def _get_years(self):
        """
             Funcion para optener 4 años siguientes apartir del actual
        :return:
            :: Genera 4 años sumando al años actual
        """
        lsi = []
        anno = datetime.today()
        sumYear = int(anno.year)
        for a in range(5):
            lsi.append((str(sumYear + a), _(str(sumYear + a))))
        return lsi

    def _get_datos_poliza(self):
        for data in self:
            ICPSudo = self.env['ir.config_parameter'].sudo()
            url = ICPSudo.get_param('uia_poliza.UrlAPI')+'/api/PolizaUC/getEstadoPoliza'

            if data.anno != False and data.periodo != False:
                dataJSon = {
                    "year": int(data.anno),
                    "periodo": int(data.periodo),
                    "cedulaEstudiante": "string",
                    "cedulaBeneficiario": "string",
                    "nombreBeneficiario": "string",
                    "parentescoBeneficiario": "string",
                    "numeroTelefonoBeneficiario": "string",
                    "correoBeneficiario": "string",
                    "tipoIdentificacionBeneficiario": "string"
                }
                header = {
                    'Content-Type': 'application/json',
                    'Accept': 'text/plain'
                }
                response = requests.post(url, headers=header, json=dataJSon, verify=False)
                if response.status_code == 200:
                    data.totalPolizas = response.json()['data']['totalPolizas']
                    data.totalPolizasActualizadas = response.json()['data']['totalPolizasActualizadas']
                    if response.json()['data']['totalPolizas'] != 0:
                        data.progresoPoliza =  (response.json()['data']['totalPolizasActualizadas']*100) / response.json()['data']['totalPolizas']
                    else:
                        data.progresoPoliza = 0

    def get_estudiantes_poliza(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('uia_poliza.UrlAPI')+'/api/PolizaUC/getDatosPoliza'

        dataJSon = {
            "year": int(self.anno),
            "periodo": int(self.periodo),
            "cedulaEstudiante": "string",
            "cedulaBeneficiario": "string",
            "nombreBeneficiario": "string",
            "parentescoBeneficiario": "string",
            "numeroTelefonoBeneficiario": "string",
            "correoBeneficiario": "string",
            "tipoIdentificacionBeneficiario": "string"
        }
        header = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain'
        }
        response = requests.post(url, headers=header, json=dataJSon, verify=False)

        if response.status_code == 200:
            for data in response.json()['data']:
                vals = {
                    'nombre': data['nombre'],
                    'estudianteID': data['estudianteid'],
                    'fechaNacimiento': data['annoNacimiento'],
                    'genero': data['genero'],
                    'paisNacimiento': data['paisNacimiento'],
                    'identificacion': data['identificacion'],
                    'telefono': data['telefono'],
                    'correo': data['email'],
                    'direccion': data['direccion'],
                    'datosActualizados': data['datosActualizados'],
                }
                if data['datosActualizados'] == True:
                    vals.update({
                        'beneficiarioIdentificacion': data['beneficiarioId'],
                        'beneficiarioNombre' : data['beneficiarioNombre'],
                        'beneficiarioParentesco': data['beneficiarioparentesco'],
                        'beneficiarioTelefonoPrimario': data['beneficiariotelefonoPrimario'],
                        'beneficiarioEmail': data['beneficiarioemail'],
                    })
                estudiantePoliza = list(filter(lambda x: (x.estudianteID == vals['estudianteID']) , self.estudiantes_poliza_lines_ids))

                if estudiantePoliza:
                    if estudiantePoliza[0].datosActualizados != vals['datosActualizados']:
                        self.estudiantes_poliza_lines_ids = [(1, estudiantePoliza[0].id, vals)]
                else:
                    self.estudiantes_poliza_lines_ids = [(0, 0, vals)]

    def createXLSXReport(self):
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'poliza.generar.reporte.beneficiarios.wizard',
            'target': 'new',
        }

    def createXLSXReportGeneral(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/poliza/excel_report_general/%s' % (self.id),
            'target': 'new',
        }

    def send_correo_notificacion(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        template_id = self.env.ref('uia_poliza.email_correo_poliza_estudiante').id
        template = self.env['mail.template'].browse(template_id)

        for data in self.estudiantes_poliza_lines_ids:
            if data.correo != False and data.datosActualizados != True or not data.correo:
                datosCorreo = {
                    'nombreEstudiante': data.nombre,
                    'link': ICPSudo.get_param('web.base.url')+"/formBeneficiarioPoliza?idPoliza="+str(self.id)+'&idEstudiante='+data.identificacion,
                }
                email_values = {'email_to': data.correo,
                                'email_from': ICPSudo.get_param('uia_poliza.correoEnvioNotificacionesPoliza'),
                                'subject': 'Información de Beneficiario de póliza'
                                }
                template.with_context(datosCorreo=datosCorreo).send_mail(self.id, email_values=email_values,force_send=True)

    @api.model
    def create(self,vals):
        """
            Metodos para crear un registro
        :param vals: valroes que se optiens del form
        :return:
        """
        vals['name'] = str(vals['periodo']) + 'Q ' + str(vals['anno'])
        vals['annoDescripcion'] = str(vals['anno'])
        res = super(PolizaDashboard, self).create(vals)
        return res

class PolizaInformacionLine(models.Model):
    _name = "poliza.informacion.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Poliza Informacion Line"

    poliza_id = fields.Many2one(
        comodel_name="poliza.dashboard",
        ondelete="cascade"
    )
    nombre = fields.Char(
        string="Nombre",
        required=False,
    )
    estudianteID = fields.Char(
        string="estudianteID",
        required=False,
    )
    fechaNacimiento = fields.Date(
        string="Fecha Nacimiento",
        required=False,
    )
    genero = fields.Char(
        string="Género",
        required=False,
    )
    paisNacimiento = fields.Char(
        string="Pais de Nacimiento",
        required=False,
    )
    identificacion = fields.Char(
        string="Identificación",
        required=False,
    )
    telefono = fields.Char(
        string="Teléfono",
        required=False,
    )
    correo = fields.Char(
        string="Correo",
        required=False,
    )
    direccion = fields.Char(
        string="Dirección",
        required=False,
    )
    datosActualizados = fields.Boolean(
        string="Datos Actualizados",
        default=False
    )
    beneficiarioIdentificacion = fields.Char(
        string="Identificación de Beneficiario",
        required=False,
    )
    beneficiarioNombre = fields.Char(
        string="Nombre de Beneficiario",
        required=False,
    )
    beneficiarioParentesco = fields.Char(
        string="Parentesco de Beneficiario",
        required=False,
    )
    beneficiarioTelefonoPrimario = fields.Char(
        string="Telefono de Beneficiario",
        required=False,
    )
    beneficiarioEmail = fields.Char(
        string="Correo de Beneficiario",
        required=False,
    )
    fechaActualizacion = fields.Date(
        string="Fecha Actualización",
        required=False,
    )


