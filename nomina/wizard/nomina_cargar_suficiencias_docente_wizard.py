# -*- coding: utf-8 -*-
import pytz
import requests
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime
from odoo.addons.base.models.res_partner import _tz_get

class CargarSuficienciaDocente(models.TransientModel):
    _name = 'nomina.cargar.suficiencias.docente.wizard'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Suficiencias de Docentes"

    cuatrimestre_id = fields.Many2one(
        string='Cuatrimestre',
        tracking=True,
        required=True,
        comodel_name='periodo.cuatrimestre',
    )
    fechaPago = fields.Date(
        string="Fecha de pago",
        required=False,
    )

    def cargar_suficiencias(self):
        res = any
        cantiadadHoras = any
        cantiadadHorasSemana = any
        planillaActual = any
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('nomina.urlWSOdoo')+'/api/CursosDocenteUC/getSuficienciaDocente'
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)
        vals = {}

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
                cursosDocente =  self.env['cursos.docente'].search([('cuatrimestre_id','=',self.cuatrimestre_id.id)])
                for data in response.json()['data']:
                    docente =  list(filter(lambda x: (str(x.docente_id.identification_id).replace("-", "") == data['docente'].replace("-", "") ),cursosDocente))
                    if docente:
                        adicional = self.env['configuraciones.adicionales.line'].search([('name', '=', 'Examen de Suficiencia')])
                        if docente[0].docente_id.id == 6945:
                            print('ds')
                        vals = {'adicionalId': adicional.id,
                                'name': adicional.name,
                                'sinPrestaciones': adicional.montoSinPrestaciones,
                                'cantidad': int(float(data['cantidad'])),
                                'totalAdicionales': adicional.montoSinPrestaciones * int(float(data['cantidad'])),
                                'cuatrimestre_id': self.cuatrimestre_id.id,
                                'docente_id': docente[0].docente_id.id,
                                'pagoEfectuado': False,
                                'fechaAdicional':  self.fechaPago
                                }

                        miembros = cursosDocente.adicionales_lines_ids
                        adicionalesDocente = list(filter(lambda x: (x.docente_id.id == vals['docente_id']) and
                                                                   (x.cuatrimestre_id.id == vals['cuatrimestre_id']) and
                                                                   (x.name == adicional.name) and
                                                                   (x.cantidad == int(float(data['cantidad']))) and
                                                                   (x.fechaAdicional == self.fechaPago) and
                                                                   (x.adicionales_id.id == docente[0].id), miembros))
                        if adicionalesDocente:
                            cursosDocente.adicionales_lines_ids = [(1, adicionalesDocente[0].id, vals)]
                        else:
                            cursosDocente.adicionales_lines_ids = [(0, 0, vals)]
