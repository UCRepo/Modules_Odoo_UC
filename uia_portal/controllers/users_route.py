# -*- coding: utf-8 -*-
import io
import werkzeug.utils
from odoo.tools.misc import xlsxwriter
from PyPDF2 import PdfFileReader, PdfFileWriter

from odoo import http
from odoo.http import content_disposition, request
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo.addons.portal.controllers.portal import CustomerPortal

class UsersRoute(CustomerPortal):
    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search([('work_email', '=', user.login)])

        if empleado:
            return http.request.render('uia_portal.portal_administrativo_home', {})
        else:
            res = super(UsersRoute,self).home( **kw)
            return res

    @http.route('/uia_menu_portal', type='json', auth="user", website=True)
    def counters(self, **kw):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])

        aceptaVacaciones = request.env['contrato.empleado'].sudo().search_count(['|', ('jefaturaInmediata_id', '=', empleado.id), ('jefaturaInmediataDelegado_id', '=', empleado.id)])

        return {
            'justifica': request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)]).justificaMarca,
            'adicionales': request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)]).cargaAdicionales,
            'ajustes': request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)]).cargaAjustes,
            'aceptaVacaciones': True if aceptaVacaciones > 0 else False,
        }

class GestionUserPortal(http.Controller):

    @http.route(['/my/uia_portal_gestion_vacaciones', '/my/home/uia_portal_gestion_vacaciones'], type='http', auth="user", website=True)
    def gestionVacaciones(self, **kw):
        return request.render('uia_portal.portal_administrativo_gestion_vacaciones_home',{})

    @http.route('/get_vacaciones_info', type='json', auth="user", website=True)
    def getVacacionesInfo(self, **kw):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([ ('empleado_id', '=', empleado.id)])

        return {
            'total': contrato.totalVacaciones,
            'tomadas': contrato.vacacionesTomadas,
            'restantes': contrato.vacacionesRestantes,
        }

    @http.route('/get_vacaciones_historial', type='json', auth="user", website=True)
    def getVacacionesHistorial(self, **kw):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])
        vacacionesList = []
        for vacaciones in contrato.vacaciones_ids:
            inicioVacaciones = ''
            finVacaciones = ''
            vacacionesDetail = request.env['contrato.empleado.vacaciones.line.detail'].sudo().search([('masterVacacionesLine_id', '=', vacaciones.id)])
            if vacacionesDetail:
                for detailVacaciones in vacacionesDetail:
                    inicioVacaciones +=  str(detailVacaciones.fechaInicioVacaciones)+'\n'
                    finVacaciones +=  str(detailVacaciones.fechaFinVacaciones)+'\n'
            else:
                inicioVacaciones = vacaciones.fechaInicioVacaciones
                finVacaciones = vacaciones.fechaFinVacaciones

            vacacionesDict = {
                'fechaInicioVacaciones': inicioVacaciones,
                'fechaFinVacaciones': finVacaciones,
                'diasVacaciones': vacaciones.diasVacaciones,
                'estadoJefatura': vacaciones.estadoJefatura,
                'estadoRH': vacaciones.estadoRH,
            }
            vacacionesList.append(vacacionesDict)
        return vacacionesList

    @http.route('/verificacion_vacaciones_solicitud', type='json', auth="user", website=True)
    def verificacion_vacaciones_solicitud(self,valsJS):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&', ('department_id.name', '!=', 'Docentes'), ('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])
        ICPSudo = request.env['ir.config_parameter'].sudo()

        totalVacaciones = 0
        for data in valsJS:
            fechaInicioVacaciones = datetime.strptime(data['dt_desde'], "%Y-%m-%d")
            fechaFinVacaciones = datetime.strptime(data['dt_hasta'], "%Y-%m-%d")
            fechaMedioDia = None
            if 'fechaMedioDia' in data:
                fechaMedioDia = datetime.strptime(data['fechaMedioDia'], "%Y-%m-%d")

            diaVacaciones = fechaInicioVacaciones

            horarioEmpleado = request.env['horario.empleado'].sudo().search([('empleado_id', '=', empleado.id)])
            if not horarioEmpleado:
                return 'Usted no tiene horario asignado para  las fechas de peticion de vacaciones'

            while diaVacaciones <= fechaFinVacaciones:
                horarioDia = request.env['horario.empleado.line'].sudo().search(['&', ('fechaDesde', '<=', diaVacaciones), ('fechaHasta', '>=', diaVacaciones),('horarioEmpleado_id', '=', horarioEmpleado.id)])
                if not horarioDia:
                    return 'Usted no tiene horario asignado para  la fecha ' + str(
                        diaVacaciones.date()) + ' de petición de vacaciones'

                if diaVacaciones.weekday() == 0:
                    if horarioDia.horaInicioLunes != False:
                        if 'fechaMedioDia' in data:
                            if fechaMedioDia == diaVacaciones:
                                totalVacaciones += 0.5
                            else:
                                totalVacaciones += 1
                        else:
                            totalVacaciones += 1

                elif diaVacaciones.weekday() == 1:
                    if horarioDia.horaInicioMartes != False:
                        if 'fechaMedioDia' in data:
                            if fechaMedioDia == diaVacaciones:
                                totalVacaciones += 0.5
                            else:
                                totalVacaciones += 1
                        else:
                            totalVacaciones += 1

                elif diaVacaciones.weekday() == 2:
                    if horarioDia.horaInicioMiercoles != False:
                        if 'fechaMedioDia' in data:
                            if fechaMedioDia == diaVacaciones:
                                totalVacaciones += 0.5
                            else:
                                totalVacaciones += 1
                        else:
                            totalVacaciones += 1

                elif diaVacaciones.weekday() == 3:
                    if horarioDia.horaInicioJueves != False:
                        if 'fechaMedioDia' in data:
                            if fechaMedioDia == diaVacaciones:
                                totalVacaciones += 0.5
                            else:
                                totalVacaciones += 1
                        else:
                            totalVacaciones += 1

                elif diaVacaciones.weekday() == 4:
                    if horarioDia.horaInicioViernes != False:
                        if 'fechaMedioDia' in data:
                            if fechaMedioDia == diaVacaciones:
                                totalVacaciones += 0.5
                            else:
                                totalVacaciones += 1
                        else:
                            totalVacaciones += 1

                elif diaVacaciones.weekday() == 5:
                    if horarioDia.horaInicioSabado != False:
                        if 'fechaMedioDia' in data:
                            if fechaMedioDia == diaVacaciones:
                                totalVacaciones += 0.5
                            else:
                                totalVacaciones += 0.5
                        else:
                            totalVacaciones += 0.5

                elif diaVacaciones.weekday() == 6:
                    if horarioDia.horaInicioDomingo != False:
                        if 'fechaMedioDia' in data:
                            if fechaMedioDia == diaVacaciones:
                                totalVacaciones += 0.5
                            else:
                                totalVacaciones += 1
                        else:
                            totalVacaciones += 1

                diaVacaciones += timedelta(days=1)

        if totalVacaciones <= contrato.vacacionesRestantes:

            return {
                'result': False
            }
        else:
            return {
                'result': True,
                'msg':'La cantidad de vacaciones supera las que tiene a disposición'
            }

    @http.route('/set_vacaciones_solicitud', type='json', auth="user", website=True)
    def setVacacionesSolicitud(self,valsJS=None):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])
        ICPSudo = request.env['ir.config_parameter'].sudo()

        total_Vacaciones = 0
        listVacaciones = []
        for data in valsJS:
            totalVacaciones = 0
            fechaInicioVacaciones = datetime.strptime(data['dt_desde'], "%Y-%m-%d")
            fechaFinVacaciones = datetime.strptime(data['dt_hasta'], "%Y-%m-%d")
            fechaMedioDia = None
            if 'fechaMedioDia' in data:
                fechaMedioDia = datetime.strptime(data['fechaMedioDia'], "%Y-%m-%d")

            diaVacaciones = fechaInicioVacaciones

            horarioEmpleado = request.env['horario.empleado'].sudo().search([('empleado_id', '=', empleado.id)])
            if not horarioEmpleado:
                return 'Usted no tiene horario asignado para  las fechas de peticion de vacaciones'

            while diaVacaciones <= fechaFinVacaciones:
                horarioDia = request.env['horario.empleado.line'].sudo().search(['&', ('fechaDesde', '<=', diaVacaciones), ('fechaHasta', '>=', diaVacaciones),('horarioEmpleado_id', '=', horarioEmpleado.id)])
                if not horarioDia:
                    return 'Usted no tiene horario asignado para  la fecha ' + str(diaVacaciones.date()) + ' de petición de vacaciones'

                if diaVacaciones.weekday() == 0:
                    if horarioDia.horaInicioLunes != False:
                        if 'fechaMedioDia' in data:
                            if fechaMedioDia == diaVacaciones:
                                totalVacaciones += 0.5
                            else:
                                totalVacaciones += 1
                        else:
                            totalVacaciones += 1

                elif diaVacaciones.weekday() == 1:
                    if horarioDia.horaInicioMartes != False:
                        if 'fechaMedioDia' in data:
                            if fechaMedioDia == diaVacaciones:
                                totalVacaciones += 0.5
                            else:
                                totalVacaciones += 1
                        else:
                            totalVacaciones += 1

                elif diaVacaciones.weekday() == 2:
                    if horarioDia.horaInicioMiercoles != False:
                        if 'fechaMedioDia' in data:
                            if fechaMedioDia == diaVacaciones:
                                totalVacaciones += 0.5
                            else:
                                totalVacaciones += 1
                        else:
                            totalVacaciones += 1

                elif diaVacaciones.weekday() == 3:
                    if horarioDia.horaInicioJueves != False:
                        if 'fechaMedioDia' in data:
                            if fechaMedioDia == diaVacaciones:
                                totalVacaciones += 0.5
                            else:
                                totalVacaciones += 1
                        else:
                            totalVacaciones += 1

                elif diaVacaciones.weekday() == 4:
                    if horarioDia.horaInicioViernes != False:
                        if 'fechaMedioDia' in data:
                            if fechaMedioDia == diaVacaciones:
                                totalVacaciones += 0.5
                            else:
                                totalVacaciones += 1
                        else:
                            totalVacaciones += 1

                elif diaVacaciones.weekday() == 5:
                    if horarioDia.horaInicioSabado != False:
                        if 'fechaMedioDia' in data:
                            if fechaMedioDia == diaVacaciones:
                                totalVacaciones += 0.5
                            else:
                                totalVacaciones += 0.5
                        else:
                            totalVacaciones += 0.5

                elif diaVacaciones.weekday() == 6:
                    if horarioDia.horaInicioDomingo != False:
                        if 'fechaMedioDia' in data:
                            if fechaMedioDia == diaVacaciones:
                                totalVacaciones += 0.5
                            else:
                                totalVacaciones += 1
                        else:
                            totalVacaciones += 1


                diaVacaciones += timedelta(days=1)
            total_Vacaciones += totalVacaciones
            listVacaciones.append({
                'fechaInicioVacaciones': fechaInicioVacaciones.date(),
                'fechaFinVacaciones': fechaFinVacaciones.date(),
                'diasVacaciones': totalVacaciones,
                'fechaMedioDia': data['fechaMedioDia'] if "fechaMedioDia" in valsJS else False,
                'tipoMedioDia': data['tipoMedioDia'] if "tipoMedioDia" in valsJS else False,
            })

        if total_Vacaciones == 0:
            return 'La suma de las vacaciones es igual a 0 porfavor verificar su horario'
        if total_Vacaciones <= contrato.vacacionesRestantes:
            fechaFirma = datetime.today() + timedelta(hours=6)
            vals = {
                'contratoEmpleado_id': contrato.id,
                'empleado_id': empleado.id,
                'diasVacaciones': total_Vacaciones,
                'fechaFirmaEmpleado': datetime.today() + timedelta(hours=6),
            }

            res = request.env['contrato.empleado.vacaciones.line'].sudo().create(vals)

            for data in listVacaciones:
                data.update({
                    'masterVacacionesLine_id': res.id
                })
                request.env['contrato.empleado.vacaciones.line.detail'].sudo().create(data)

            contrato.vacacionesTomadas += total_Vacaciones
            contrato.vacacionesRestantes -= total_Vacaciones

            template_id = request.env.ref('uia_portal.email_correo_aceptacion_vacaciones').id
            template = request.env['mail.template'].browse(template_id)
            email_values = {'email_to': contrato.jefaturaInmediata_id.work_email,
                            'email_cc': contrato.jefaturaInmediataDelegado_id.work_email,
                            'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                            'subject': 'Aprobación de vacaciones de ' + empleado.name,
                            }
            datosCorreo = {
                'link': request.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/set_vacaciones_aprobacion_jefaturaInmediata?idVacaciones="+str(res.id),
                'nombre': empleado.name,
                'jefatura': contrato.jefaturaInmediata_id.name,
            }

            template.sudo().with_context(datosCorreo=datosCorreo).send_mail(res.id, email_values=email_values, force_send=True)

            return 'Solicitud de vacaciones creada'
        else:
            return 'La cantidad de vacaciones supera las que tiene a disposición'

    @http.route('/set_vacaciones_aprobacion_jefaturaInmediata', type='http', auth="user", website=True)
    def set_vacaciones_aprobacion_jefaturaInmediata(self,**kw):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])
        vals = {}

        solicitudVacaciones = request.env['contrato.empleado.vacaciones.line'].sudo().search([('id', '=', int(request.params['idVacaciones']))])

        if solicitudVacaciones.contratoEmpleado_id.jefaturaInmediata_id.id == empleado.id or solicitudVacaciones.contratoEmpleado_id.jefaturaInmediataDelegado_id.id == empleado.id:
            if solicitudVacaciones.estadoJefatura == 'Revisión pendiente':
                diaMedio = False

                if solicitudVacaciones.fechaMedioDia != False:
                    diaMedio = True

                vacacionesDetail = request.env['contrato.empleado.vacaciones.line.detail'].sudo().search([('masterVacacionesLine_id', '=', solicitudVacaciones.id)])
                vacacionesList = []
                if len(vacacionesDetail) > 0:
                    for data in vacacionesDetail:
                        dict ={
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


                vals.update({
                    'tipo': 'Vacaciones',
                    'nombre_empleado': solicitudVacaciones.empleado_id.name,
                    'vacacionesList':vacacionesList,
                    'txt_razon': solicitudVacaciones.razon,
                    'idVacaciones': request.params['idVacaciones'],
                    'accionRealizada': False
                })

                return http.request.render('uia_portal.portal_administrativo_gestion_vacaciones_accion_jefatura_inmediata',vals)
            else:
                vals.update({
                    'accionRealizada': True
                })
                return http.request.render('uia_portal.portal_administrativo_gestion_vacaciones_accion_jefatura_inmediata',vals)

    @http.route('/set_proceso_accion_vacaciones_jefatura_inmediata', type='json', auth="user", website=True)
    def set_proceso_accion_vacaciones_jefatura_inmediata(self,valsJS=None):
        solicitudVacaciones = request.env['contrato.empleado.vacaciones.line'].sudo().search([('id', '=', int(valsJS['id_vacaciones']))])
        ICPSudo = request.env['ir.config_parameter'].sudo()

        solicitudVacaciones.estadoJefatura = valsJS['accion']

        if valsJS['accion'] == "Aceptado":

            solicitudVacaciones.fechaFirmaJefatura = datetime.today() + timedelta(hours=6)
            template_id = request.env.ref('uia_portal.email_correo_aceptacion_vacaciones').id
            template = request.env['mail.template'].browse(template_id)

            email_values = {
                'email_to': solicitudVacaciones.contratoEmpleado_id.jefaturaRH_id.work_email,
                'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                'subject': 'Aprobación de vacaciones de ' + solicitudVacaciones.contratoEmpleado_id.empleado_id.name,
            }

            datosCorreo = {
                'link': request.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/set_vacaciones_aprobacion_jefaturaRH?idVacaciones="+str(solicitudVacaciones.id),
                'nombre': solicitudVacaciones.contratoEmpleado_id.empleado_id.name,
                'jefatura': solicitudVacaciones.contratoEmpleado_id.jefaturaRH_id.name,
            }

            template.sudo().with_context(datosCorreo=datosCorreo).send_mail(solicitudVacaciones.id, email_values=email_values,force_send=True)
            return {
                'result': True,
            }
        else:
            solicitudVacaciones.contratoEmpleado_id.vacacionesTomadas -= solicitudVacaciones.diasVacaciones
            solicitudVacaciones.contratoEmpleado_id.vacacionesRestantes += solicitudVacaciones.diasVacaciones
            solicitudVacaciones.activo = False
            return {
                'result': True,
            }

    @http.route('/set_vacaciones_aprobacion_jefaturaRH', type='http', auth="user", website=True)
    def set_vacaciones_aprobacion_jefaturaRH(self,**kw):

        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])

        solicitudVacaciones = request.env['contrato.empleado.vacaciones.line'].sudo().search([('id', '=', int(request.params['idVacaciones']))])

        if solicitudVacaciones.contratoEmpleado_id.jefaturaRH_id.id == empleado.id:
            diaMedio = False

            if solicitudVacaciones.fechaMedioDia != False:
                diaMedio = True

            vacacionesDetail = request.env['contrato.empleado.vacaciones.line.detail'].sudo().search([('masterVacacionesLine_id', '=', solicitudVacaciones.id)])
            vacacionesList = []
            if len(vacacionesDetail) > 0:
                for data in vacacionesDetail:
                    dict ={
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

            vals = {
                'tipo': 'Vacaciones',
                'nombre_empleado': solicitudVacaciones.empleado_id.name,
                'vacacionesList': vacacionesList,
                'txt_razon': solicitudVacaciones.razon,
                'idVacaciones': request.params['idVacaciones'],
            }

            return http.request.render('uia_portal.portal_administrativo_gestion_vacaciones_accion_jefatura_RH',vals)

    @http.route('/set_proceso_accion_vacaciones_jefatura_RH', type='json', auth="user", website=True)
    def set_proceso_accion_vacaciones_jefatura_RH(self,valsJS=None):
        solicitudVacaciones = request.env['contrato.empleado.vacaciones.line'].sudo().search([('id', '=', int(valsJS['id_vacaciones']))])
        ICPSudo = request.env['ir.config_parameter'].sudo()

        solicitudVacaciones.estadoRH = valsJS['accion']
        vals = {}
        if valsJS['accion'] == "Aceptado":
            solicitudVacaciones.fechaFirmaRH = datetime.today() + timedelta(hours=6)
            vals =  {
                'vacacionesId': valsJS['id_vacaciones'],
                'reporte': True,
                'result': True,
            }
        else:
            solicitudVacaciones.contratoEmpleado_id.vacacionesTomadas -= solicitudVacaciones.diasVacaciones
            solicitudVacaciones.contratoEmpleado_id.vacacionesRestantes += solicitudVacaciones.diasVacaciones
            solicitudVacaciones.activo = False
            vals = {
                'result': True,
                'reporte': False,
            }

        template_id = request.env.ref('uia_portal.email_correo_notificacion_vacaciones').id
        template = request.env['mail.template'].browse(template_id)

        email_values = {'email_to': solicitudVacaciones.empleado_id.work_email,
                        'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                        'subject': 'Resolución del proceso de vacaciones.',
                        }
        datosCorreo = {
            'nombre': solicitudVacaciones.contratoEmpleado_id.empleado_id.name,
            'accion': "Aceptada" if valsJS['accion'] == "Aceptado" else "Rechazada",
        }

        template.sudo().with_context(datosCorreo=datosCorreo).send_mail(solicitudVacaciones.id, email_values=email_values,force_send=True)

        return  vals

    @http.route('/set_vacaciones_aprobacion', type='http', auth="user", website=True)
    def set_vacaciones_aprobacion(self, **kw):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])

        if request.env['hr.department'].sudo().search(['&',('manager_id','=',empleado.id),('manager_id','!=',None)]):
            solicitudvacaciones = request.env['contrato.empleado.vacaciones.line'].sudo().search([('id', '=', request.params['idVacaciones'])])
            vals = {
                'idVacaciones': request.params['idVacaciones'],

            }
            return http.request.render('uia_portal.portal_aprobacion_vacaciones', vals)
        else:
            vals = {
                'idVacaciones': 'SinAutorizacion',
            }
            return http.request.render('uia_portal.portal_aprobacion_vacaciones', vals)

    @http.route('/get_vacaciones_aprobacion_info', type='json', auth="user", website=True)
    def get_vacaciones_aprobacion_info(self,idVacaciones=None):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        solicitudvacaciones = request.env['contrato.empleado.vacaciones.line'].sudo().search([('id', '=', idVacaciones)])

        if request.env['hr.department'].sudo().search([('manager_id', '=', empleado.id)]) and solicitudvacaciones.estado == 'En proceso':
            return {
                'razon': solicitudvacaciones.razon,
                'empleado': solicitudvacaciones.empleado_id.name,
                'diasVacaciones': solicitudvacaciones.diasVacaciones,
                'desde': solicitudvacaciones.fechaInicioVacaciones,
                'hasta': solicitudvacaciones.fechaFinVacaciones,
                'aplicado': False
            }
        else:
            if int(request.env['ir.config_parameter'].sudo().get_param('uia_portal.empleado_id')) == empleado.id and solicitudvacaciones.estado == 'Aprobada por Jefatura':
                return {
                    'razon': solicitudvacaciones.razon,
                    'empleado': solicitudvacaciones.empleado_id.name,
                    'diasVacaciones': solicitudvacaciones.diasVacaciones,
                    'desde': solicitudvacaciones.fechaInicioVacaciones,
                    'hasta': solicitudvacaciones.fechaFinVacaciones,
                    'aplicado': False
                }
            else:
                return {
                    'aplicado': True
                }

    @http.route('/set_vacaciones_accion', type='json', auth="user", website=True)
    def set_vacaciones_accion(self,idVacaciones=None,accion=None):

        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        solicitudVacaciones = request.env['contrato.empleado.vacaciones.line'].sudo().search([('id', '=', idVacaciones)])

        if request.env['hr.department'].sudo().search([('manager_id', '=', empleado.id)]) and int(request.env['ir.config_parameter'].sudo().get_param('uia_portal.empleado_id')) != empleado.id:
            if solicitudVacaciones.estado == 'En proceso' and accion == True:
                solicitudVacaciones.estado = 'Aprobada por Jefatura';
                solicitudVacaciones.aceptaionJefatura = True;
                solicitudVacaciones.fechaFirmaJefatura = datetime.today() + timedelta(hours=6)

                jefaturaRH = request.env['hr.employee'].sudo().search([('id', '=', int(request.env['ir.config_parameter'].sudo().get_param('uia_portal.empleado_id')))])
                template_id = request.env.ref('uia_portal.email_correo_aceptacion_vacaciones').id
                template = request.env['mail.template'].browse(template_id)
                email_values = {'email_to': jefaturaRH.work_email,
                                'subject': 'Aprobación de vacaciones de '+solicitudVacaciones.empleado_id.name
                                }
                vacacionesData = {
                    'link': request.env['ir.config_parameter'].sudo().get_param('web.base.url') + "/set_vacaciones_aprobacion?idVacaciones=" + str(idVacaciones),
                    'nombre': empleado.name,
                }

                template.sudo().with_context(vacacionesData=vacacionesData).send_mail(solicitudVacaciones.id, email_values=email_values,force_send=True)

                return {
                    'result': True,
                    'pdfReport': False,
                    'vacacionesId': idVacaciones,
                }

            else:
                solicitudVacaciones.estado = 'Rechazada';
                solicitudVacaciones.aceptaionJefatura = False;
                solicitudVacaciones.activo = False;

                return {
                    'result': True,
                    'pdfReport': False,
                    'vacacionesId': idVacaciones,
                }

        elif int(request.env['ir.config_parameter'].sudo().get_param('uia_portal.empleado_id')) == empleado.id:

            if solicitudVacaciones.estado == 'En proceso' and accion == True:
                solicitudVacaciones.estado = 'Aprobada por Jefatura';
                solicitudVacaciones.aceptaionJefatura = True;
                solicitudVacaciones.fechaFirmaRH = datetime.today() + timedelta(hours=6)
                return {
                    'result': True,
                    'pdfReport': False,
                    'vacacionesId': idVacaciones,
                }

            elif solicitudVacaciones.estado == 'Aprobada por Jefatura' and accion == True:
                solicitudVacaciones.estado = 'Aprobada';
                solicitudVacaciones.aceptaionJefaturaRH = True;
                solicitudVacaciones.fechaFirmaRH = datetime.today() + timedelta(hours=6)
                return {
                    'result': True,
                    'pdfReport': True,
                    'vacacionesId': idVacaciones,
                }
            else:
                solicitudVacaciones.estado = 'Rechazada';
                solicitudVacaciones.aceptaionJefaturaRH = False;
                solicitudVacaciones.activo = False;
                return {
                    'result': True,
                    'pdfReport': False,
                    'vacacionesId': idVacaciones,
                }

    @http.route('/create_report_accion_vacaciones', type='http', auth="user", website=True)
    def create_report_accion_vacaciones(self,**kw):

        solicitudVacaciones = request.env['contrato.empleado.vacaciones.line'].sudo().browse(int(request.params['vacacionesId']))
        datas = {
            'vacacionesid': solicitudVacaciones,
        }

        pdf = request.env.ref('uia_portal.report_accion_personal_vacaciones').sudo()._render_qweb_pdf(solicitudVacaciones.id,data=datas)[0]

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'attachment; filename=' + 'Acción de personal vacaiones ' + solicitudVacaciones.empleado_id.name + '.pdf;')
        ]

        return request.make_response(pdf, headers=pdfhttpheaders)

