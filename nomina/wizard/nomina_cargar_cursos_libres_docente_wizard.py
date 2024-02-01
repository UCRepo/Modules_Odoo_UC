# -*- coding: utf-8 -*-
from datetime import *
from odoo.http import request
import requests
import math
import pytz
import json
from odoo import api, fields, models, _


class CargarCursoLibreDocente(models.TransientModel):
    _name="nomina.cargar.curso.libre.docente.wizard"
    _description = "Crear Curso del Docente"

    periodo_id = fields.Many2one(
        comodel_name="periodo.cursos.libre",
        string="Cuatrimestre",
        required=True,
        tracking=False,
    )

    docente_ids = fields.Many2one(
        comodel_name="hr.employee",
        string="Docente Especifico",
        readonly=False
    )

    def agregar_cursos_docente(self):
        periodo = any
        res = any
        cantiadadHoras = any
        cantiadadHorasSemana = any
        cursosDict = {}
        cursosList = []
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('nomina.urlWSOdoo')+'/api/CursosDocenteUC/getCursosDocente'
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)


        cuatrimestre = self.env['periodo.cursos.libre'].search(['&',('year','=',self.periodo_id.year),('decripcion','=',self.periodo_id.decripcion)])

        docentes = self.env['hr.employee'].search([('department_id.name','=',"Docentes")])

        if self.docente_ids:
            docentes = self.env['hr.employee'].search([('id','=',self.docente_ids.id)])

        if cuatrimestre:
            for dataDocente in docentes:

                cursosDocente = self.env['cursos.libre.docente'].search(['&',('docente_id','=',dataDocente.id),('periodo_id','=',cuatrimestre.id)])
                dataJSon = {
                    'DocenteCedula': dataDocente.identification_id,
                    'Anno': self.periodo_id.year,
                    'Periodo': self.periodo_id.decripcion,
                }
                header = {
                    'Content-Type': 'application/json',
                    'Accept': 'text/plain'
                }
                response = requests.post(url, headers=header, json=dataJSon, verify=False)

                if not cursosDocente:
                    if response.status_code == 200 and len(response.json()['data']) > 0:
                        vals = {
                            'docente_id': dataDocente.id,
                            'periodo_id': cuatrimestre.id,
                            'name': dataDocente.name + " " + cuatrimestre.name
                        }
                        res = self.env['cursos.libre.docente'].sudo().create(vals)
                        for data in response.json()['data']:
                            cursoActivo = True

                            vals = {
                                'docente_id': dataDocente.id,
                                'periodo_id': cuatrimestre.id,
                                'name': self.env['configuraciones.cursos.libre'].search([('codigoCurso', '=', data['codigoCurso'])]).name,
                                'descripcion': self.env['configuraciones.cursos'].search([('codigoCurso', '=', data['codigoCurso'])]).descripcion,
                                'codigoCurso': data['codigoCurso'],
                                'alumnos': data['matriculados'],
                                'estadoActa': data['estadoActa'],
                                'estadoCurso': data['estadoCurso'],
                                'cursoActivo': cursoActivo,
                            }

                            res.cursos_lines_ids = [(0, 0, vals)]
                        return None
                else:
                    self._actualizar_cursos_docente(cursosDocente,response,cuatrimestre)


    def _actualizar_cursos_docente(self,cursosDocente,response,cuatrimestre):
        cantiadadHoras = any
        cantiadadHorasSemana = any
        cursosDict = {}
        cursosList = []
        ICPSudo = self.env['ir.config_parameter'].sudo()
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)

        if response.status_code == 200:

            for curso in cursosDocente.cursos_lines_ids:
                curso.cursoActivo = False

            for data in response.json()['data']:
                cursoActivo = True

                curso = list(filter(lambda x: (x.codigoCurso == data['codigoCurso']) and
                                              (x.cursoActivo == False), cursosDocente.cursos_lines_ids))

                if curso:
                    curso[0].estadoActa = data['estadoActa']
                    curso[0].cursoActivo = True
                    curso[0].fechaCambioCurso = None
                    if curso[0].estadoCurso != data['estadoCurso']:
                        curso[0].estadoCurso = data['estadoCurso']
                        if data['estadoCurso'] == 'TRASLADAR' or data['estadoCurso'] == 'No Impartido':
                            curso[0].cursoActivo = False
                    elif data['estadoCurso'] == 'TRASLADAR' or data['estadoCurso'] == 'No Impartido':
                        curso[0].cursoActivo = False
                    elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext" ) and data['matriculados'] < 4:
                        curso[0].cursoActivo = True
                else:
                    vals = {
                        'docente_id': cursosDocente.docente_id.id,
                        'periodo_id': cursosDocente.periodo_id.id,
                        'name': self.env['configuraciones.cursos.libre'].search([('codigoCurso', '=', data['codigoCurso'])]).name,
                        'descripcion': self.env['configuraciones.cursos'].search([('codigoCurso', '=', data['codigoCurso'])]).descripcion,
                        'codigoCurso': data['codigoCurso'],
                        'alumnos': data['matriculados'],
                        'estadoActa': data['estadoActa'],
                        'cursoActivo': True,
                    }

                    cursosDocente.cursos_lines_ids = [(0, 0, vals)]

    def _get_cambio_curso(self):
        user_tz = pytz.timezone(self.env.user.tz)
        indexDia = pytz.utc.localize(datetime.today()).astimezone(user_tz).weekday()
        fechaActual = pytz.utc.localize(datetime.today()).astimezone(user_tz).date() - timedelta(days=(5 - indexDia))
        return  fechaActual


