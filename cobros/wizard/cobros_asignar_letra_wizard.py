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

class NominaCargarAjustePagoDocenteWizard(models.TransientModel):
    _name = "cobros.asignar.letras.wizard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Asignar Letras a Miembros del equipo"

    documentoLetrasCambio= fields.Binary(
        string='Letras de Cambio'
    )
    periodoPago_id = fields.Many2one(
        string='Periodo de Pago',
        tracking=True,
        required=True,
        comodel_name='cobros.periodo.pago',
    )

    def asignar_letras_miembros(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(self.documentoLetrasCambio)),read_only=True)

        ws = wb.active
        usuarios = request.env['res.users'].sudo().search([])
        letras = self.env['cobros.periodo.pago.line'].sudo().search([('periodoCobro_id', '=', self.periodoPago_id.id)])

        docentesNoEncontradosList = []
        for record in ws.iter_rows(min_row=2, max_row=None, min_col=None,max_col=None, values_only=True):

            usuario = list(filter(lambda x: (x.login == str(record[4])),usuarios))

            letra = list(filter(lambda x: (x.numeroLetra == str(record[2])),letras))

            if len(letra)  == 1:
                letra[0].empleadoAsignadoInicial = usuario[0].id
                letra[0].empleadoAsignado = usuario[0].id