class GestionVacacioneXAprobar(http.Controller):
    @http.route(['/my/uia_portal_gestion_vacacione_aprobar_jefatura', '/my/home/uia_portal_gestion_vacacione_aprobar_jefatura'], type='http', auth="user", website=True)
    def uia_portal_gestion_vacacione_aprobar_jefatura(self, **kw):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([ ('empleado_id', '=', empleado.id)])
        vals = {}
        valsList=[]
        for contrato in request.env['contrato.empleado'].sudo().search(['|', ('jefaturaInmediata_id', '=', empleado.id), ('jefaturaInmediataDelegado_id', '=', empleado.id)]):

            vacaciones = request.env['contrato.empleado.vacaciones.line'].sudo().search(['&',('estadoJefatura', '!=', 'Aceptado'),('estadoJefatura', '!=', 'Rechazado'), ('contratoEmpleado_id.id', '=', contrato.id)])

            for vacacion in vacaciones:
                inicio = ''
                fin = ''
                for dias in request.env['contrato.empleado.vacaciones.line.detail'].sudo().search([('masterVacacionesLine_id', '=', vacacion.id)]):
                    inicio += str(dias.fechaInicioVacaciones) +'\n'
                    fin += str(dias.fechaFinVacaciones) +'\n'

                dict = {
                    'id': vacacion.id,
                    'nombre': vacaciones.empleado_id.name,
                    'desde': inicio,
                    'hasta':fin,
                }
                valsList.append(dict)
        vals.update({
            'vacacionesDetail': valsList
        })
        return request.render('uia_portal.portal_administrativo_gestion_vacaciones_aprobar_jefatura_home',vals)

