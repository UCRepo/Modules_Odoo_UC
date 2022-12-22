# -*- coding: utf-8 -*-
from datetime import *
from odoo.http import request
import requests
import math
import pytz
import json
from odoo import api, fields, models, _


class CargarCursoDocente(models.TransientModel):
    _name="nomina.cargar.curso.docente.wizard"
    _description = "Crear Curso del Docente"

    cuatrimestre_id = fields.Many2one(
        comodel_name="periodo.cuatrimestre",
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


        cuatrimestre = self.env['periodo.cuatrimestre'].search(['&',('year','=',self.cuatrimestre_id.year),('decripcion','=',self.cuatrimestre_id.decripcion)])

        docentes = self.env['hr.employee'].search([('department_id.name','=',"Docentes")])

        if self.docente_ids:
            docentes = self.env['hr.employee'].search([('id','=',self.docente_ids.id)])

        if cuatrimestre:
            for dataDocente in docentes:

                cursosDocente = self.env['cursos.docente'].search(['&',('docente_id','=',dataDocente.id),('cuatrimestre_id','=',cuatrimestre.id)])
                dataJSon = {
                    'DocenteCedula': dataDocente.identification_id,
                    'Anno': self.cuatrimestre_id.year,
                    'Periodo': self.cuatrimestre_id.decripcion.replace('Q', '') ,
                }
                header = {
                    'Content-Type': 'application/json',
                    'Accept': 'text/plain'
                }
                response = requests.post(url, headers=header, json=dataJSon, verify=False)

                if not cursosDocente:
                    if response.status_code == 200:
                        if 2>1:
                            vals = {
                                'docente_id': dataDocente.id,
                                'cuatrimestre_id': cuatrimestre.id,
                                'warning': False,
                                'name': dataDocente.name +" "+ cuatrimestre.name
                            }
                            res = self.env['cursos.docente'].sudo().create(vals)
                            for data in response.json()['data']:
                                cursoActivo = True
                                if (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext" ) and data['matriculados'] == 1:
                                    cantiadadHoras = 2
                                    cantiadadHorasSemana = 2
                                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext" )and data['matriculados'] == 2:
                                    cantiadadHoras = 2
                                    cantiadadHorasSemana = 2
                                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext" )and data['matriculados'] == 3:
                                    cantiadadHoras = 3
                                    cantiadadHorasSemana = 3
                                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext" )and data['matriculados'] == 4:
                                    cantiadadHoras = 3
                                    cantiadadHorasSemana = 3
                                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext" )and data['matriculados'] == 5:
                                    cantiadadHoras = 3
                                    cantiadadHorasSemana = 3
                                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext" ) and data['matriculados'] == 6:
                                    cantiadadHoras = 3
                                    cantiadadHorasSemana = 3
                                else:
                                    cantiadadHoras = data['horasCurso']
                                    cantiadadHorasSemana = data['horasCurso']


                                if self.env['configuraciones.cursos.medicina'].search(['&',('planillaExterna','=',True),('codigoCurso','=',data['codigoCurso'])]):
                                    cursoActivo = False


                                res.cursos_lines_ids = [(0, 0, {'cursos_id': res.id,
                                                                'docente_id': dataDocente.id,
                                                                'cuatrimestre_id': cuatrimestre.id,
                                                                'name': self.env['configuraciones.cursos'].search([('codigoCurso', '=', data['codigoCurso'])]).name,
                                                                'descripcion': self.env['configuraciones.cursos'].search([('codigoCurso','=', data['codigoCurso'])]).descripcion,
                                                                'codigoCurso': data['codigoCurso'],
                                                                'cantiadadHoras': cantiadadHoras,
                                                                'cantiadadHorasSemana': cantiadadHorasSemana,
                                                                'horario': data['horario'],
                                                                'dia1': data['dia1'],
                                                                'dia2': "N/A",
                                                                'dia3': "N/A",
                                                                'horaInicio': data['horaInicio'],
                                                                'minutoInicio': data['minutoInicio'],
                                                                'ampmInicio': data['ampmInicio'],
                                                                'horaFinal': data['horaFinal'],
                                                                'minutoFinal': data['minutoFinal'],
                                                                'ampmFinal': data['ampmFinal'],
                                                                'alumnos': data['matriculados'],
                                                                'estadoCurso': data['estadoCurso'],
                                                                'estadoActa': data['estadoActa'],
                                                                'cursoActivo': cursoActivo,
                                                                })]
                else:
                    self._actualizar_cursos_docente(cursosDocente,response,cuatrimestre)

            self._envio_correo_horarios_erroneos()
            self._envio_correo_cursos_deshabilitados()
            self._envio_correo_cursos_choques()

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
                if curso.fechaCambioCurso ==  False:
                    curso.fechaCambioCurso = self._get_cambio_curso()

            for data in response.json()['data']:
                cursoActivo = True
                tutoriaDif = False

                if self.env['configuraciones.cursos.medicina'].search(['&', ('planillaExterna', '=', True), ('codigoCurso', '=', data['codigoCurso'])]):
                    cursoActivo = False

                if (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext") and data['matriculados'] == 1:
                    cantiadadHoras = 2
                    cantiadadHorasSemana = 2
                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext") and data['matriculados'] == 2:
                    cantiadadHoras = 2
                    cantiadadHorasSemana = 2
                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext") and data['matriculados'] == 3:
                    cantiadadHoras = 3
                    cantiadadHorasSemana = 3
                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext") and data['matriculados'] == 4:
                    cantiadadHoras = 3
                    cantiadadHorasSemana = 3
                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext") and data['matriculados'] == 5:
                    cantiadadHoras = 3
                    cantiadadHorasSemana = 3
                elif (data['estadoCurso'] == "Tutoria" or data['estadoCurso'] == "Tutoria Ext") and data['matriculados'] == 6:
                    cantiadadHoras = 3
                    cantiadadHorasSemana = 3
                else:
                    cantiadadHoras = data['horasCurso']
                    cantiadadHorasSemana = data['horasCurso']

                curso = None
                if not tutoriaDif:
                    curso = list(filter(lambda  x: (x.dia1 == data['dia1']) and
                                                   (x.horario == data['horario']),cursosDocente.cursos_lines_ids))
                else:
                    curso = list(filter(lambda x: (x.dia1 == data['dia1']) and
                                                  (x.horario == data['horario']) and
                                                  (x.codigoCurso == data['codigoCurso']), cursosDocente.cursos_lines_ids))


                if curso:
                    curso[0].estadoActa = data['estadoActa']
                    curso[0].cantiadadHoras = cantiadadHoras
                    curso[0].cantiadadHorasSemana = cantiadadHorasSemana
                    curso[0].cursoActivo = cursoActivo
                    curso[0].fechaCambioCurso = None
                    if curso[0].estadoCurso != data['estadoCurso']:
                        curso[0].estadoCurso = data['estadoCurso']
                        if data['estadoCurso'] == 'Trasladar' or data['estadoCurso'] == 'No Impartido':
                            curso[0].cursoActivo = False
                    elif data['estadoCurso'] == 'Trasladar' or data['estadoCurso'] == 'No Impartido':
                        curso[0].cursoActivo = False
                    elif (data['estadoCurso'] == "Trasladar" or data['estadoCurso'] == "Tutoria Ext" ) and data['matriculados'] < 4:
                        curso[0].cursoActivo = True
                else:
                    cursosDocente.cursos_lines_ids = [(0, 0, {'cursos_id': cursosDocente.id,
                                                              'docente_id': cursosDocente.docente_id.id,
                                                              'cuatrimestre_id': cursosDocente.cuatrimestre_id.id,
                                                              'name': self.env['configuraciones.cursos'].search([('codigoCurso', '=', data['codigoCurso'])]).name,
                                                              'descripcion': self.env['configuraciones.cursos'].search([('codigoCurso','=',data['codigoCurso'])]).descripcion,
                                                              'codigoCurso': data['codigoCurso'],
                                                              'cantiadadHoras': cantiadadHoras,
                                                              'cantiadadHorasSemana': cantiadadHorasSemana,
                                                              'horario': data['horario'],
                                                              'dia1': data['dia1'],
                                                              'dia2': "N/A",
                                                              'dia3': "N/A",
                                                              'horaInicio': data['horaInicio'],
                                                              'minutoInicio': data['minutoInicio'],
                                                              'ampmInicio': data['ampmInicio'],
                                                              'horaFinal': data['horaFinal'],
                                                              'minutoFinal': data['minutoFinal'],
                                                              'ampmFinal': data['ampmFinal'],
                                                              'alumnos': data['matriculados'],
                                                              'estadoCurso': data['estadoCurso'],
                                                              'estadoActa': data['estadoActa'],
                                                              'cursoActivo': cursoActivo,
                                                              'fechaInicioPago': self._get_cambio_curso(),
                                                              })]

    def _envio_correo_horarios_erroneos(self):
        cursosDict = {}
        cursosList = []
        ICPSudo = self.env['ir.config_parameter'].sudo()
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)


        if self.cuatrimestre_id:
            cursosDocente = self.env['cursos.docente.line'].search([('cuatrimestre_id', '=', self.cuatrimestre_id.id),'|', ('cantiadadHoras', '<',0 ),('cantiadadHoras', '>',6)])
            for data in cursosDocente:

                cursosDict = {
                    'docente': data.docente_id.name,
                    'curso': data.descripcion,
                    'codigo': data.codigoCurso,
                    'horasCurso': data.cantiadadHoras,
                    'horarioCurso': data.horario,
                }
                cursosList.append(cursosDict)
                data.unlink()
            if len(cursosList) != 0:
                template_id = self.env.ref('nomina.email_cursos_horario_erroneo').id
                template = self.env['mail.template'].browse(template_id)
                email_values = {'email_to': ICPSudo.get_param('nomina.correoEnvioHorarioErroneo'),
                                'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                                'subject': 'Reporte de cursos horario erroneo ' + str(anno.date())
                                }
                template.with_context(listCursos=cursosList).send_mail(self.id, email_values=email_values,force_send=True)

    def _envio_correo_cursos_deshabilitados(self):
        cursosDict = {}
        cursosList = []
        ICPSudo = self.env['ir.config_parameter'].sudo()
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)

        if self.cuatrimestre_id:
            cursosDocente = self.env['cursos.docente.line'].search([('fechaCambioCurso', '=',pytz.utc.localize(datetime.today()).astimezone(user_tz).date())])
            for data in cursosDocente:
                cursosDict = {
                    'docente': data.docente_id.name,
                    'curso': data.descripcion,
                    'codigo': data.codigoCurso,
                    'horasCurso': data.cantiadadHoras,
                    'horarioCurso': data.horario,
                }
                cursosList.append(cursosDict)
            if len(cursosList) != 0:
                template_id = self.env.ref('nomina.email_cursos_cursos_deshabilitados').id
                template = self.env['mail.template'].browse(template_id)
                email_values = {'email_to': ICPSudo.get_param('nomina.correoEnvioHorarioErroneo'),
                                'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                                'subject': 'Reporte de cursos deshabilitados ' + str(anno.date())
                                }
                template.with_context(listCursos=cursosList).send_mail(self.id, email_values=email_values,force_send=True)

    def _envio_correo_cursos_choques(self):
        cursosDict = {}
        cursosList = []
        ICPSudo = self.env['ir.config_parameter'].sudo()
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)

        if self.cuatrimestre_id:
            cursosDocente = self.env['cursos.docente.line'].search([('cuatrimestre_id', '=', self.cuatrimestre_id.id)])
            for data in cursosDocente:
                if data.cursoActivo:
                    cursoChoque = list(filter(lambda x: (x.dia1 == data.dia1) and
                                                        (int(data.horaInicio) >= int(x.horaInicio)) and
                                                        (x.docente_id == data.docente_id) and
                                                        (x.id != data.id) and
                                                        (x.cursoActivo == True) and
                                                        (x.cuatrimestre_id == data.cuatrimestre_id) and
                                                        (x.alumnos > 3) and
                                                        (int(data.horaInicio) < int(x.horaFinal) ),cursosDocente ))

                    for dataCurso in cursoChoque:
                        dataCurso.cursoActivo = False
                        cursosDict = {
                            'docente': data.docente_id.name,
                            'curso': data.descripcion,
                            'codigo': data.codigoCurso,
                            'horasCurso': data.cantiadadHoras,
                            'horarioCurso': data.horario,
                        }
                        cursosList.append(cursosDict)

        if len(cursosList) != 0:
            template_id = self.env.ref('nomina.email_cursos_cursos_choques').id
            template = self.env['mail.template'].browse(template_id)
            email_values = {'email_to': 'ggamboaf@uia.ac.cr',
                            'email_from': ICPSudo.get_param('nomina.correoEnvio'),
                            'subject': 'Cursos con Choques de Horario ' + str(anno.date())
                            }
            template.with_context(listCursos=cursosList).send_mail(self.id, email_values=email_values, force_send=True)

    def _get_cambio_curso(self):
        user_tz = pytz.timezone(self.env.user.tz)
        indexDia = pytz.utc.localize(datetime.today()).astimezone(user_tz).weekday()
        fechaActual = pytz.utc.localize(datetime.today()).astimezone(user_tz).date() - timedelta(days=(6 - (6-(indexDia + 1)) ))
        return  fechaActual


