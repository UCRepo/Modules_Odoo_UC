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

class NominaCargarAdicionalesWizard(models.TransientModel):
    _name = "nomina.cargar.adicionales.wizard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Generar Asistencia"

    documento_Adicionales = fields.Binary(
        string='Adicionales'
    )

    def cargar_adicionales(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(self.documento_Adicionales)),read_only=True)

        ws = wb.active

        docentesNoEncontradosList = []
        for record in ws.iter_rows(min_row=2, max_row=None, min_col=None,max_col=None, values_only=True):

            docentes = request.env['hr.employee'].sudo().search([('department_id.name', '=', 'Docentes')])
            docente = any
            for data in docentes:
                if data.identification_id != False:
                    cedDocente = data.identification_id.replace("-", "")
                    if cedDocente == str(record[0]).replace("-",""):
                        docente = data

            if docente == any:
                dict = {
                    'cedula':str(record[0]),
                    'tipo':str(record[1]),
                    'cantidad':str(record[2]),
                    'anno':str(record[3]),
                    'periodo':str(record[4]),
                    'fecha':str(record[5]),
                    'nombreDocente': '',
                    'motivo': 'No Se Encontro al Docente',
                }

                noDocente = list(filter(lambda x: (x['cedula'] == dict['cedula']) and
                                                (x['tipo']== dict['tipo']) and
                                                (x['cantidad'] == dict['cantidad']) and
                                                (x['anno']== dict['anno']) and
                                                (x['periodo'] == dict['periodo']) and
                                                (x['fecha']== dict['fecha']) and
                                                (x['motivo'] == dict['motivo']),docentesNoEncontradosList))
                if len(noDocente) ==  0:
                    docentesNoEncontradosList.append(dict)

                continue

            cuatrimestre = self.env['periodo.cuatrimestre'].search(['&', ('year', '=', str(record[3])), ('decripcion', '=', str(record[4]) + "Q")])

            cursosDocente = self.env['cursos.docente'].search(['&', ('docente_id', '=', docente.id), ('cuatrimestre_id', '=', cuatrimestre.id)])

            adicional = self.env['configuraciones.adicionales.line'].search([('name', '=', record[1])])

            if not adicional:
                dict = {
                    'cedula':str(record[0]),
                    'tipo':str(record[1]),
                    'cantidad':str(record[2]),
                    'anno':str(record[3]),
                    'periodo':str(record[4]),
                    'fecha':str(record[5]),
                    'nombreDocente': docente.name,
                    'motivo': 'No Se Encontro el Tipo de Adicional',
                }

                noDocente = list(filter(lambda x: (x['cedula'] == dict['cedula']) and
                                                (x['tipo']== dict['tipo']) and
                                                (x['cantidad'] == dict['cantidad']) and
                                                (x['anno']== dict['anno']) and
                                                (x['periodo'] == dict['periodo']) and
                                                (x['fecha']== dict['fecha']) and
                                                (x['motivo'] == dict['motivo']),docentesNoEncontradosList))
                if len(noDocente) ==  0:
                    docentesNoEncontradosList.append(dict)

                continue

            vals = {'adicionalId': adicional.id,
                    'name': record[1],
                    'sinPrestaciones': adicional.montoSinPrestaciones,
                    'cantidad': int(float(record[2])),
                    'totalAdicionales': adicional.montoSinPrestaciones * int(float(record[2])),
                    'cuatrimestre_id': cursosDocente.cuatrimestre_id.id,
                    'docente_id': cursosDocente.docente_id.id,
                    'pagoEfectuado': False,
                    'fechaAdicional': record[5]
                    }

            miembros =  cursosDocente.adicionales_lines_ids
            adicionalesDocente = list(filter(lambda x: (x.docente_id.id == vals['docente_id']) and
                                                        (x.cuatrimestre_id.id == vals['cuatrimestre_id']) and
                                                        (x.name == record[1]) and
                                                        (x.cantidad == int(float(record[2]))) and
                                                        (x.fechaAdicional == record[5]) and
                                                        (x.adicionales_id.id == cursosDocente.id ), miembros))
            if adicionalesDocente:
                cursosDocente.adicionales_lines_ids = [(1, adicionalesDocente[0].id, vals)]
            else:
                cursosDocente.adicionales_lines_ids = [(0, 0, vals)]

        if len(docentesNoEncontradosList) > 0:
            template_id = self.env.ref('nomina.email_adicionales_docente_no_encontrado').id
            template = self.env['mail.template'].browse(template_id)
            email_values = {
                            'email_to': self.env.user.email,
                            'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                            'subject': 'Reporte de Adicionales no Aplicados'
                            }
            template.with_context(datosCorreo=docentesNoEncontradosList).send_mail(self.id, email_values=email_values, force_send=True)