class GestionUserPortalIncapacidades(http.Controller):

    @http.route(['/my/uia_portal_gestion_incapacidades', '/my/home/uia_portal_gestion_incapacidades'], type='http', auth="user", website=True)
    def gestionVacaciones(self, **kw):
        return request.render('uia_portal.portal_administrativo_gestion_incapacidades_home',{})

    @http.route('/get_incapacidades_historial', type='json', auth="user", website=True)
    def getVacacionesHistorial(self, **kw):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])
        incapacidadesList = []
        for incapacidades in contrato.incapacidades_ids:
            incapacidadesDict = {
                'fechaInicioIncapacidad': incapacidades.fechaInicioIncapacidad,
                'fechaFinIncapacidad': incapacidades.fechaFinIncapacidad,
                'totalDiasIncapacidad': incapacidades.totalDiasIncapacidad,
                'tipoIncapacidad': incapacidades.tipoIncapacidad,
            }
            incapacidadesList.append(incapacidadesDict)
        return incapacidadesList

    @http.route('/set_incapacidad_solicitud', type='json', auth="user", website=True)
    def setVacacionesSolicitud(self,desde=None,hasta=None,boleta=None,tipo=None):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])

        tipoIncapacidad = tipo
        totalDiasIncapacidad =(datetime.strptime(hasta, "%Y-%m-%d %H:%M:%S") - datetime.strptime(desde, "%Y-%m-%d %H:%M:%S")).days+1

        vals = {
            'contratoEmpleado_id': contrato.id,
            'empleado_id': empleado.id,
            'tipoIncapacidad': tipoIncapacidad,
            'numeroBoletaIncapacidad': boleta,
            'totalDiasIncapacidad': totalDiasIncapacidad,
            'fechaInicioIncapacidad' : datetime.strptime(desde, "%Y-%m-%d %H:%M:%S"),
            'fechaFinIncapacidad' : datetime.strptime(hasta, "%Y-%m-%d %H:%M:%S"),
        }

        if tipoIncapacidad == 'INS':
            vals.update({
                'diasIncapacidadRebajas': totalDiasIncapacidad,
                'diasIncapacidad': 0,
            })
        elif tipoIncapacidad == 'MAT':
            print('dfff')
        else:
            if totalDiasIncapacidad <= 3:
                vals.update({
                    'diasIncapacidadRebajas': 0,
                    'diasIncapacidad': totalDiasIncapacidad,
                })
            else:
                vals.update({
                    'diasIncapacidadRebajas': totalDiasIncapacidad -3,
                    'diasIncapacidad': 3,
                })

        res = request.env['contrato.empleado.incapacidad.line'].sudo().create(vals)

        return 'Incapacidad agregada'

    @http.route('/create_report', type='http', auth="user", website=True)
    def create_report(self,**kw):

        solicitudVacaciones = request.env['contrato.empleado.vacaciones.line'].sudo().browse(int(request.params['vacacionesId']))
        datas = {
            'vacacionesid': solicitudVacaciones,
        }

        pdf = request.env.ref('uia_portal.report_accion_personal_vacaiones').sudo()._render_qweb_pdf(solicitudVacaciones.id,data=datas)[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'attachment; filename=' + 'Acción de personal vacaiones' + solicitudVacaciones.empleado_id.name + '.pdf;')
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

