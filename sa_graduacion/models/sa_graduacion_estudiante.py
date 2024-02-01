# -*- coding:utf-8 -*-
import base64
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError
from odoo import api, fields, models, _


class PeriodoGraduacion(models.Model):
    _name = "sa.graduacion.estudiante"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description= "Graduación del estudiante"


    periodoGraduacion_id = fields.Many2one(
        string='Periodo de graduación',
        tracking=True,
        required=True,
        comodel_name='sa.periodo.graduacion',
    )

    name = fields.Char(
        string="Nombre",
        required=True,
        tracking=True,
    )

    identificacion = fields.Char(
        string="Identificación",
        required=True,
        tracking=True,
    )

    carnet = fields.Char(
        string="Carnet",
        required=True,
        tracking=True,
    )

    correo = fields.Char(
        string="Correo",
        required=True,
        tracking=True,
    )

    telefono = fields.Char(
        string="Teléfono",
        required=True,
        tracking=True,
    )

    carrera = fields.Char(
        string="Carrera",
        required=True,
        tracking=True,
    )

    grado = fields.Selection(
        string="Grado",
        selection=[
            ('BACHILLERATO', 'BACHILLERATO'),
            ('LICENCIATURA', 'LICENCIATURA'),
            ('MAESTRIA', 'MAESTRIA'),
        ],
        required=False,
    )

    estado_Migratorio = fields.Selection(
        string="Estado Mifgratorio",
        selection=[
            ('Nacional', 'Nacional'),
            ('Extranjero', 'Extranjero'),
        ],
        required=False,
    )

    state = fields.Selection(
        string="Estado",
        selection=[
            ('Recibido', 'Recibido'),
            ('En revisión', 'En revisión'),
            ('Aprobado', 'Aprobado'),
            ('Rechazado', 'Rechazado'),
        ],
        required=False,
        tracking=True,
        default="Recibido",
    )

    observaciones = fields.Text(
        string="Observaciones",
        required=False,
        tracking=True,
    )

    fecha_Solicitud = fields.Date(
        string="Fecha de solicitud",
        required=False,
        tracking=True,
    )

    fecha_Vencimiento = fields.Date(
        string="Fecha de vencimiento",
        required=False,
        tracking=True,
    )

    #region Documentos
    copia_Identificacion = fields.Binary(
        string='Identificación vigente',
        required=False,
    )

    copia_Titulo_Educacion = fields.Binary(
        string='Título Educación Media',
        required=False,
    )

    copia_Diploma = fields.Binary(
        string='Copia del diploma',
        required=False,
    )

    copia_Apostille = fields.Binary(
        string='Apostille del diploma ',
        required=False,
    )

    copia_Equiparacion_MEP = fields.Binary(
        string='Equiparación del MEP',
        required=False,
    )

    copia_Titulo_Bachillerato = fields.Binary(
        string='Título Universitario Bachillerato',
        required=False,
    )

    copia_Titulo_Bachillerato_Licenciatura = fields.Binary(
        string='Títulos Universitarios Bachillerato Licenciatura',
        required=False,
    )

    copia_TCU_Certificacion = fields.Binary(
        string='Recibido TCU completo o certificación',
        required=False,
    )

    copia_comprobande = fields.Binary(
        string='Comprobante de pago',
        required=False,
    )

    copia_Boleta = fields.Binary(
        string='Boleta firmada',
        required=False,
    )

    #endregion

    #region Filename

    filename_Identificacion = fields.Char(
        default='Identificación vigente',
        required=False,
    )

    filename_Titulo_Educacion = fields.Char(
        default='Título Educación Media',
        required=False,
    )

    filename_Diploma = fields.Char(
        default='Copia del diploma',
        required=False,
    )

    filename_Apostille = fields.Char(
        default='Apostille del diploma ',
        required=False,
    )

    filename_Equiparacion_MEP = fields.Char(
        default='Equiparación del MEP',
        required=False,
    )

    filename_Titulo_Bachillerato = fields.Char(
        default='Título Universitario Bachillerato',
        required=False,
    )

    filename_Titulo_Bachillerato_Licenciatura = fields.Char(
        default='Títulos Universitarios Bachillerato Licenciatura',
        required=False,
    )

    filename_TCU_Certificacion = fields.Char(
        default='Recibido TCU completo o certificación',
        required=False,
    )

    filename_comprobande = fields.Char(
        default='Comprobante de pago',
        required=False,
    )

    filename_Boleta = fields.Char(
        default='Boleta firmada',
        required=False,
    )
    #endregion



    def envio_Correo_Recibido(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        datosCorreo = {
            'nombre': self.name,
            'state': self.state,
            'observaciones': "",
        }
        template_id = self.env.ref('sa_graduacion.email_proceso_graduacion_Recibido').id
        template = self.env['mail.template'].browse(template_id)
        email_values = {'email_to': self.correo,
                        'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                        'email_cc': 'graduacion@uia.ac.cr',
                        'subject': 'Estatus de proceso de graduación',
                        }
        template.with_context(datosCorreo=datosCorreo).send_mail( self._origin.id, email_values=email_values, force_send=True)

    def envio_Correo_Revision(self):
        self.state = "En revisión"
        ICPSudo = self.env['ir.config_parameter'].sudo()
        datosCorreo = {
            'nombre': self.name,
            'state': self.state,
            'observaciones': "",
        }
        template_id = self.env.ref('sa_graduacion.email_proceso_graduacion_Recibido').id
        template = self.env['mail.template'].browse(template_id)
        email_values = {'email_to': self.correo,
                        'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                        'email_cc': 'graduacion@uia.ac.cr',
                        'subject': 'Estatus de proceso de graduación',
                        }
        template.with_context(datosCorreo=datosCorreo).send_mail( self._origin.id, email_values=email_values, force_send=True)

    def envio_Correo_Aprobado(self):
        self.state = "Aprobado"
        ICPSudo = self.env['ir.config_parameter'].sudo()

        report_template_id = self.env.ref('sa_graduacion.report_boleta_gradaucion').sudo()._render_qweb_pdf(self.id)
        data_record = base64.b64encode(report_template_id[0])
        ir_values = {
            'name': "Boleta de solicitud de graduación.pdf",
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/x-pdf',
        }
        datosCorreo = {
            'nombre': self.name,
            'state': self.state,
            'observaciones': "",
        }
        data_id = self.env['ir.attachment'].create(ir_values)
        template_id = self.env.ref('sa_graduacion.email_proceso_graduacion_Aceptacion').id
        template = self.env['mail.template'].browse(template_id)
        template.attachment_ids = [(6, 0, [data_id.id])]
        email_values = {'email_to': self.correo,
                        'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                        'email_cc': 'graduacion@uia.ac.cr',
                        'subject': 'Estatus de proceso de graduación',
                        }
        template.with_context(datosCorreo=datosCorreo).send_mail( self._origin.id, email_values=email_values, force_send=True)
        template.attachment_ids = [(3, data_id.id)]

    def envio_Correo_Rechazado(self):
        self.state = "Rechazado"
        ICPSudo = self.env['ir.config_parameter'].sudo()
        datosCorreo = {
            'nombre': self.name,
            'state': self.state,
            'observaciones': self.observaciones.split('\n') if self.observaciones else "",
        }
        template_id = self.env.ref('sa_graduacion.email_proceso_graduacion_Rechazado').id
        template = self.env['mail.template'].browse(template_id)
        email_values = {'email_to': self.correo,
                        'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                        'email_cc': 'graduacion@uia.ac.cr',
                        'subject': 'Estatus de proceso de graduación',
                        }
        template.with_context(datosCorreo=datosCorreo).send_mail( self._origin.id, email_values=email_values, force_send=True)

    def descargar_boelta(self):
        return self.env.ref('sa_graduacion.report_boleta_gradaucion').sudo().report_action(self.id)


