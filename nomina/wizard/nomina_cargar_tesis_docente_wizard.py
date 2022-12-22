from datetime import *
from odoo.http import request
import requests
import math
import pytz
import json
from odoo import api, fields, models, _


class NominCargarTesisDocenteWizard(models.TransientModel):
    _name = "nomina.cargar.tesis.docente.wizard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Generar Asistencia"

    cuatrimestre_id = fields.Many2one(
        comodel_name="periodo.cuatrimestre",
        string="Cuatrimestre",
        required=True,
        tracking=False,
    )

    def cargar_tesis(self):
        res = any
        cantiadadHoras = any
        cantiadadHorasSemana = any
        planillaActual = any
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = 'https://localhost:44305/api/CursosDocente/getTesisDocente'
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)
        vals = {}

        cuatrimestre = self.env['periodo.cuatrimestre'].search(['&', ('year', '=', self.cuatrimestre_id.year), ('decripcion', '=', self.cuatrimestre_id.decripcion)])

        if self.cuatrimestre_id:
            dataJSon = {
                'Anno': self.cuatrimestre_id.year,
                'Periodo': self.cuatrimestre_id.decripcion.replace('Q', ''),
            }
            header = {
                'Content-Type': 'application/json',
                'Accept': 'text/plain'
            }
            response = requests.post(url, headers=header, json=dataJSon, verify=False)

            if response.status_code == 200:
                for data in response.json()['data']:
                    vals = {}
                    vals.update({
                        'cuatrimestre_id': self.cuatrimestre_id.id,
                        'estudiante': data['estudiante'],
                        'tema': data['temaTesis'],
                        'carrera': data['carrera'],
                    })
                    director = []
                    tutor = []
                    lector = []

                    docentes = request.env['hr.employee'].sudo().search([('department_id.name', '=', 'Docentes')])

                    director = list(filter(lambda x: str(x.identification_id).replace("-", "") == str(data['director']).replace("-", ""), docentes))
                    tutor = list(filter(lambda x: str(x.identification_id).replace("-", "") == str(data['tutor']).replace("-", ""), docentes))
                    lector = list(filter(lambda x: str(x.identification_id).replace("-", "") == str(data['lector']).replace("-", ""), docentes))
                    if len(director) > 0:
                        vals.update({
                            'director': director[0].id,
                        })
                    if len(tutor) > 0:
                        vals.update({
                            'tutor': tutor[0].id,
                        })
                    if len(lector) > 0:
                        vals.update({
                            'lector': lector[0].id,
                        })

                    res = self.env['tesis.docente'].sudo().create(vals)