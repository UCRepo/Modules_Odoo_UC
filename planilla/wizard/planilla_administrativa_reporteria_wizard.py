# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date, timedelta, datetime
import calendar
import os

class PlanillaAdministrativaReporteria(models.Model):
    _name = "planialla.administrativa.reporteria.wizard"
    _inherit = 'mail.thread'

    tipoReporte = fields.Selection(
        string="Tipo de reporte",
        selection=[
            ('01', '01'),
            ('02', '02'),
        ],
        required=False,
    )
    desde = fields.Date(
        string="Desde",
        required=False,
    )
    hasta = fields.Date(
        string="Hasta",
        required=False,
    )
    def generar_xls_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/planillaAdministrativa/asistencia_general/excel_report?desde='+str(self.desde)+'&hasta='+str(self.hasta),
            'target': 'new',
        }