class GestionUserPortalLicencias(http.Controller):

    @http.route(['/my/uia_portal_gestion_licencias', '/my/home/uia_portal_gestion_licencias'], type='http', auth="user", website=True)
    def gestionVacaciones(self, **kw):
        return request.render('uia_portal.portal_administrativo_gestion_licencias_home',{})

    @http.route('/get_licencias_historial', type='json', auth="user", website=True)
    def getVacacionesHistorial(self, **kw):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])
        licenciasList = []
        for licencia in contrato.licencias_ids:
            licenciasDict = {
                'tipoLicencia': licencia.tipoLicencia,
                'fechaInicioLicencia': licencia.fechaInicioLicencia,
                'fechaFinLicencia': licencia.fechaFinLicencia,
                'tipoPago': licencia.tipoPago,
                'estadoJefatura': licencia.estadoJefatura,
                'estadoRH': licencia.estadoRH,
            }
            licenciasList.append(licenciasDict)
        return licenciasList

    @http.route('/get_tipo_licencias', type='json', auth="user", website=True)
    def get_tipo_licencias(self, **kw):
        tipoTicenciasList = []
        tipoTicenciasList.append("Tipos de licencias")
        tipoTicenciasList.append("Sin goce salarial")
        tipoTicenciasList.append("Matrimonio")
        tipoTicenciasList.append("Muerte de un familiar")
        tipoTicenciasList.append("Paternidad")
        tipoTicenciasList.append("Maternidad")

        return {
            'tipoTicencias': tipoTicenciasList
        }

    @http.route('/set_licencia_solicitud', type='json', auth="user", website=True)
    def set_licencia_solicitud(self,valsJS=None):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])
        ICPSudo = request.env['ir.config_parameter'].sudo()

        tipoPago= ""

        if valsJS['tipo_licencia'] == "Sin goce salarial":
            tipoPago = "Sin pago";
        elif valsJS['tipo_licencia'] == "Matrimonio" or valsJS['tipo_licencia'] == "Muerte de un familiar":
            tipoPago = "Pago completo";
        elif valsJS['tipo_licencia'] == "Paternidad" or valsJS['tipo_licencia'] == "Maternidad":
            tipoPago = "Pago medio";

        res = None
        vals = {}
        if valsJS['tipo_licencia'] == "Paternidad":
            diaMinimo = None
            diaMaximo = None
            if int(valsJS['slt_dia_1']) > int(valsJS['slt_dia_2']):
                diaMinimo = int(valsJS['slt_dia_2'])
                diaMaximo = int(valsJS['slt_dia_1'])
            else:
                diaMinimo = int(valsJS['slt_dia_1'])
                diaMaximo = int(valsJS['slt_dia_2'])
            fecha = datetime.strptime(valsJS['slt_anno']+"-"+valsJS['slt_mes']+"-01", "%Y-%m-%d")
            while True:
                if fecha.weekday() == diaMinimo:
                    break
                else:
                    fecha += timedelta(days=1)

            fechaDia_1 = fecha
            fechaDia_2 = fecha + timedelta(days=(diaMaximo - diaMinimo))
            fechaDia_3 = fechaDia_1 + timedelta(weeks=1)
            fechaDia_4 = fechaDia_2 + timedelta(weeks=1)
            fechaDia_5 = fechaDia_3 + timedelta(weeks=1)
            fechaDia_6 = fechaDia_4 + timedelta(weeks=1)
            fechaDia_7 = fechaDia_5 + timedelta(weeks=1)
            fechaDia_8 = fechaDia_6 + timedelta(weeks=1)

            vals = {
                'contratoEmpleado_id': contrato.id,
                'empleado_id': empleado.id,
                'tipoLicencia': valsJS['tipo_licencia'],
                'fechaInicioLicencia': fechaDia_1,
                'fechaFinLicencia': fechaDia_8,
                'tipoPago': tipoPago,
                'razon': valsJS['txt_razon'],
                'fechaFirmaEmpleado': datetime.today() + timedelta(hours=6),
                'fechaPaternidad_1': fechaDia_1,
                'fechaPaternidad_2': fechaDia_2,
                'fechaPaternidad_3': fechaDia_3,
                'fechaPaternidad_4': fechaDia_4,
                'fechaPaternidad_5': fechaDia_5,
                'fechaPaternidad_6': fechaDia_6,
                'fechaPaternidad_7': fechaDia_7,
                'fechaPaternidad_8': fechaDia_8,
            }

            res = contrato.licencias_ids.sudo().create(vals)

        elif valsJS['tipo_licencia'] == "Maternidad":
            fechaInicio = datetime.strptime(valsJS['slt_anno'] + "-" + valsJS['slt_mes'] + "-01", "%Y-%m-%d")
            fechaFin = fechaInicio + relativedelta(months=4)

            vals ={
                'contratoEmpleado_id': contrato.id,
                'empleado_id': empleado.id,
                'tipoLicencia': valsJS['tipo_licencia'],
                'fechaInicioLicencia': fechaInicio.date(),
                'fechaFinLicencia': fechaFin.date(),
                'tipoPago': tipoPago,
                'razon': valsJS['txt_razon'],
                'fechaFirmaEmpleado': datetime.today() + timedelta(hours=6),
            }

            res = contrato.licencias_ids.sudo().create(vals)

        else:

            vals ={
                'contratoEmpleado_id': contrato.id,
                'empleado_id': empleado.id,
                'tipoLicencia': valsJS['tipo_licencia'],
                'fechaInicioLicencia': valsJS['dt_desde'],
                'fechaFinLicencia': valsJS['dt_hasta'],
                'tipoPago': tipoPago,
                'razon': valsJS['txt_razon'],
                'fechaFirmaEmpleado': datetime.today() + timedelta(hours=6),
            }

            res = contrato.licencias_ids.sudo().create(vals)

        template_id = request.env.ref('uia_portal.email_correo_aceptacion_licencia').id
        template = request.env['mail.template'].browse(template_id)

        email_values = {'email_to': contrato.jefaturaInmediata_id.work_email,
                        'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                        'subject': 'Aprobación de licencia de ' + empleado.name,
                        }
        emailData = {
            'link': request.env['ir.config_parameter'].sudo().get_param('web.base.url') + "/set_licencia_aprobacion_jefaturaInmediata?idlicencia=" + str(res.id),
            'nombre': empleado.name,
            'tipoLicencia': valsJS['tipo_licencia'],
            'fechaLicencia': str(vals['fechaInicioLicencia']) + ' ' + str(vals['fechaFinLicencia']),
            'diasList': valsJS['txt_razon'],
            'razon': valsJS['txt_razon'],
        }

        template.sudo().with_context(emailData=emailData).send_mail(res.id, email_values=email_values,force_send=True)

    @http.route('/set_licencia_aprobacion_jefaturaInmediata', type='http', auth="user", website=True)
    def set_licencia_aprobacion_jefaturaInmediata(self,**kw):

        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])

        solicitudLicencia = request.env['contrato.empleado.licencias.line'].sudo().search([('id', '=', int(request.params['idlicencia']))])

        if solicitudLicencia.contratoEmpleado_id.jefaturaInmediata_id.id == empleado.id or solicitudVacaciones.contratoEmpleado_id.jefaturaInmediataDelegado_id.id == empleado.id:
            dataDias = ""
            if solicitudLicencia.tipoLicencia == "Paternidad":
                dataDias += "Semana: 1 "+str(solicitudLicencia.fechaPaternidad_1)+" - "+str(solicitudLicencia.fechaPaternidad_2)+"\n"
                dataDias += "Semana: 2 "+str(solicitudLicencia.fechaPaternidad_3)+" - "+str(solicitudLicencia.fechaPaternidad_4)+"\n"
                dataDias += "Semana: 3 "+str(solicitudLicencia.fechaPaternidad_5)+" - "+str(solicitudLicencia.fechaPaternidad_6)+"\n"
                dataDias += "Semana: 4 "+str(solicitudLicencia.fechaPaternidad_7)+" - "+str(solicitudLicencia.fechaPaternidad_8)+"\n"

            vals = {
                'tipo_licencia': solicitudLicencia.tipoLicencia,
                'nombre_empleado': solicitudLicencia.empleado_id.name,
                'dt_desde': solicitudLicencia.fechaInicioLicencia,
                'dt_hasta': solicitudLicencia.fechaFinLicencia,
                'txt_razon': solicitudLicencia.razon,
                'dataDias': dataDias,
                'idLicencia': request.params['idlicencia'],
            }

            return http.request.render('uia_portal.portal_administrativo_gestion_licencias_accion_jefatura_inmediata',vals)

    @http.route('/set_proceso_accion_licencia_jefatura_inmediata', type='json', auth="user", website=True)
    def set_proceso_accion_licencia_jefatura_inmediata(self,valsJS=None):
        solicitudLicencia = request.env['contrato.empleado.licencias.line'].sudo().search([('id', '=', int(valsJS['id_licencia']))])
        ICPSudo = request.env['ir.config_parameter'].sudo()

        solicitudLicencia.estadoJefatura = valsJS['accion']

        if valsJS['accion'] == "Aceptado":

            solicitudLicencia.fechaFirmaJefatura = datetime.today() + timedelta(hours=6)
            template_id = request.env.ref('uia_portal.email_correo_aceptacion_licencia').id
            template = request.env['mail.template'].browse(template_id)

            email_values = {'email_to': solicitudLicencia.contratoEmpleado_id.jefaturaRH_id.work_email,
                            'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                            'subject': 'Aprobación de licencia de ' + solicitudLicencia.contratoEmpleado_id.empleado_id.name,
                            }
            emailData = {
                'link': request.env['ir.config_parameter'].sudo().get_param('web.base.url') + "/set_licencia_aprobacion_jefaturaRH?idlicencia=" + str(solicitudLicencia.id),
                'nombre': solicitudLicencia.contratoEmpleado_id.empleado_id.name,
                'tipoLicencia': solicitudLicencia.tipoLicencia,
                'fechaLicencia': str(solicitudLicencia.fechaInicioLicencia) + ' ' + str(solicitudLicencia.fechaFinLicencia),
                'razon': solicitudLicencia.razon,
            }

            template.sudo().with_context(emailData=emailData).send_mail(solicitudLicencia.id, email_values=email_values,force_send=True)
            return {
                'result': True,
            }
        else:
            solicitudLicencia.activo = False
            return {
                'result': True,
            }

    @http.route('/set_licencia_aprobacion_jefaturaRH', type='http', auth="user", website=True)
    def set_licencia_aprobacion_jefaturaRH(self,**kw):

        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])

        solicitudLicencia = request.env['contrato.empleado.licencias.line'].sudo().search([('id', '=', int(request.params['idlicencia']))])

        if solicitudLicencia.contratoEmpleado_id.jefaturaRH_id.id == empleado.id:
            dataDias = ""
            if solicitudLicencia.tipoLicencia == "Paternidad":
                dataDias += "Semana: 1 "+str(solicitudLicencia.fechaPaternidad_1)+" - "+str(solicitudLicencia.fechaPaternidad_2)+"\n"
                dataDias += "Semana: 2 "+str(solicitudLicencia.fechaPaternidad_3)+" - "+str(solicitudLicencia.fechaPaternidad_4)+"\n"
                dataDias += "Semana: 3 "+str(solicitudLicencia.fechaPaternidad_5)+" - "+str(solicitudLicencia.fechaPaternidad_6)+"\n"
                dataDias += "Semana: 4 "+str(solicitudLicencia.fechaPaternidad_7)+" - "+str(solicitudLicencia.fechaPaternidad_8)+"\n"
            vals ={
                'tipo_licencia': solicitudLicencia.tipoLicencia,
                'nombre_empleado': solicitudLicencia.empleado_id.name,
                'dt_desde': solicitudLicencia.fechaInicioLicencia,
                'dt_hasta': solicitudLicencia.fechaFinLicencia,
                'dataDias': dataDias,
                'txt_razon': solicitudLicencia.razon,
                'idLicencia': request.params['idlicencia'],
            }

            return http.request.render('uia_portal.portal_administrativo_gestion_licencias_accion_jefatura_RH', vals)

    @http.route('/set_proceso_accion_licencia_jefatura_RH', type='json', auth="user", website=True)
    def set_proceso_accion_licencia_jefatura_RH(self,valsJS=None):
        solicitudLicencia = request.env['contrato.empleado.licencias.line'].sudo().search([('id', '=', int(valsJS['id_licencia']))])
        ICPSudo = request.env['ir.config_parameter'].sudo()

        solicitudLicencia.estadoRH = valsJS['accion']
        vals = {}
        if valsJS['accion'] == "Aceptado":
            solicitudLicencia.fechaFirmaRH = datetime.today() + timedelta(hours=6)
            vals =  {
                'id_licencia': valsJS['id_licencia'],
                'reporte': True,
                'result': True,
            }
        else:
            solicitudLicencia.activo = False
            vals = {
                'result': True,
                'reporte': False,
            }

            template_id = request.env.ref('uia_portal.email_correo_notificacion_licencia').id
            template = request.env['mail.template'].browse(template_id)

            email_values = {'email_to': solicitudLicencia.empleado_id.work_email,
                            'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                            'subject': 'Resolución del proceso de licencia.',
                            }
            datosCorreo = {
                'nombre': solicitudLicencia.contratoEmpleado_id.empleado_id.name,
                'tipoLicencia': solicitudLicencia.tipoLicencia,
                'accion': "Aceptada" if valsJS['accion'] == "Aceptado" else "Rechazada",
            }

            template.sudo().with_context(datosCorreo=datosCorreo).send_mail(solicitudLicencia.id, email_values=email_values,force_send=True)
        return  vals

    @http.route('/create_report_accion_licencia', type='http', auth="user", website=True)
    def create_report(self,**kw):

        solicitudLicencia = request.env['contrato.empleado.licencias.line'].sudo().search([('id', '=', int(request.params['id_licencia']))])
        datas = {
            'solicitudLicencia': solicitudLicencia,
        }

        pdf = request.env.ref('uia_portal.report_accion_personal_licencia').sudo()._render_qweb_pdf(solicitudLicencia.id,data=datas)[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'attachment; filename=' + 'Acción de personal licencia' + solicitudLicencia.empleado_id.name + '.pdf;')
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

