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
    _name = "nomina.cargar.ajuste.pago.docente.wizard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Cargar Ajuste Pago Docente"

    documentoAjustePago= fields.Binary(
        string='Ajustes de Pago'
    )
    tipo = fields.Selection(
        string="",
        selection=[
            ('Monto Fijo', 'Monto Fijo'),
            ('Por Horas', 'Por Horas'),
        ],
        required=True,
    )

    def cargar_ajuste_pago_docente(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(self.documentoAjustePago)),read_only=True)

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
                    'monto':str(record[2]),
                    'fecha':str(record[3]),
                    'anoo':str(record[4]),
                    'periodo':str(record[5]),
                    'nombreDocente': '',
                    'motivo': 'No Se Encontro al Docente',
                }

                noDocente = list(filter(lambda x: (x['cedula'] == dict['cedula']) and
                                                (x['tipo']== dict['tipo']) and
                                                (x['monto'] == dict['monto']) and
                                                (x['fecha']== dict['fecha']) and
                                                (x['anoo'] == dict['anoo']) and
                                                (x['periodo']== dict['periodo']) and
                                                (x['motivo'] == dict['motivo']),docentesNoEncontradosList))
                if len(noDocente) ==  0:
                    docentesNoEncontradosList.append(dict)

                continue

            cuatrimestre = self.env['periodo.cuatrimestre'].search(['&', ('year', '=', str(record[4])), ('decripcion', '=', str(record[5]) + "Q")])

            cursosDocente = self.env['cursos.docente'].search(['&', ('docente_id', '=', docente.id), ('cuatrimestre_id', '=', cuatrimestre.id)])

            correoAutoriza = ''
            if str(record[6]) == '':
                correoAutoriza = self.env.user.email
            else:
                correoAutoriza = str(record[6])

            autoriza = self.env['hr.employee'].search(['&',('work_email','=',correoAutoriza),('department_id.name', '!=', 'Docentes'),('department_id.name', '!=', 'Inactivos')])

            ajuste = self.env['configuraciones.ajuste.pago.line'].search([('name','=',str(record[1]))])

            if not ajuste:
                dict = {
                    'cedula':str(record[0]),
                    'tipo':str(record[1]),
                    'monto':str(record[2]),
                    'fecha':str(record[3]),
                    'anoo':str(record[4]),
                    'periodo':str(record[5]),
                    'nombreDocente': docente.name,
                    'motivo': 'No Se Encontro el Tipo de Ajuste',
                }

                noDocente = list(filter(lambda x: (x['cedula'] == dict['cedula']) and
                                                (x['tipo']== dict['tipo']) and
                                                (x['monto'] == dict['monto']) and
                                                (x['fecha']== dict['fecha']) and
                                                (x['anoo'] == dict['anoo']) and
                                                (x['periodo']== dict['periodo']) and
                                                (x['motivo'] == dict['motivo']),docentesNoEncontradosList))
                if len(noDocente) ==  0:
                    docentesNoEncontradosList.append(dict)

                continue

            ajustesPago = list(filter(lambda x: (x.docente_id.id == docente.id) and
                                          (x.cuatrimestre_id.id == cuatrimestre.id) and
                                          (x.fechaAjuste == record[3].date()) and
                                          (x.name == ajuste.name) and
                                          (x.monto == float(record[2])) and
                                          (x.ajuste_id == ajuste.id) , cursosDocente.ajustes_lines_ids))

            total = 0
            if self.tipo == 'Monto Fijo':
                if float(record[2]) > 0:
                    total = float(record[2]) /  self.env['configuraciones'].search([]).factor
            else:
                m = int(record[8])
                total = (self.env['contrato.empleado'].search([('empleado_id','=',docente.id)]).salario / 60) * ((int(record[2]) + (m / 60)) * 60)

            vals = {
                'ajuste_id': ajuste.id,
                'name': ajuste.name,
                'monto': float(record[2]),
                'horas': 0,
                'minutos': 0,
                'cuatrimestre_id': cuatrimestre.id,
                'docente_id': docente.id,
                'descripcion': str(record[7]),
                'total': total,
                'autoriza_id': autoriza.id,
                'fechaAjuste': record[3].date(),
                'pagoEfectuado': False
            }
            if self.tipo == 'Monto Fijo':
                if ajustesPago:
                    cursosDocente.ajustes_lines_ids = [(1, ajustesPago[0].id, vals)]
                else:
                    cursosDocente.ajustes_lines_ids = [(0, 0, vals)]
            else:
                cursosDocente.ajustes_lines_ids = [(0, 0, vals)]

        if len(docentesNoEncontradosList) > 0:
            template_id = self.env.ref('nomina.email_ajuste_pago_docente_no_encontrado').id
            template = self.env['mail.template'].browse(template_id)
            email_values = {'email_to': self.env.user.email,
                            'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                            'subject': 'Reporte de Ajustes de Pago no Aplicados'
                            }
            template.with_context(datosCorreo=docentesNoEncontradosList).send_mail(self.id, email_values=email_values, force_send=True)