import pytz
import logging
from datetime import date, timedelta, datetime
from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)

class NominaAsistenciaDocenteReport(models.AbstractModel):
    _name='report.nomina.report_asistencia_docente_id'

    @api.model
    def _get_report_values(self, docids, data):
        asistencia_docente = self.env['ir.actions.report']._get_report_from_name('nomina.report_asistencia_docente_id')
        data['planilla_line_ids'] = self.env['planilla.cuatrimestre'].search([('id','=',data['planilla_line_ids'])])
        data['docente_ids'] = self.env['hr.employee'].search([('id','=',data['docente_ids'])])
        return {
            'doc_ids': self.ids,
            'doc_model': asistencia_docente.model,
            'get_asistencia_docente': self.get_asistencia_docente(data['planilla_line_ids'],data['docente_ids']),
        }

    def get_asistencia_docente(self,planilla_line_ids,docente_ids):
        resultList = []
        asistenciaLine = []
        result = {
            'nombreDocente': docente_ids.name,
            'correo': docente_ids.work_email,
        }
        for asistencia in self.env['asistencia.docente.line'].search(['&', ('docente_id', '=', docente_ids.id), ('cuatrimestre_id', '=', planilla_line_ids.cuatrimestrePlanilla_id.id)]):
            fechaCurso = asistencia.fechaCurso
            if fechaCurso >= planilla_line_ids.fechaInicioPago and fechaCurso <= planilla_line_ids.fechaFinalPago:
                asistencia = {
                    'fechaCurso': asistencia.fechaCurso,
                    'cursoMarca': asistencia.cursoMarca,
                    'entradaClases': asistencia.entradaClases,
                    'salidaClases': asistencia.salidaClases,
                    'estado': asistencia.estado,
                    'deduccionTotal': asistencia.deduccionTotal,
                }
                asistenciaLine.append(asistencia)

        result.update({
            'asistenciaLine': asistenciaLine
        })
        resultList.append(result)

        return resultList





















