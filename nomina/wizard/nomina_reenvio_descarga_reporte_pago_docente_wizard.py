from datetime import *
from odoo.http import request
import requests
import math
import pytz
import json
import base64
import pytz
import requests
from odoo import api, fields, models, _


class NominReenvioDescargaReportePagoDocenteWizard(models.TransientModel):
    _name = "nomina.reenvio.descarga.reporte.pago.docente.wizard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Reenvio y Descarga de Reporte de pago"

    planillaCuatrimestre_id = fields.Many2one(
        comodel_name="planilla.cuatrimestre",
        string="Cuatrimestre",
        required=True,
        tracking=False,
    )

    docente_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Docente",
        required=True,
        tracking=False,
    )

    def reenviar_reporte(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        lineaPlanilla = self.env['planilla.cuatrimestre.line'].search(['&',('docentesLinea_id','=',self.planillaCuatrimestre_id.id),('docente_id','=',self.docente_id.id)])
        datas = {
            'lineaPlanilla': lineaPlanilla,
            'planillaPago': self.planillaCuatrimestre_id,
        }
        report_template_id = self.env.ref('nomina.report_detalles_pago_docente')._render_qweb_pdf(self, data=datas)
        data_record = base64.b64encode(report_template_id[0])
        ir_values = {
            'name': "Pre Planilla " + lineaPlanilla.nombreDocente + ".pdf",
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/x-pdf',
        }
        datosCorreo = {
            'docenteNombre': lineaPlanilla.nombreDocente,
            'fechaInicioPago': str( self.planillaCuatrimestre_id.fechaInicioPago),
            'fechaFinalPago':  self.planillaCuatrimestre_id.fechaFinalPago,
        }
        data_id = self.env['ir.attachment'].create(ir_values)
        template_id = self.env.ref('nomina.email_docente_preplanilla').id
        template = self.env['mail.template'].browse(template_id)
        template.attachment_ids = [(6, 0, [data_id.id])]
        email_values = {'email_to': lineaPlanilla.correoDocente,
                        'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                        'subject': lineaPlanilla.nombreDocente + ' Pre Planilla del: ' + str( self.planillaCuatrimestre_id.fechaInicioPago) + " a " + str(
                            self.planillaCuatrimestre_id.fechaFinalPago)
                        }
        template.with_context(datosCorreo=datosCorreo).send_mail( self.planillaCuatrimestre_id.id, email_values=email_values, force_send=True)
        template.attachment_ids = [(3, data_id.id)]

    def descargar_reporte(self):
        lineaPlanilla = self.env['planilla.cuatrimestre.line'].search(['&', ('docentesLinea_id', '=', self.planillaCuatrimestre_id.id), ('docente_id', '=', self.docente_id.id)])
        datas = {
            'lineaPlanilla': lineaPlanilla,
            'planillaPago': self.planillaCuatrimestre_id,
            'planillaPagoid': self.planillaCuatrimestre_id.id,
            'lineaPlanillaid': lineaPlanilla.id,
        }
        return  self.env.ref('nomina.report_detalles_pago_docente').report_action(self, data=datas)