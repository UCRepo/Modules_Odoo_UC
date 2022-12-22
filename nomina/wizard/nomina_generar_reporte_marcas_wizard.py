from datetime import *
from odoo.http import request
import requests
import math
import pytz
import json
import logging
from odoo import api, fields, models, _



class NominaGenerarAsistenciaDocenteWizard(models.TransientModel):
    _name = "nomina.generar.reporte.marcas.wizard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Generar Reporte Marcas"

    planilla_line_ids = fields.Many2one(
        comodel_name="planilla.cuatrimestre",
        string="Cuatrimestre",
        required=True,
        tracking=False,
    )
    docente_ids = fields.Many2one(
        comodel_name="hr.employee",
        string="Docente Especifico",
        readonly=False
    )

    def descargar_reporte_asistencia(self):

        datas = {
            'planilla_line_ids': self.planilla_line_ids.id,
            'docente_ids': self.docente_ids.id,
        }
        return  self.env.ref('nomina.report_asistencia_docente').report_action(self, data=datas)