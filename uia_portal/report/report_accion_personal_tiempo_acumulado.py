# -*- coding: utf-8 -*-
import pytz
from datetime import date, timedelta, datetime
from odoo import api, fields, models, _

class AccionPersonalReport(models.AbstractModel):
    _name='report.uia_portal.report_accion_personal_tiempo_acumulado_id'

    @api.model
    def _get_report_values(self, docids, data):
        docente_pago_report = self.env['ir.actions.report']._get_report_from_name('uia_portal.report_accion_personal_tiempo_acumulado_id')
        return {
            'get_accion_personal_tiempo_acumulado': self.get_accion_personal_tiempo_acumulado(data['idTiempoAcumulado']),
        }

    def get_accion_personal_tiempo_acumulado(self,solicitudTiempoAcumulado):
        jefaturaRH = solicitudTiempoAcumulado.contratoEmpleado_id.jefaturaRH_id
        timezoneEmeplado = pytz.timezone(solicitudTiempoAcumulado.empleado_id.resource_id.tz)
        timezoneJefatura = pytz.timezone(solicitudTiempoAcumulado.contratoEmpleado_id.jefaturaInmediata_id.resource_id.tz)
        timezoneRH = pytz.timezone(jefaturaRH.resource_id.tz)
        firmaEmpleadoFecha = pytz.utc.localize(solicitudTiempoAcumulado.fechaFirmaEmpleado).astimezone(timezoneEmeplado).replace(tzinfo=None)
        firmaJefaturaFecha = pytz.utc.localize(solicitudTiempoAcumulado.fechaFirmaJefatura).astimezone(timezoneJefatura).replace(tzinfo=None)
        firmaRHFecha = pytz.utc.localize(solicitudTiempoAcumulado.fechaFirmaRH).astimezone(timezoneRH).replace(tzinfo=None)
        entradaSalida = ''

        if solicitudTiempoAcumulado.inicioFinJornada != 'Rango de Fechas':
            entradaSalida = 'INICIANDO LABORES '+str(solicitudTiempoAcumulado.tiempoAcumuladoTomado/60)+'h DESPUES DE SU HORARIO DE ENTRADA'
            if solicitudTiempoAcumulado.inicioFinJornada == 'finJornada':
                entradaSalida = 'FINALIZANDO LABORES '+str(solicitudTiempoAcumulado.tiempoAcumuladoTomado/60)+'h DESPUES DE SU HORARIO DE SALIDA'

        return {
            'fechaEmision': date.today(),
            'nombreAdministrativo': solicitudTiempoAcumulado.empleado_id.name,
            'cedulaAdministrativo': solicitudTiempoAcumulado.empleado_id.identification_id,
            'departamentoAdministrativo': solicitudTiempoAcumulado.empleado_id.department_id.name,
            'puestoAdministrativo': solicitudTiempoAcumulado.empleado_id.job_title,
            'jefatura': solicitudTiempoAcumulado.empleado_id.department_id.manager_id.name,
            'fecha':  str(solicitudTiempoAcumulado.fechaDesdeTiempoAcumulado)+' al ' +str(solicitudTiempoAcumulado.fechaHastaTiempoAcumulado),
            'entradaSalida':  entradaSalida,
            'tiempoAcumuladoRestante': solicitudTiempoAcumulado.contratoEmpleado_id.tiempoAcumuladoRestante/60,
            'tiempoTomado': solicitudTiempoAcumulado.tiempoAcumuladoTomado/60,
            'firmaEmpleadoNombre': solicitudTiempoAcumulado.empleado_id.name,
            'firmaEmpleadoUsuario': solicitudTiempoAcumulado.empleado_id.work_email,
            'firmaEmpleadoFecha': datetime.strftime(firmaEmpleadoFecha,"%Y-%m-%d %H:%M"),
            'firmaJefaturaNombre': solicitudTiempoAcumulado.empleado_id.department_id.manager_id.name,
            'firmaJefaturaUsuario': solicitudTiempoAcumulado.empleado_id.department_id.manager_id.work_email,
            'firmaJefaturaFecha': datetime.strftime(firmaJefaturaFecha,"%Y-%m-%d %H:%M"),
            'firmaRHNombre': jefaturaRH.name,
            'firmaRHUsuario': jefaturaRH.work_email,
            'firmaRHFecha': datetime.strftime(firmaRHFecha,"%Y-%m-%d %H:%M"),
        }





