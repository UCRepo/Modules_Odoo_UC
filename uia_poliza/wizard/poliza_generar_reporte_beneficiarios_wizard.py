from datetime import date, timedelta, datetime,timezone,time
from odoo.http import request
import requests
import math
import pytz
import json
from odoo import api, fields, models, _

class NominaPolizaGenerarReporteBeneficiariosWizard(models.TransientModel):
    _name = "poliza.generar.reporte.beneficiarios.wizard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Póliza Generar Reporte Beneficiarios"

    polizaDesde = fields.Date(
        string="Desde",
        required=False,
    )

    polizaHasta = fields.Date(
        string="Hasta",
        required=False,
    )
    poliza = fields.Many2one(
        comodel_name="poliza.dashboard",
        string="Póliza",
        readonly=False
    )

    def generar_poliza_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/poliza/excel_report/%s' % (self.id),
            'target': 'new',
        }