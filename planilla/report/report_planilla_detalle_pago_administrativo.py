# -*- coding: utf-8 -*-
import pytz
from datetime import date, timedelta, datetime
from odoo import api, fields, models, _

class PlanillaDocenteReport(models.AbstractModel):
    _name='report.planilla.report_detalle_pago_administrativo_id'

    @api.model
    def _get_report_values(self, docids, data):
        docente_pago_report = self.env['ir.actions.report']._get_report_from_name('planilla.report_detalle_pago_administrativo_id')
        holidays = self.env['cursos.docente'].browse(self.ids)
        return {
            'doc_ids': self.ids,
            'doc_model': docente_pago_report.model,
            'get_pago_info': self.get_pago_info(data['dataPago']),
        }

    def get_pago_info(self,dataPago):
        deduccionesList = []
        otrosConceptosList = []
        impuestosList = []
        prestamosList = []
        reembolsosList = []
        otrosCargosList = []
        if dataPago.CCSSEmpleado > 0:
            deduccionesList.append('CCSS '+' ₡'+"{:,}".format(dataPago.CCSSEmpleado))
        if dataPago.rentaEmpleado > 0:
            deduccionesList.append('Renta ' + ' ₡' + "{:,}".format(dataPago.rentaEmpleado))
        if dataPago.embargo > 0:
            deduccionesList.append('Embargo ' + ' ₡' + "{:,}".format(dataPago.embargo))
        if dataPago.pension > 0:
            deduccionesList.append('Pensión ' + ' ₡' + "{:,}".format(dataPago.pension))
        if dataPago.rentaEmpleadoDocente > 0:
            deduccionesList.append('Renta docente ' + ' ₡' + "{:,}".format(dataPago.rentaEmpleadoDocente))
        if dataPago.deduccionAsistencia > 0:
            deduccionesList.append('Asistencia ' + ' ₡' + "{:,}".format(dataPago.rentaEmpleadoDocente))
        return {
            'deduccionesList': deduccionesList,
            'otrosConceptosList': otrosConceptosList,
            'impuestosList': impuestosList,
            'prestamosList': prestamosList,
            'reembolsosList': reembolsosList,
            'otrosCargosList': otrosCargosList,
            'desdehasta': str(dataPago.prePlanilla_id.desde) +' a '+str(dataPago.prePlanilla_id.hasta),
            'nombreEmpleado': dataPago.nombreEmpleado,
            'correoEmpleado': dataPago.correoEmpleado,
            'cedulaEmpleado': dataPago.cedulaEmpleado,
            'cedulaEmpleado': dataPago.cedulaEmpleado,
            'departamento': dataPago.empleado_id.department_id.name,
            'puesto': dataPago.empleado_id.job_title,
            'salarioBruto': ' ₡ '+"{:,}".format((dataPago.salarioBruto)/2),
            'diasPagoCompleto': ' '+"{:.2f}".format(dataPago.diasPagoCompleto),
            'diasIncapacidad': ' '+"{:.2f}".format((dataPago.diasPagoMedio + dataPago.diasPagoNulo)),
            'deducciones': ' ₡'+"{:,}".format(dataPago.totalDeduccion),
            'salarioNeto': ' ₡'+"{:,}".format(dataPago.salarioNeto),
            'feriados': ' '+"{:.2f}".format(0),
            'tareas': ' ₡'+"{:,}".format(0),
            'timepoExtra': ' '+"{:.2f}".format(0),
            'timepoExtraFeriados': ' '+"{:.2f}".format(0),
            'vacaciones': ' '+"{:.2f}".format(0),
            'extraFeriado': ' '+"{:.2f}".format(0),
            'totalVacaciones': ' ₡'+"{:,}".format(0),
            'totalTimepoExtra': ' ₡'+"{:,}".format(0),
            'otrosConceptos': ' ₡'+"{:,}".format(0),
            'beneficiosPagar': ' ₡'+"{:,}".format(0),
            'impuestos': ' ₡'+"{:,}".format(0),
            'prestamos': ' ₡'+"{:,}".format(0),
            'reembolsos': ' ₡'+"{:,}".format(0),
            'cargos': ' ₡'+"{:,}".format(0),
        }





