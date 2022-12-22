# -*- coding: utf-8 -*-
import io
from odoo.tools.misc import xlsxwriter
from PyPDF2 import PdfFileReader, PdfFileWriter

from odoo import http
from odoo.http import content_disposition, request
from datetime import date, timedelta, datetime
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

        return {
            'justifica': request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)]).justificaMarca,
            'adicionales': request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)]).cargaAdicionales,
            'ajustes': request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)]).cargaAjustes,
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
            vacacionesDict = {
                'fechaInicioVacaciones': vacaciones.fechaInicioVacaciones,
                'fechaFinVacaciones': vacaciones.fechaFinVacaciones,
                'diasVacaciones': vacaciones.diasVacaciones,
                'estado': vacaciones.estado,
            }
            vacacionesList.append(vacacionesDict)
        return vacacionesList

    @http.route('/set_vacaciones_solicitud', type='json', auth="user", website=True)
    def setVacacionesSolicitud(self,desde=None,hasta=None,razon=None):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])

        fechaInicioVacaciones = datetime.strptime(desde, "%Y-%m-%d %H:%M:%S")
        fechaFinVacaciones = datetime.strptime(hasta, "%Y-%m-%d %H:%M:%S")
        totalVacaciones = 0
        diaVacaciones = fechaInicioVacaciones

        horarioEmpleado = request.env['horario.empleado'].search([('empleado_id', '=', empleado.id)])
        if not horarioEmpleado:
            return 'Usted no tiene horario asignado para  las fechas de peticion de vacaciones'

        while diaVacaciones <= fechaFinVacaciones:

            horarioDia = request.env['horario.empleado.line'].search(['&', ('fechaDesde', '<=', diaVacaciones), ('fechaHasta', '>=', diaVacaciones),('horarioEmpleado_id', '=', horarioEmpleado.id)])
            if not horarioDia:
                return 'Usted no tiene horario asignado para  las fechas de petición de vacaciones'

            if diaVacaciones.weekday() == 0:
                if horarioDia.horaInicioLunes != False:
                    totalVacaciones += 1

            elif diaVacaciones.weekday() == 1:
                if horarioDia.horaInicioMartes != False:
                    totalVacaciones += 1

            elif diaVacaciones.weekday() == 2:
                if horarioDia.horaInicioMiercoles != False:
                    totalVacaciones += 1

            elif diaVacaciones.weekday() == 3:
                if horarioDia.horaInicioJueves != False:
                    totalVacaciones += 1

            elif diaVacaciones.weekday() == 4:
                if horarioDia.horaInicioViernes != False:
                    totalVacaciones += 1

            elif diaVacaciones.weekday() == 5:
                if horarioDia.horaInicioSabado != False:
                    totalVacaciones += 1

            elif diaVacaciones.weekday() == 6:
                if horarioDia.horaInicioDomingo != False:
                    totalVacaciones += 1

            diaVacaciones += timedelta(days=1)

        if totalVacaciones <= contrato.vacacionesRestantes:
            fechaFirma = datetime.today() + timedelta(hours=6)
            vals = {
                'contratoEmpleado_id': contrato.id,
                'empleado_id': empleado.id,
                'fechaInicioVacaciones': fechaInicioVacaciones.date(),
                'fechaFinVacaciones': fechaFinVacaciones.date(),
                'diasVacaciones': totalVacaciones,
                'estado': 'En proceso',
                'peticion': True,
                'aceptaionJefatura': False,
                'aceptaionJefaturaRH': False,
                'razon': razon,
                'fechaFirmaEmpleado': datetime.today() + timedelta(hours=6),
            }

            res = request.env['contrato.empleado.vacaciones.line'].sudo().create(vals)
            contrato.vacacionesTomadas += totalVacaciones
            contrato.vacacionesRestantes -= totalVacaciones

            template_id = request.env.ref('uia_portal.email_correo_aceptacion_vacaciones').id
            template = request.env['mail.template'].browse(template_id)
            email_values = {'email_to': empleado.department_id.manager_id.work_email,
                            'subject': 'Aprobación de vacaciones de '+empleado.name,
                            }
            vacacionesData = {
                'link': request.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/set_vacaciones_aprobacion?idVacaciones="+str(res.id),
                'nombre': empleado.name,
                'totalVacaciones': totalVacaciones,
                'fechasVacaciones': str(fechaInicioVacaciones.date())+' '+str(fechaFinVacaciones.date()),
                'totalVacaciones': totalVacaciones,
                'razon': razon,
            }

            template.sudo().with_context(vacacionesData=vacacionesData).send_mail(res.id, email_values=email_values, force_send=True)

            return 'Solicitud de vacaciones creada'
        else:
            return 'La cantidad de vacaciones supera las que tiene a disposición'

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
    def create_report(self,**kw):

        solicitudVacaciones = request.env['contrato.empleado.vacaciones.line'].sudo().browse(int(request.params['vacacionesId']))
        datas = {
            'vacacionesid': solicitudVacaciones,
        }

        pdf = request.env.ref('uia_portal.report_accion_personal_vacaciones').sudo()._render_qweb_pdf(solicitudVacaciones.id,data=datas)[0]
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf)),
            ('Content-Disposition', 'attachment; filename=' + 'Acción de personal vacaiones' + solicitudVacaciones.empleado_id.name + '.pdf;')
        ]
        return request.make_response(pdf, headers=pdfhttpheaders)

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
    def set_tiempo_acumulado_solicitud(self,fecha=None,jornada=None,tiempo=None,razon=None):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        contrato = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', empleado.id)])

        fechaTomaTiempoAcumulado = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
        tiempo = float(tiempo)

        horarioEmpleado = request.env['horario.empleado'].search([('empleado_id', '=', empleado.id)])
        if not horarioEmpleado:
            return 'Usted no tiene horario asignado para  las fechas de peticion de vacaciones'

        horarioDia = request.env['horario.empleado.line'].search(['&', ('fechaDesde', '<=', fechaTomaTiempoAcumulado), ('fechaHasta', '>=', fechaTomaTiempoAcumulado),('horarioEmpleado_id', '=', horarioEmpleado.id)])
        if not horarioDia:
            return 'Usted no tiene horario asignado para  las fechas de petición de vacaciones'

        if fechaTomaTiempoAcumulado.weekday() == 0:
            if horarioDia.horaInicioLunes == False:
                return 'Dia no laborado'
        elif fechaTomaTiempoAcumulado.weekday() == 1:
            if horarioDia.horaInicioMartes == False:
                return 'Dia no laborado'
        elif fechaTomaTiempoAcumulado.weekday() == 2:
            if horarioDia.horaInicioMiercoles == False:
                return 'Dia no laborado'
        elif fechaTomaTiempoAcumulado.weekday() == 3:
            if horarioDia.horaInicioJueves == False:
                return 'Dia no laborado'
        elif fechaTomaTiempoAcumulado.weekday() == 4:
            if horarioDia.horaInicioViernes == False:
                return 'Dia no laborado'
        elif fechaTomaTiempoAcumulado.weekday() == 5:
            if horarioDia.horaInicioSabado == False:
                return 'Dia no laborado'
        elif fechaTomaTiempoAcumulado.weekday() == 6:
            if horarioDia.horaInicioDomingo == False:
                return 'Dia no laborado'


        if tiempo <= contrato.tiempoAcumuladoRestante:
            fechaFirma = datetime.today() + timedelta(hours=6)
            vals = {
                'contratoEmpleado_id': contrato.id,
                'empleado_id': empleado.id,
                'fechaTiempoAcumulado': fechaTomaTiempoAcumulado.date(),
                'tiempoAcumuladoTomado': tiempo,
                'inicioFinJornada': tiempo,
                'estado': 'En proceso',
                'peticion': True,
                'aceptaionJefatura': False,
                'aceptaionJefaturaRH': False,
                'razon': razon,
                'fechaFirmaEmpleado': fechaFirma,
            }

            res = request.env['contrato.empleado.tiempo.acumulado.line'].sudo().create(vals)
            contrato.tiempoAcumuladoTomado += tiempo
            contrato.tiempoAcumuladoRestante -= tiempo

            template_id = request.env.ref('uia_portal.email_correo_aceptacion_tiempoAcumulado').id
            template = request.env['mail.template'].browse(template_id)
            email_values = {'email_to': empleado.department_id.manager_id.work_email,
                            'subject': 'Aprobación de tiempo acumulado de '+empleado.name,
                            }
            tiempoacumulado = {
                'link': request.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/set_tiempo_acumulado_aprobacion?idTiempoAcumulado="+str(res.id),
                'nombre': empleado.name,
                'totalTiempoAcumulado': tiempo/60,
                'fechasVacaciones': str(fechaTomaTiempoAcumulado.date()),
                'razon': razon,
            }
            template.sudo().with_context(tiempoacumulado=tiempoacumulado).send_mail(res.id, email_values=email_values, force_send=True)

            return 'Solicitud de tiempo acumulado creada'
        else:
            return 'La cantidad de tiempo acumulado supera las que tiene a disposición'


    @http.route('/set_tiempo_acumulado_aprobacion', type='http', auth="user", website=True)
    def set_tiempo_acumulado_aprobacion(self, **kw):
        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])

        if request.env['hr.department'].sudo().search(['&',('manager_id','=',empleado.id),('manager_id','!=',None)]):
            solicitudvacaciones = request.env['contrato.empleado.tiempo.acumulado.line'].sudo().search([('id', '=', request.params['idTiempoAcumulado'])])
            vals = {
                'idTiempoAcumulado': request.params['idTiempoAcumulado'],

            }
            return http.request.render('uia_portal.portal_aprobacion_tiempo_acumulado', vals)
        else:
            vals = {
                'idTiempoAcumulado': 'SinAutorizacion',
            }
            return http.request.render('uia_portal.portal_aprobacion_tiempo_acumulado', vals)

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

    @http.route('/set_tiempo_acumulado_accion', type='json', auth="user", website=True)
    def set_tiempo_acumulado_accion(self,idTiempoAcumulado=None,accion=None):

        user = request.env['res.users'].sudo().search([('id', '=', request.uid)])
        empleado = request.env['hr.employee'].sudo().search(['&',('department_id.name', '!=','Docentes'),('work_email', '=', user.login)])
        solicitudTiempoAcumulado = request.env['contrato.empleado.tiempo.acumulado.line'].sudo().search([('id', '=', idTiempoAcumulado)])

        if request.env['hr.department'].sudo().search([('manager_id', '=', empleado.id)]) and int(request.env['ir.config_parameter'].sudo().get_param('uia_portal.empleado_id')) != empleado.id:
            if solicitudTiempoAcumulado.estado == 'En proceso' and accion == True:
                solicitudTiempoAcumulado.estado = 'Aprobada por Jefatura';
                solicitudTiempoAcumulado.aceptaionJefatura = True;
                solicitudTiempoAcumulado.fechaFirmaJefatura = datetime.today() + timedelta(hours=6)

                jefaturaRH = request.env['hr.employee'].sudo().search([('id', '=', int(request.env['ir.config_parameter'].sudo().get_param('uia_portal.empleado_id')))])
                template_id = request.env.ref('uia_portal.email_correo_aceptacion_tiempoAcumulado').id
                template = request.env['mail.template'].browse(template_id)
                email_values = {'email_to': jefaturaRH.work_email,
                                'subject': 'Aprobación de tiempo acumulado de '+solicitudTiempoAcumulado.empleado_id.name
                                }

                tiempoacumulado = {
                    'link': request.env['ir.config_parameter'].sudo().get_param('web.base.url') + "/set_tiempo_acumulado_aprobacion?idTiempoAcumulado=" + str(idTiempoAcumulado),
                    'nombre': empleado.name,
                }

                template.sudo().with_context(tiempoacumulado=tiempoacumulado).send_mail(solicitudTiempoAcumulado.id, email_values=email_values,force_send=True)

                return {
                    'result': True,
                    'pdfReport': False,
                    'idTiempoAcumulado': idTiempoAcumulado,
                }

            else:
                solicitudTiempoAcumulado.estado = 'Rechazada';
                solicitudTiempoAcumulado.aceptaionJefatura = False;
                solicitudTiempoAcumulado.activo = False;

                return {
                    'result': True,
                    'pdfReport': False,
                    'idTiempoAcumulado': idTiempoAcumulado,
                }

        elif int(request.env['ir.config_parameter'].sudo().get_param('uia_portal.empleado_id')) == empleado.id:

            if solicitudTiempoAcumulado.estado == 'En proceso' and accion == True:
                solicitudTiempoAcumulado.estado = 'Aprobada por Jefatura';
                solicitudTiempoAcumulado.aceptaionJefatura = True;
                solicitudTiempoAcumulado.fechaFirmaRH = datetime.today() + timedelta(hours=6)
                return {
                    'result': True,
                    'pdfReport': False,
                    'idTiempoAcumulado': idTiempoAcumulado,
                }

            elif solicitudTiempoAcumulado.estado == 'Aprobada por Jefatura' and accion == True:
                solicitudTiempoAcumulado.estado = 'Aprobada';
                solicitudTiempoAcumulado.aceptaionJefaturaRH = True;
                solicitudTiempoAcumulado.fechaFirmaRH = datetime.today() + timedelta(hours=6)
                return {
                    'result': True,
                    'pdfReport': True,
                    'idTiempoAcumulado': idTiempoAcumulado,
                }
            else:
                solicitudTiempoAcumulado.estado = 'Rechazada';
                solicitudTiempoAcumulado.aceptaionJefaturaRH = False;
                solicitudTiempoAcumulado.activo = False;
                return {
                    'result': True,
                    'pdfReport': False,
                    'idTiempoAcumulado': idTiempoAcumulado,
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