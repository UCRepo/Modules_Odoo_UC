# -*- coding: utf-8 -*-
import pytz
from datetime import date, timedelta, datetime
from odoo import api, fields, models, _

class AccionPersonalReport(models.AbstractModel):
    _name='report.uia_portal.report_accion_personal_vacaciones_id'

    @api.model
    def _get_report_values(self, docids, data):
        docente_pago_report = self.env['ir.actions.report']._get_report_from_name('uia_portal.report_accion_personal_vacaiones_id')
        return {
            'get_accion_personal_vacaciones': self.get_accion_personal_vacaciones(data['vacacionesid']),
        }

    def get_accion_personal_vacaciones(self,solicitudVacaciones):
        jefaturaRH = solicitudVacaciones.contratoEmpleado_id.jefaturaRH_id
        timezoneEmeplado = pytz.timezone(solicitudVacaciones.empleado_id.resource_id.tz)
        timezoneJefatura = pytz.timezone(solicitudVacaciones.contratoEmpleado_id.jefaturaInmediata_id.resource_id.tz)
        timezoneRH = pytz.timezone(jefaturaRH.resource_id.tz)
        firmaEmpleadoFecha = pytz.utc.localize(solicitudVacaciones.fechaFirmaEmpleado).astimezone(timezoneEmeplado).replace(tzinfo=None)
        firmaJefaturaFecha = pytz.utc.localize(solicitudVacaciones.fechaFirmaJefatura).astimezone(timezoneJefatura).replace(tzinfo=None)
        firmaRHFecha = pytz.utc.localize(solicitudVacaciones.fechaFirmaRH).astimezone(timezoneRH).replace(tzinfo=None)

        vacacionesDetail = self.env['contrato.empleado.vacaciones.line.detail'].sudo().search([('masterVacacionesLine_id', '=', solicitudVacaciones.id)])
        vacacionesList = []
        if len(vacacionesDetail) > 0:
            for data in vacacionesDetail:
                dict = {
                    'dt_desde': data.fechaInicioVacaciones,
                    'dt_hasta': data.fechaFinVacaciones,
                    'fechaMedioDia': data.fechaMedioDia != False if data.fechaMedioDia else '',
                    'tipoMedioDia': data.tipoMedioDia != False if data.tipoMedioDia else '',
                    'cantDias': data.diasVacaciones,
                }
                vacacionesList.append(dict)
        else:
            dict = {
                'dt_desde': solicitudVacaciones.fechaInicioVacaciones,
                'dt_hasta': solicitudVacaciones.fechaFinVacaciones,
                'fechaMedioDia': solicitudVacaciones.fechaMedioDia != False if solicitudVacaciones.fechaMedioDia else '',
                'tipoMedioDia': solicitudVacaciones.tipoMedioDia != False if solicitudVacaciones.tipoMedioDia else '',
                'cantDias': solicitudVacaciones.diasVacaciones,
            }
            vacacionesList.append(dict)

        return {
            'fechaEmision': date.today(),
            'nombreAdministrativo': solicitudVacaciones.empleado_id.name,
            'cedulaAdministrativo': solicitudVacaciones.empleado_id.identification_id,
            'departamentoAdministrativo': solicitudVacaciones.empleado_id.department_id.name,
            'puestoAdministrativo': solicitudVacaciones.empleado_id.job_title,
            'jefatura': solicitudVacaciones.empleado_id.department_id.manager_id.name,
            'vacacionesList': vacacionesList,
            'desdehasta': ' DESDE '+ str(solicitudVacaciones.fechaInicioVacaciones) +' HASTA '+ str(solicitudVacaciones.fechaFinVacaciones) +' ',
            # 'regreso': solicitudVacaciones.fechaFinVacaciones + timedelta(days=1),
            'restantes': solicitudVacaciones.contratoEmpleado_id.vacacionesRestantes,
            'diasVacaciones': solicitudVacaciones.diasVacaciones,
            'firmaEmpleadoNombre': solicitudVacaciones.empleado_id.name,
            'firmaEmpleadoUsuario': solicitudVacaciones.empleado_id.work_email,
            'firmaEmpleadoFecha': datetime.strftime(firmaEmpleadoFecha,"%Y-%m-%d %H:%M"),
            'firmaJefaturaNombre': solicitudVacaciones.contratoEmpleado_id.jefaturaInmediata_id.name,
            'firmaJefaturaUsuario': solicitudVacaciones.contratoEmpleado_id.jefaturaInmediata_id.work_email,
            'firmaJefaturaFecha': datetime.strftime(firmaJefaturaFecha,"%Y-%m-%d %H:%M"),
            'firmaRHNombre': jefaturaRH.name,
            'firmaRHUsuario': jefaturaRH.work_email,
            'firmaRHFecha': datetime.strftime(firmaRHFecha,"%Y-%m-%d %H:%M"),
        }




