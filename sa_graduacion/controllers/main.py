# -*- coding: utf-8 -*-
import io
from odoo.tools.misc import xlsxwriter
import pytz
import json
import requests
from odoo import http
from odoo.http import content_disposition, request
from datetime import date, timedelta, datetime

class ProcesoGraduacion(http.Controller):

    @http.route('/get_estudiante_carreras', type='json', auth="public", website=True)
    def get_estudiante_carreras(self,cedulaEstudiante=None):
        ICPSudo = request.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('sa_graduacion.procesoGraduacionURLAPI') + '/api/Estudiante/getCarrerasEstudiante'

        dataJSon = {
            "cedulaEstudiante": cedulaEstudiante,
        }
        header = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain'
        }

        response = requests.post(url, headers=header, json=dataJSon, verify=False)

        if response.status_code == 200:
            carreras = ['Seleccioné la Carrera']
            carreras = carreras + response.json()['data']
            return {
                'tiene': True,
                'carreras': carreras
            }
        else:
            return {
                'tiene': False
            }

    @http.route('/proceso_graduacion', type='http', auth="public", website=True)
    def proceso_graduacion(self,valsJS=None ):
        user_tz = pytz.timezone(request.env.user.tz)
        hoy = pytz.utc.localize(datetime.today()).astimezone(user_tz)

        periodo = request.env['sa.periodo.graduacion'].sudo().search([('fecha_incio','<=',hoy.date()),('fecha_final','>=',hoy.date())])

        vals = {
            'periodo_Graduacion': periodo.name

        }

        return http.request.render('sa_graduacion.proceso_graduacion', vals)

    @http.route('/get_estado_graduacion', type='json', auth="public", website=True)
    def get_estado_graduacion(self,cedulaEstudiante=None ):
        user_tz = pytz.timezone(request.env.user.tz)
        hoy = pytz.utc.localize(datetime.today()).astimezone(user_tz)

        periodo = request.env['sa.periodo.graduacion'].sudo().search([('fecha_incio','<=',hoy.date()),('fecha_final','>=',hoy.date())])

        estudiante = request.env['sa.graduacion.estudiante'].sudo().search([('periodoGraduacion_id','=',periodo.id),('identificacion','=',cedulaEstudiante)])

        if estudiante:
            return {
                'estado': estudiante.state,
                'tiene': True,
                'pago': True if estudiante.copia_comprobande and estudiante.copia_Boleta else False,
            }
        else:
            return {
                'tiene': False,
            }

    @http.route('/set_pago_graduacion', type='json', auth="public", website=True)
    def set_pago_graduacion(self,valsJS=None ):
        user_tz = pytz.timezone(request.env.user.tz)
        hoy = pytz.utc.localize(datetime.today()).astimezone(user_tz)

        periodo = request.env['sa.periodo.graduacion'].sudo().search([('fecha_incio','<=',hoy.date()),('fecha_final','>=',hoy.date())])

        estudiante = request.env['sa.graduacion.estudiante'].sudo().search([('periodoGraduacion_id','=',periodo.id),('identificacion','=',valsJS['identificacion'])])

        estudiante.copia_comprobande = valsJS['comprobante']
        estudiante.copia_Boleta = valsJS['boleta']
        return {
            'result': "Gracias",
        }

    @http.route('/proceso_graduacion_actualizar', type='json', auth="public", website=True)
    def proceso_graduacion_actualizar(self,valsJS=None ):
        user_tz = pytz.timezone(request.env.user.tz)
        hoy = pytz.utc.localize(datetime.today()).astimezone(user_tz)
        periodo = request.env['sa.periodo.graduacion'].sudo().search([('fecha_incio', '<=', hoy.date()), ('fecha_final', '>=', hoy.date())])
        estudiante = request.env['sa.graduacion.estudiante'].sudo().search([('periodoGraduacion_id', '=', periodo.id), ('identificacion', '=', valsJS['identificacion'])])
        ICPSudo = request.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('proceso_tcu.procesoTCUURLAPI') + '/api/Estudiante/getEstudianteInfo'
        dataJSon = {
            "cedulaEstudiante": valsJS['identificacion'],
        }
        header = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain'
        }
        response = requests.post(url, headers=header, json=dataJSon, verify=False)

        if response.status_code == 200:
            estudiante = response.json()['data']
            valsJS['name'] = estudiante['nombre']
            valsJS['carnet'] = estudiante['carnet']
        else:
            valsJS['name'] = "N/A"
            valsJS['carnet'] = "N/A"

        valsJS['periodoGraduacion_id'] = periodo.id
        valsJS['fecha_Vencimiento'] = hoy.date() + timedelta(days=7)
        valsJS['fecha_Solicitud'] = hoy.date()


        estudiante.sudo().write(valsJS)
        proceso.envio_Correo_Recibido()


        return {
            'result': "Gracias sele informará, por medio de correo electrónico, el estado de la solicitud o bien podrá introducir otra vez su identificación en refrescando esta página para ver el estado de la solicitud.",
        }

    @http.route('/proceso_graduacion_crear', type='json', auth="public", website=True)
    def proceso_graduacion_crear(self,valsJS=None ):
        user_tz = pytz.timezone(request.env.user.tz)
        hoy = pytz.utc.localize(datetime.today()).astimezone(user_tz)
        periodo = request.env['sa.periodo.graduacion'].sudo().search([('fecha_incio', '<=', hoy.date()), ('fecha_final', '>=', hoy.date())])
        ICPSudo = request.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('proceso_tcu.procesoTCUURLAPI') + '/api/Estudiante/getEstudianteInfo'
        dataJSon = {
            "cedulaEstudiante": valsJS['identificacion'],
        }
        header = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain'
        }
        response = requests.post(url, headers=header, json=dataJSon, verify=False)

        if response.status_code == 200:
            estudiante = response.json()['data']
            valsJS['name'] = estudiante['nombre']
            valsJS['carnet'] = estudiante['carnet']
        else:
            valsJS['name'] = "N/A"
            valsJS['carnet'] = "N/A"

        valsJS['periodoGraduacion_id'] = periodo.id
        valsJS['fecha_Vencimiento'] = hoy.date() + timedelta(days=7)
        valsJS['fecha_Solicitud'] = hoy.date()


        proceso = request.env['sa.graduacion.estudiante'].sudo().create(valsJS)
        proceso.envio_Correo_Recibido()


        return {
            'result': "Gracias sele informará, por medio de correo electrónico, el estado de la solicitud o bien podrá introducir otra vez su identificación en refrescando esta página para ver el estado de la solicitud.",
        }