class GestionUserPortalTiempoAcumulado(http.Controller):

    @http.route(['/my/uia_portal_gestion_tiempo_acumulado', '/my/home/uia_portal_gestion_tiempo_acumulado'], type='http', auth="user", website=True)
    def gestionTiempoAcumulado(self, **kw):
        return request.render('uia_portal.portal_administrativo_gestion_tiempo_acumulado_home',{})

    @http.route('/get_tiempo_acumulado_info', type='json', auth="user", website=True)
    def getTiempoAcumuladoInfo(self, **kw):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([ ('empleado_id', '=', empleado.id)])

        return {
            'total': contrato.tiempoAcumuladoTotal,
            'tomadas': contrato.tiempoAcumuladoTomado,
            'restantes': contrato.tiempoAcumuladoRestante,
        }

    @http.route('/get_tiempo_acumulado_historial', type='json', auth="user", website=True)
    def get_tiempo_acumulado_historial(self, **kw):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])
        tiempoAcumuladoList = []
        for tiempoAcumulado in contrato.timepoAcumulado_ids:
            tiempoAcumuladoDict = {
                'fechaTiempoAcumulado': tiempoAcumulado.fechaTiempoAcumulado,
                'tiempoAcumuladoTomado': tiempoAcumulado.tiempoAcumuladoTomado,
                'inicioFinJornada': tiempoAcumulado.inicioFinJornada,
                'estado': tiempoAcumulado.estado,
            }
            tiempoAcumuladoList.append(tiempoAcumuladoDict)

        return tiempoAcumuladoList

    @http.route('/set_tiempo_acumulado_solicitud', type='json', auth="user", website=True)
    def set_tiempo_acumulado_solicitud(self,valsJS=None):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])
        ICPSudo = request.env['ir.config_parameter'].sudo()

        totalDiasTiempoCumulado = 0
        totalTiempoCumulado = 0

        fechaDesdeTomaTiempoAcumulado = datetime.strptime(valsJS['dt_desde'], "%Y-%m-%d")
        fechaHastaTomaTiempoAcumulado = datetime.strptime(valsJS['dt_hasta'], "%Y-%m-%d")


        horarioEmpleado = request.env['horario.empleado'].search([('empleado_id', '=', empleado.id)])
        if not horarioEmpleado:
            return 'Usted no tiene horario asignado para  las fechas de peticion de vacaciones'

        while fechaDesdeTomaTiempoAcumulado <= fechaHastaTomaTiempoAcumulado:

            horarioDia = request.env['horario.empleado.line'].search(['&', ('fechaDesde', '<=', fechaDesdeTomaTiempoAcumulado), ('fechaHasta', '>=', fechaDesdeTomaTiempoAcumulado),('horarioEmpleado_id', '=', horarioEmpleado.id)])
            if not horarioDia:
                return 'Usted no tiene horario asignado para  la fecha ' + diaVacaciones.date() + ' de petición de vacaciones'

            if fechaDesdeTomaTiempoAcumulado.weekday() == 0:
                if horarioDia.horaInicioLunes != False:
                    totalDiasTiempoCumulado += 1
                    if 'slt_tiempo' in valsJS:
                        totalTiempoCumulado += int(valsJS['slt_tiempo'])
                    else:
                        totalTiempoCumulado += 600

            elif fechaDesdeTomaTiempoAcumulado.weekday() == 1:
                if horarioDia.horaInicioMartes != False:
                    totalDiasTiempoCumulado += 1
                    if 'slt_tiempo' in valsJS:
                        totalTiempoCumulado += int(valsJS['slt_tiempo'])
                    else:
                        totalTiempoCumulado += 600

            elif fechaDesdeTomaTiempoAcumulado.weekday() == 2:
                if horarioDia.horaInicioMiercoles != False:
                    totalDiasTiempoCumulado += 1
                    if 'slt_tiempo' in valsJS:
                        totalTiempoCumulado += int(valsJS['slt_tiempo'])
                    else:
                        totalTiempoCumulado += 600

            elif fechaDesdeTomaTiempoAcumulado.weekday() == 3:
                if horarioDia.horaInicioJueves != False:
                    totalDiasTiempoCumulado += 1
                    if 'slt_tiempo' in valsJS:
                        totalTiempoCumulado += int(valsJS['slt_tiempo'])
                    else:
                        totalTiempoCumulado += 600

            elif fechaDesdeTomaTiempoAcumulado.weekday() == 4:
                if horarioDia.horaInicioViernes != False:
                    totalDiasTiempoCumulado += 1
                    if 'slt_tiempo' in valsJS:
                        totalTiempoCumulado += int(valsJS['slt_tiempo'])
                    else:
                        totalTiempoCumulado += 600

            elif fechaDesdeTomaTiempoAcumulado.weekday() == 5:
                if horarioDia.horaInicioSabado != False:
                    totalDiasTiempoCumulado += 1
                    if 'slt_tiempo' in valsJS:
                        totalTiempoCumulado += int(valsJS['slt_tiempo'])
                    else:
                        totalTiempoCumulado += 600

            elif fechaDesdeTomaTiempoAcumulado.weekday() == 6:
                if horarioDia.horaInicioDomingo != False:
                    totalDiasTiempoCumulado += 1
                    if 'slt_tiempo' in valsJS:
                        totalTiempoCumulado += int(valsJS['slt_tiempo'])
                    else:
                        totalTiempoCumulado += 600

            fechaDesdeTomaTiempoAcumulado += timedelta(days=1)


        if totalTiempoCumulado <= contrato.tiempoAcumuladoRestante:
            fechaFirma = datetime.today() + timedelta(hours=6)
            vals = {
                'contratoEmpleado_id': contrato.id,
                'empleado_id': empleado.id,
                'fechaDesdeTiempoAcumulado': valsJS['dt_desde'],
                'fechaHastaTiempoAcumulado': valsJS['dt_hasta'],
                'tiempoAcumuladoTomado': str(totalTiempoCumulado/60)+'h',
                'diasAcumuladoTomado': totalDiasTiempoCumulado,
                'inicioFinJornada': valsJS['slt_jornada'] if 'slt_jornada' in valsJS else 'Rango de Fechas',
                'peticion': True,
                'razon': valsJS['txt_razon'],
                'fechaFirmaEmpleado': fechaFirma,
            }

            res = request.env['contrato.empleado.tiempo.acumulado.line'].sudo().create(vals)
            contrato.tiempoAcumuladoTomado += totalTiempoCumulado
            contrato.tiempoAcumuladoRestante -= totalTiempoCumulado

            template_id = request.env.ref('uia_portal.email_correo_aceptacion_tiempoAcumulado').id
            template = request.env['mail.template'].browse(template_id)
            email_values = {'email_to': res.contratoEmpleado_id.jefaturaInmediata_id.work_email,
                            'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                            'subject': 'Aprobación de tiempo acumulado de '+empleado.name,
                            }
            datosCorreo = {
                'link': request.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/set_tiempo_acumulado_aprobacion_jefatura_inmediata?idTiempoAcumulado="+str(res.id),
                'nombre': empleado.name,
                'jefatura': contrato.jefaturaInmediata_id.name,
            }
            template.sudo().with_context(datosCorreo=datosCorreo).send_mail(res.id, email_values=email_values, force_send=True)

            return 'Solicitud de tiempo acumulado creada'
        else:
            return 'La cantidad de tiempo acumulado supera las que tiene a disposición'

    @http.route('/set_tiempo_acumulado_aprobacion_jefatura_inmediata', type='http', auth="user", website=True)
    def set_tiempo_acumulado_aprobacion_jefatura_inmediata(self, **kw):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&', ('department_id.name', '!=', 'Docentes'), ('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])

        solicitudTiempoAcumulado= request.env['contrato.empleado.tiempo.acumulado.line'].sudo().search([('id', '=', int(request.params['idTiempoAcumulado']))])

        if solicitudTiempoAcumulado.contratoEmpleado_id.jefaturaInmediata_id.id == empleado.id or solicitudVacaciones.contratoEmpleado_id.jefaturaInmediataDelegado_id.id == empleado.id:
            diaMedio = False

            if solicitudTiempoAcumulado.inicioFinJornada != False:
                diaMedio = True

            vals = {
                'tipo': 'Tiempo Acumulado',
                'nombre_empleado': solicitudTiempoAcumulado.empleado_id.name,
                'dt_desde': solicitudTiempoAcumulado.fechaDesdeTiempoAcumulado,
                'dt_hasta': solicitudTiempoAcumulado.fechaHastaTiempoAcumulado,
                'tiempoAcumuladoTomado': solicitudTiempoAcumulado.tiempoAcumuladoTomado,
                'tipoMedioDia': solicitudTiempoAcumulado.inicioFinJornada,
                'txt_razon': solicitudTiempoAcumulado.razon,
                'idTiempoAcumulado': request.params['idTiempoAcumulado'],
            }

            return http.request.render('uia_portal.portal_administrativo_gestion_tiempo_acumulado_accion_jefatura_inmediata',vals)

    @http.route('/set_proceso_accion_tiempo_acumulado_jefatura_inmediata', type='json', auth="user", website=True)
    def set_proceso_accion_tiempo_acumulado_jefatura_inmediata(self,valsJS=None):
        solicitudTiempoAcumulado = request.env['contrato.empleado.tiempo.acumulado.line'].sudo().search([('id', '=', int(valsJS['id_tiempo_acumulado']))])
        ICPSudo = request.env['ir.config_parameter'].sudo()
        solicitudTiempoAcumulado.estadoJefatura = valsJS['accion']

        if valsJS['accion'] == "Aceptado":

            solicitudTiempoAcumulado.fechaFirmaJefatura = datetime.today() + timedelta(hours=6)
            template_id = request.env.ref('uia_portal.email_correo_aceptacion_tiempoAcumulado').id
            template = request.env['mail.template'].browse(template_id)

            email_values = {
                'email_to': solicitudTiempoAcumulado.contratoEmpleado_id.jefaturaRH_id.work_email,
                'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                'subject': 'Aprobación de tiempo acumulado de ' + solicitudTiempoAcumulado.contratoEmpleado_id.empleado_id.name,
            }

            datosCorreo = {
                'link': request.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/set_tiempo_acumulado_aprobacion_jefaturaRH?idTiempoAcumulado="+str(solicitudTiempoAcumulado.id),
                'nombre': solicitudTiempoAcumulado.contratoEmpleado_id.empleado_id.name,
                'jefatura': solicitudTiempoAcumulado.contratoEmpleado_id.jefaturaRH_id.name,
            }

            template.sudo().with_context(datosCorreo=datosCorreo).send_mail(solicitudTiempoAcumulado.id, email_values=email_values,force_send=True)
            return {
                'result': True,
            }
        else:
            solicitudTiempoAcumulado.contratoEmpleado_id.tiempoAcumuladoTomado -= solicitudTiempoAcumulado.tiempoAcumuladoTomado
            solicitudTiempoAcumulado.contratoEmpleado_id.tiempoAcumuladoRestante += solicitudTiempoAcumulado.tiempoAcumuladoTomado
            solicitudVacaciones.activo = False
            return {
                'result': True,
            }

    @http.route('/set_tiempo_acumulado_aprobacion_jefaturaRH', type='http', auth="user", website=True)
    def set_tiempo_acumulado_aprobacion_jefaturaRH(self, **kw):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&', ('department_id.name', '!=', 'Docentes'), ('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])

        solicitudTiempoAcumulado= request.env['contrato.empleado.tiempo.acumulado.line'].sudo().search([('id', '=', int(request.params['idTiempoAcumulado']))])

        if solicitudTiempoAcumulado.contratoEmpleado_id.jefaturaRH_id.id == empleado.id:
            diaMedio = False

            if solicitudTiempoAcumulado.inicioFinJornada != False:
                diaMedio = True

            vals = {
                'tipo': 'Tiempo Acumulado',
                'nombre_empleado': solicitudTiempoAcumulado.empleado_id.name,
                'dt_desde': solicitudTiempoAcumulado.fechaDesdeTiempoAcumulado,
                'dt_hasta': solicitudTiempoAcumulado.fechaHastaTiempoAcumulado,
                'tiempoAcumuladoTomado': solicitudTiempoAcumulado.tiempoAcumuladoTomado,
                'tipoMedioDia': solicitudTiempoAcumulado.inicioFinJornada,
                'txt_razon': solicitudTiempoAcumulado.razon,
                'idTiempoAcumulado': request.params['idTiempoAcumulado'],
            }

            return http.request.render('uia_portal.portal_administrativo_gestion_tiempo_acumulado_accion_jefatura_RH',vals)

    @http.route('/set_proceso_accion_tiempo_acumulado_jefatura_RH', type='json', auth="user", website=True)
    def set_proceso_accion_tiempo_acumulado_jefatura_RH(self,valsJS=None):
        solicitudTiempoAcumulado = request.env['contrato.empleado.tiempo.acumulado.line'].sudo().search([('id', '=', int(valsJS['id_tiempo_acumulado']))])
        ICPSudo = request.env['ir.config_parameter'].sudo()
        solicitudTiempoAcumulado.estadoRH = valsJS['accion']
        vals = {}
        if valsJS['accion'] == "Aceptado":
            solicitudTiempoAcumulado.fechaFirmaRH = datetime.today() + timedelta(hours=6)
            vals =  {
                'idTiempoAcumulado': valsJS['id_tiempo_acumulado'],
                'reporte': True,
                'result': True,
            }
        else:
            solicitudTiempoAcumulado.contratoEmpleado_id.tiempoAcumuladoTomado -= solicitudTiempoAcumulado.tiempoAcumuladoTomado
            solicitudTiempoAcumulado.contratoEmpleado_id.tiempoAcumuladoRestante += solicitudTiempoAcumulado.tiempoAcumuladoTomado
            solicitudTiempoAcumulado.activo = False
            vals = {
                'result': True,
                'reporte': False,
            }

        template_id = request.env.ref('uia_portal.email_correo_notificacion_tiempo_acumulado').id
        template = request.env['mail.template'].browse(template_id)

        email_values = {'email_to': solicitudTiempoAcumulado.empleado_id.work_email,
                        'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                        'subject': 'Resolución del proceso de tiempo acumulado.',
                        }
        datosCorreo = {
            'nombre': solicitudTiempoAcumulado.contratoEmpleado_id.empleado_id.name,
            'accion': "Aceptada" if valsJS['accion'] == "Aceptado" else "Rechazada",
        }

        template.sudo().with_context(datosCorreo=datosCorreo).send_mail(solicitudTiempoAcumulado.id, email_values=email_values,force_send=True)

        return  vals

    @http.route('/get_tiempo_acumulado_aprobacion_info', type='json', auth="user", website=True)
    def get_tiempo_acumulado_aprobacion_info(self,idTiempoAcumulado=None):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        solicitudTiempoAcumulado = request.env['contrato.empleado.tiempo.acumulado.line'].sudo().search([('id', '=', idTiempoAcumulado)])

        jornada = 'Fin de jornada'
        if solicitudTiempoAcumulado.inicioFinJornada == 'finJornada':
            jornada = 'Inicio de jornada'

        if request.env['hr.department'].sudo().search([('manager_id', '=', empleado.id)]) and solicitudTiempoAcumulado.estado == 'En proceso':

            return {
                'razon': solicitudTiempoAcumulado.razon,
                'empleado': solicitudTiempoAcumulado.empleado_id.name,
                'tiempoAcumuladoTomado': solicitudTiempoAcumulado.tiempoAcumuladoTomado/60,
                'fechaTiempoAcumulado': solicitudTiempoAcumulado.fechaTiempoAcumulado,
                'inicioFinJornada': jornada,
                'aplicado': False
            }
        else:
            if int(request.env['ir.config_parameter'].sudo().get_param('uia_portal.empleado_id')) == empleado.id and solicitudTiempoAcumulado.estado == 'Aprobada por Jefatura':
                return {
                    'razon': solicitudTiempoAcumulado.razon,
                    'empleado': solicitudTiempoAcumulado.empleado_id.name,
                    'tiempoAcumuladoTomado': solicitudTiempoAcumulado.tiempoAcumuladoTomado/60,
                    'fechaTiempoAcumulado': solicitudTiempoAcumulado.fechaTiempoAcumulado,
                    'inicioFinJornada': jornada,
                    'aplicado': False
                }
            else:
                return {
                    'aplicado': True
                }

    @http.route('/create_report_tiempo_acumulado', type='http', auth="user", website=True)
    def create_report_tiempo_acumulado(self,**kw):

        solicitudTiempoAcumulado = request.env['contrato.empleado.tiempo.acumulado.line'].sudo().browse(int(request.params['idTiempoAcumulado']))
        datas = {
            'idTiempoAcumulado': solicitudTiempoAcumulado,
        }

        pdf = request.env.ref('uia_portal.report_accion_personal_tiempo_acumulado').sudo()._render_qweb_pdf(solicitudTiempoAcumulado.id,data=datas)[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'attachment; filename=' + 'Acción de personal Tiempo Acumulado' + solicitudTiempoAcumulado.empleado_id.name + '.pdf;')
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

