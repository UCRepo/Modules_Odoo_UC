import base64
from datetime import *
from odoo.http import request
import openpyxl
import requests
import math
import pytz
import json
import logging
from io import BytesIO
from odoo import api, fields, models, _
from collections import OrderedDict
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class NominaCargarJustificacionMarcasDocenteWizard(models.TransientModel):
    _name = "nomina.cargar.justificacion.marcas.docente.wizard"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Cargar Justificacion Marcas Docente"

    documento_Justificaciones= fields.Binary(
        string='Justificación'
    )

    def cargar_justificacion_marcas(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        wb = openpyxl.load_workbook(filename=BytesIO(base64.b64decode(self.documento_Justificaciones)),read_only=True)

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
                    'anoo':str(record[1]),
                    'periodo':str(record[2]),
                    'dia':str(record[3]),
                    'fecha':str(record[4]),
                    'horaInicio':str(record[5]),
                    'minutoInicio':str(record[6]),
                    'horaFinal':str(record[7]),
                    'minutoFinal':str(record[8]),
                    'nombreDocente': '',
                    'motivo': 'No Se Encontro al Docente',
                }

                noDocente = list(filter(lambda x: (x['cedula'] == dict['cedula']) and
                                                (x['dia']== dict['dia']) and
                                                (x['horaInicio'] == dict['horaInicio']) and
                                                (x['minutoInicio']== dict['minutoInicio']) and
                                                (x['horaFinal'] == dict['horaFinal']) and
                                                (x['minutoFinal']== dict['minutoFinal']) and
                                                (x['motivo'] == dict['motivo']),docentesNoEncontradosList))
                if len(noDocente) ==  0:
                    docentesNoEncontradosList.append(dict)

                continue

            cuatrimestre = self.env['periodo.cuatrimestre'].search(['&', ('year', '=', str(record[1])), ('decripcion', '=', str(record[2]) + "Q")])

            cursosDocente = self.env['cursos.docente'].search(['&', ('docente_id', '=', docente.id), ('cuatrimestre_id', '=', cuatrimestre.id)])

            asistenciaLine = self.env['asistencia.docente.line'].search(['&',('asistencia_id', '=', cursosDocente.id),('docente_id','=',docente.id)])

            curso = list(filter(lambda x: (x.docente_id.id == docente.id) and
                                          (x.cuatrimestre_id.id == cuatrimestre.id) and
                                          (x.horaInicio == str(record[5])) and
                                          (x.minutoInicio == str(record[6])) and
                                          (x.horaFinal == str(record[7])) and
                                          (x.minutoFinal == str(record[8])) and
                                          (x.dia1 == str(record[3])) and
                                          (x.cursoActivo == True) , cursosDocente.cursos_lines_ids))

            if len(curso) <= 0:
                dict ={
                    'cedula':str(record[0]),
                    'anoo':str(record[1]),
                    'periodo':str(record[2]),
                    'dia':str(record[3]),
                    'fecha':str(record[4]),
                    'horaInicio':str(record[5]),
                    'minutoInicio':str(record[6]),
                    'horaFinal':str(record[7]),
                    'minutoFinal':str(record[8]),
                    'nombreDocente': docente.name,
                    'motivo': 'No Se Encontro el Curso',
                }
                noCurso = list(filter(lambda x: (x['cedula'] == dict['cedula']) and
                                                (x['dia']== dict['dia']) and
                                                (x['horaInicio'] == dict['horaInicio']) and
                                                (x['minutoInicio']== dict['minutoInicio']) and
                                                (x['horaFinal'] == dict['horaFinal']) and
                                                (x['minutoFinal']== dict['minutoFinal']) and
                                                (x['motivo'] == dict['motivo']),docentesNoEncontradosList))
                if len(noCurso) ==  0:
                    docentesNoEncontradosList.append(dict)
                continue

            asistencia = list(filter(lambda x: (x.docente_id.id == docente.id) and
                                               (x.cuatrimestre_id.id == cuatrimestre.id) and
                                               (x.cursoMarca == curso[0].codigoCurso) and
                                               (x.fechaCurso == record[4].date()), asistenciaLine))

            vals = {
                'docente_id': docente.id,
                'cuatrimestre_id': cuatrimestre.id,
                'asistencia_id': cursosDocente.id,
                'aplicar': True,
                'cursoMarca': curso[0].codigoCurso,
                'fechaCurso': record[4].date(),
                'horarioCurso': curso[0].horario,
                'entradaClases': datetime.strptime(str(record[4].date())+' '+str(record[5])+':'+str(record[6])+':00',"%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                'salidaClases':  datetime.strptime(str(record[4].date())+' '+str(record[7])+':'+str(record[8])+':00',"%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                'tiempoClases': curso[0].cantiadadHoras,
                'deduccionEntradaTardia': 0,
                'deduccionSalidaTemprana': 0,
                'deduccionOmisionMarca': 0,
                'deduccionAusencia': 0,
                'deduccionTotal': 0,
                'marcaJustificada': True,
                'estado': 'OK'
            }

            if asistencia:
                cursosDocente.asistencia_line_ids = [(1, asistencia[0].id, vals)]
            else:
                cursosDocente.asistencia_line_ids = [(0, 0, vals)]

        if len(docentesNoEncontradosList) > 0:
            template_id = self.env.ref('nomina.email_justificacion_marcas_docente_no_encontrado').id
            template = self.env['mail.template'].browse(template_id)
            email_values = {'email_to': self.env.user.email,
                            'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                            'subject': 'Reporte de Justificación de Marcas no Aplicadas'
                            }
            template.with_context(listAsistencia=docentesNoEncontradosList).send_mail(self.id, email_values=email_values, force_send=True)