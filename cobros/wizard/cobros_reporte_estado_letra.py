import base64
from datetime import *
from odoo.http import request
import openpyxl
import requests
import math
import pytz
import json
from io import BytesIO
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class CobrosReporteXEstadoLetraWizard(models.TransientModel):
    _name = "cobros.reporte.estado.letras.wizard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Reporte por estado de letra"


    tipoEstadoPago = fields.Selection(
        string="Tipo Estado de Pago",
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

    periodoPago_id = fields.Many2one(
        string='Periodo de Pago',
        tracking=True,
        required=True,
        comodel_name='cobros.periodo.pago',
    )


    def generar_excel_reporte_estado_pago(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/cobros/excel_reporte_estado_pago/%s' % (self.id),
            'target': 'new',
        }