class GestionUserPortalJustificacionMarcas(http.Controller):

    @http.route(['/my/uia_portal_gestion_justificaciones_marca', '/my/home/uia_portal_gestion_justificaciones_marca'], type='http', auth="user", website=True)
    def gestionJustificacionesMarca(self, **kw):
        return request.render('uia_portal.portal_administrativo_gestion_justificaciones_marca',{})

    @http.route('/get_docente_justificaciones_marca', type='json', auth="user", website=True)
    def get_docente_justificaciones_marca(self,cedulaDocente=None):
        docentes = request.env['hr.employee'].sudo().search([('department_id.name', '=', 'Docentes')])
        docente = None
        vals = {}
        for data in docentes:
            if data.identification_id != False:
                cedDocente = data.identification_id.replace("-", "")
                if cedDocente == str(cedulaDocente).replace("-", ""):
                    docente = data

        if docente:
            vals.update({
                'encontrado': True,
                'docenteNombre': docente.name,
            })
        else:
            vals.update({
                'encontrado': False,
            })

        return vals

    @http.route('/get_cursos_docente_justificaciones_marca', type='json', auth="user", website=True)
    def get_cursos_docente_justificaciones_marca(self,fechaCurso=None,cedulaDocente=None,anno=None,periodo=None):
        docentes = request.env['hr.employee'].sudo().search([('department_id.name', '=', 'Docentes')])
        fechaCurso = datetime.strptime(fechaCurso, "%Y-%m-%d %H:%M:%S")
        docente = None
        vals = {}
        cuatrimestre = request.env['periodo.cuatrimestre'].sudo().search(['&', ('year', '=', str(anno)), ('decripcion', '=', str(periodo))])
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])


        if datetime.today().date() >= cuatrimestre.fechaInicioPrimerPago and datetime.today().date() <= cuatrimestre.fechaFinPrimerPago + timedelta(days=3):
            if fechaCurso.date() >= cuatrimestre.fechaInicioPrimerPago and fechaCurso.date() <= cuatrimestre.fechaFinPrimerPago + timedelta(days=3):
                vals.update({
                    'estadoFecha': 'OK',
                    'pagoMarca': 'Primer Pago',
                })
            else:
                return {
                    'encontrado': True,
                    'estadoFecha': 'NOT',
                    'rangoJustificacion': ' del ' + str(cuatrimestre.fechaInicioPrimerPago) + ' al ' + str(cuatrimestre.fechaFinPrimerPago + timedelta(days=3))
                }

        elif datetime.today().date() >= cuatrimestre.fechaInicioSegundoPago and datetime.today().date() <= cuatrimestre.fechaFinSegundoPago + timedelta(days=3):
            if fechaCurso.date() >= cuatrimestre.fechaInicioSegundoPago and fechaCurso.date() <= cuatrimestre.fechaFinSegundoPago + timedelta(days=3):
                vals.update({
                    'estadoFecha': 'OK',
                    'pagoMarca': 'Segundo Pago',
                })
            else:
                return {
                    'encontrado': True,
                    'estadoFecha': 'NOT',
                    'rangoJustificacion': ' del ' + str(cuatrimestre.fechaInicioSegundoPago) + ' al ' + str(cuatrimestre.fechaFinSegundoPago + timedelta(days=3))
                }

        elif datetime.today().date() >= cuatrimestre.fechaInicioTercerPago and datetime.today().date() <= cuatrimestre.fechaFinTercerPago + timedelta(days=3):
            if fechaCurso.date() >= cuatrimestre.fechaInicioTercerPago and fechaCurso.date() <= cuatrimestre.fechaFinTercerPago + timedelta(days=3):
                vals.update({
                    'estadoFecha': 'OK',
                    'pagoMarca': 'Tercer Pago',
                })
            else:

                return {
                    'encontrado': True,
                    'estadoFecha': 'NOT',
                    'rangoJustificacion': ' del '+str(cuatrimestre.fechaInicioTercerPago) + ' al ' + str( cuatrimestre.fechaFinTercerPago + timedelta(days=3))
                }

        if user.login == 'aguilleno@uia.ac.cr' or user.login == 'ggamboaf@uia.ac.cr':
            vals.update({
                'estadoFecha': 'OK',
                'pagoMarca': 'Tercer Pago',
            })
        for data in docentes:
            if data.identification_id != False:
                cedDocente = data.identification_id.replace("-", "")
                if cedDocente == str(cedulaDocente).replace("-", ""):
                    docente = data

        cursosDocentes = request.env['cursos.docente'].sudo().search(['&',('docente_id','=',docente.id),('cuatrimestre_id', '=', cuatrimestre.id)])

        dia = any

        if fechaCurso.weekday() == 0:
            dia = 'L'
        elif fechaCurso.weekday() == 1:
            dia = 'K'
        elif fechaCurso.weekday() == 2:
            dia = 'M'
        elif fechaCurso.weekday() == 3:
            dia = 'J'
        elif fechaCurso.weekday() == 4:
            dia = 'V'
        elif fechaCurso.weekday() == 5:
            dia = 'S'
        elif fechaCurso.weekday() == 6:
            dia = 'D'

        listCursos = list(filter(lambda x: (x.dia1 == dia) and
                                           (x.cursoActivo == True)  ,cursosDocentes.cursos_lines_ids))
        listCurso = []

        for data in listCursos:
            if type(data.fechaCambioCurso) is bool and type(data.fechaInicioPago) is bool :
                listCurso.append({
                    'id':data.id,
                    'horarioCurso':data.horario,
                    'codigoCurso':data.codigoCurso,
                })
            elif type(data.fechaCambioCurso) is bool:
                if fechaCurso.date() >= data.fechaInicioPago :
                    listCurso.append({
                        'id': data.id,
                        'horarioCurso': data.horario,
                        'codigoCurso': data.codigoCurso,
                    })
            elif type(data.fechaInicioPago) is bool:
                if fechaCurso.date() <=  data.fechaCambioCurso:
                    listCurso.append({
                        'id': data.id,
                        'horarioCurso': data.horario,
                        'codigoCurso': data.codigoCurso,
                    })

        if listCursos:
            vals.update({
                'encontrado': True,
                'listCursos': listCurso,
            })
        else:
            vals.update({
                'encontrado': False,
            })

        return vals

    @http.route('/set_cursos_docente_justificaciones_marca', type='json', auth="user", website=True)
    def set_cursos_docente_justificaciones_marca(self,cursosJustificacion=None,fechaCurso=None,pagoMarca=None):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        ICPSudo = request.env['ir.config_parameter'].sudo()
        fecha = datetime.strptime(fechaCurso, "%Y-%m-%d %H:%M:%S")

        datosCorreo = []
        correoDocente = ''
        for data in cursosJustificacion:
            curso = request.env['cursos.docente.line'].sudo().search([('id','=',data)])
            correoDocente= curso.docente_id.work_email
            asistenciaLine = request.env['asistencia.docente.line'].sudo().search(['&', ('asistencia_id', '=', curso.cursos_id.id), ('docente_id', '=', curso.docente_id.id)])

            vals = {
                'docente_id': curso.docente_id.id,
                'cuatrimestre_id': curso.cuatrimestre_id.id,
                'asistencia_id': curso.cursos_id.id,
                'aplicar': True,
                'cursoMarca': curso.codigoCurso,
                'fechaCurso': fecha.date(),
                'horarioCurso': curso.horario,
                'entradaClases': datetime.strptime(str(fecha.date())+' '+str(curso.horaInicio)+':'+str(curso.minutoInicio)+':00',"%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                'salidaClases':  datetime.strptime(str(fecha.date())+' '+str(curso.horaFinal)+':'+str(curso.minutoFinal)+':00',"%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                'tiempoClases': curso.cantiadadHoras,
                'deduccionEntradaTardia': 0,
                'deduccionSalidaTemprana': 0,
                'deduccionOmisionMarca': 0,
                'deduccionAusencia': 0,
                'deduccionTotal': 0,
                'marcaJustificada': True,
                'empleadoJustificacion': empleado.id,
                'pagoMarca': pagoMarca,
                'estado': 'OK'
            }
            datosCorreo.append({
                'docenteNombre':curso.docente_id.name,
                'codigoCurso':curso.codigoCurso,
                'horarioCurso':curso.horario,
                'fechaJustificacion':fecha,
            })
            asistencia = list(filter(lambda x: (x.docente_id.id == curso.docente_id.id) and
                                               (x.cuatrimestre_id.id == curso.cuatrimestre_id.id) and
                                               (x.cursoMarca == curso.codigoCurso) and
                                               (x.horarioCurso == curso.horario) and
                                               (x.fechaCurso == fecha.date()), asistenciaLine))
            idAsistencia = None
            if asistencia:
                request.env['asistencia.docente.line'].browse(asistencia[0].id).sudo().write(vals)
                idAsistencia = asistencia[0].id
            else:
                idAsistencia = request.env['asistencia.docente.line'].sudo().create(vals)

        template_id = request.env.ref('uia_portal.email_correo_justificacion_marcas').id
        template = request.env['mail.template'].browse(template_id)
        email_values = {'email_to': user.login,
                        'email_cc': correoDocente,
                        'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                        'subject': 'Justificación de Marcas'
                        }

        template.sudo().with_context(datosCorreo=datosCorreo).send_mail(1,email_values=email_values,force_send=True)

        return {
            'estado': 'Justificación aplicada correctamente'
        }

class GestionUserPortalCargarAdicionales(http.Controller):

    @http.route(['/my/uia_portal_cargar_adicionales', '/my/home/uia_portal_cargar_adicionales'], type='http', auth="user", website=True)
    def gestionJustificacionesMarca(self, **kw):
        return request.render('uia_portal.portal_administrativo_cargar_adicionales',{})

    @http.route('/get_docente_carga_adicionales', type='json', auth="user", website=True)
    def get_docente_carga_adicionales(self,cedulaDocente=None):
        docentes = request.env['hr.employee'].sudo().search([('department_id.name', '=', 'Docentes')])
        vals = {}
        docente =  list(filter(lambda x: (str(x.identification_id).replace("-", "") == str(cedulaDocente).replace("-", "") ),docentes))
        if docente:
            listAdicionales = []
            for data in request.env['configuraciones.adicionales.line'].sudo().search([]):
                adicionalesDict = {
                    'nombre': data.name,
                    'id': data.id
                }
                listAdicionales.append(adicionalesDict)

            vals.update({
                'encontrado': True,
                'docenteNombre': docente[0].name,
                'adicionalesList': listAdicionales
            })
        else:
            vals.update({
                'encontrado': False,
            })

        return vals

    @http.route('/set_cargar_adicional', type='json', auth="user", website=True)
    def set_cargar_adicional(self,fechaAdicional=None,identificacionDocente=None,tipoAdicional=None,cantidad=None,periodo=None,anno=None):
        docentes = request.env['hr.employee'].sudo().search([('department_id.name', '=', 'Docentes')])
        user = request.env['res.users'].sudo().browse(request.uid)
        ICPSudo = request.env['ir.config_parameter'].sudo()
        fecha = datetime.strptime(fechaAdicional, "%Y-%m-%d %H:%M:%S")

        docente = list(filter(lambda x: (str(x.identification_id).replace("-", "") == str(identificacionDocente).replace("-", "")),docentes))

        cuatrimestre = request.env['periodo.cuatrimestre'].sudo().search(['&', ('year', '=', anno), ('decripcion', '=', periodo)])
        if not cuatrimestre:
            return {
                'estado': 'El Cuatrimestre aún no ha sido creado'
            }

        cursosDocente = request.env['cursos.docente'].sudo().search(['&', ('docente_id', '=', docente[0].id), ('cuatrimestre_id', '=', cuatrimestre.id)])

        adicional = request.env['configuraciones.adicionales.line'].sudo().search([('id', '=', int(tipoAdicional))])

        vals = {'adicionalId': adicional.id,
                'name': adicional.name,
                'sinPrestaciones': adicional.montoSinPrestaciones,
                'cantidad': float(cantidad),
                'totalAdicionales': adicional.montoSinPrestaciones * float(cantidad),
                'cuatrimestre_id': cursosDocente.cuatrimestre_id.id,
                'docente_id': cursosDocente.docente_id.id,
                'adicionales_id': cursosDocente.id,
                'pagoEfectuado': False,
                'fechaAdicional': fecha.date()
                }

        miembros = cursosDocente.adicionales_lines_ids
        adicionalesDocente = list(filter(lambda x: (x.docente_id.id == vals['docente_id']) and
                                                   (x.cuatrimestre_id.id == vals['cuatrimestre_id']) and
                                                   (x.name == vals['name']) and
                                                   (x.cantidad == vals['cantidad']) and
                                                   (x.fechaAdicional == vals['fechaAdicional']) and
                                                   (x.adicionales_id.id == cursosDocente.id), miembros))

        if adicionalesDocente:
            miembros.browse(adicionalesDocente[0].id).sudo().write(vals)
            return {
                'estado': 'No se pudo agregar el adicional por qué ya existe '
            }
        else:
            miembros.sudo().create(vals)

        datosCorreo = {
            'docenteNombre': docente[0].name,
            'fechaAdicional': fecha.date(),
            'cantidad': cantidad,
            'monto': '₡ '+"{:,}".format(adicional.montoSinPrestaciones * float(cantidad)),
        }

        template_id = request.env.ref('uia_portal.email_correo_carga_adicionales').id
        template = request.env['mail.template'].browse(template_id)
        email_values = {'email_to': user.login,
                        'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                        'subject': 'Carga de Adicional de Pago'
                        }

        template.sudo().with_context(datosCorreo=datosCorreo).send_mail(1,email_values=email_values,force_send=True)

        return {
            'estado': 'Carga Existosa del Adicional '
        }

class GestionUserPortalCargarAjustesPago(http.Controller):

    @http.route(['/my/uia_portal_cargar_ajustes_pago', '/my/home/uia_portal_cargar_ajustes_pago'], type='http', auth="user", website=True)
    def gestionJustificacionesMarca(self, **kw):
        return request.render('uia_portal.portal_administrativo_cargar_ajustes_pago',{})

    @http.route('/get_docente_carga_ajustes_pago', type='json', auth="user", website=True)
    def get_docente_carga_ajustes_pago(self,cedulaDocente=None):
        docentes = request.env['hr.employee'].sudo().search([('department_id.name', '=', 'Docentes')])
        vals = {}
        docente =  list(filter(lambda x: (str(x.identification_id).replace("-", "") == str(cedulaDocente).replace("-", "") ),docentes))
        if docente:
            listAdicionales = []
            for data in request.env['configuraciones.ajuste.pago.line'].sudo().search([]):
                adicionalesDict = {
                    'nombre': data.name,
                    'id': data.id
                }
                listAdicionales.append(adicionalesDict)

            vals.update({
                'encontrado': True,
                'docenteNombre': docente[0].name,
                'adicionalesList': listAdicionales
            })
        else:
            vals.update({
                'encontrado': False,
            })

        return vals

    @http.route('/set_cargar_ajustes_pago', type='json', auth="user", website=True)
    def set_cargar_ajustes_pago(self,fechaAdicional=None,identificacionDocente=None,tipoAdicional=None,monto=None,periodo=None,anno=None,descripcion=None):
        docentes = request.env['hr.employee'].sudo().search([('department_id.name', '=', 'Docentes')])
        user = request.env['res.users'].sudo().browse(request.uid)
        empleado = request.env['hr.employee'].sudo().search(['&', ('department_id.name', '!=', 'Docentes'), ('work_email', '=', user.login)])
        ICPSudo = request.env['ir.config_parameter'].sudo()
        fecha = datetime.strptime(fechaAdicional, "%Y-%m-%d %H:%M:%S")

        docente = list(filter(lambda x: (str(x.identification_id).replace("-", "") == str(identificacionDocente).replace("-", "")),docentes))

        cuatrimestre = request.env['periodo.cuatrimestre'].sudo().search(['&', ('year', '=', anno), ('decripcion', '=', periodo)])
        if not cuatrimestre:
            return {
                'estado': 'El Cuatrimestre aún no ha sido creado'
            }

        cursosDocente = request.env['cursos.docente'].sudo().search(['&', ('docente_id', '=', docente[0].id), ('cuatrimestre_id', '=', cuatrimestre.id)])

        ajuste = request.env['configuraciones.ajuste.pago.line'].sudo().search([('id', '=', int(tipoAdicional))])

        vals = {
            'ajuste_id': ajuste.id,
            'name': ajuste.name,
            'monto': float(monto),
            'horas': 0,
            'minutos': 0,
            'cuatrimestre_id': cuatrimestre.id,
            'docente_id': docente[0].id,
            'descripcion': descripcion,
            'total': float(monto) /  request.env['configuraciones'].sudo().search([]).factor,
            'autoriza_id': empleado.id,
            'fechaAjuste': fecha.date(),
            'ajustes_id': cursosDocente.id,
            'pagoEfectuado': False
        }

        miembros = cursosDocente.ajustes_lines_ids
        ajustesDocente = list(filter(lambda x:     (x.docente_id.id == vals['docente_id']) and
                                                   (x.cuatrimestre_id.id == vals['cuatrimestre_id']) and
                                                   (x.name == vals['name']) and
                                                   (x.monto == vals['monto']) and
                                                   (x.fechaAjuste == vals['fechaAjuste']) and
                                                   (x.ajustes_id.id == cursosDocente.id), miembros))

        if ajustesDocente:
            miembros.browse(ajustesDocente[0].id).sudo().write(vals)
            return {
                'estado': 'No se pudo agregar el ajsute por qué ya existe '
            }
        else:
            miembros.sudo().create(vals)

        datosCorreo = {
            'docenteNombre': docente[0].name,
            'fechaAjuste': fecha.date(),
            'monto':  '₡ '+"{:,}".format(float(monto)),
            'descripcion': descripcion,
        }

        template_id = request.env.ref('uia_portal.email_correo_carga_ajuste_pago').id
        template = request.env['mail.template'].browse(template_id)
        email_values = {'email_to': user.login,
                        'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                        'subject': 'Carga de Ajuste de Pago'
                        }

        template.sudo().with_context(datosCorreo=datosCorreo).send_mail(1,email_values=email_values,force_send=True)

        return {
            'estado': 'Carga Existosa del Ajuste '
        }