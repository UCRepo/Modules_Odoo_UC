# -*- coding: utf-8 -*-
from datetime import date, timedelta, datetime
from odoo.http import request
import requests
import pytz
import json
from odoo import api, fields, models, _

class CronsContrato(models.Model):
    _name = "contrato.cron"
    _inherit = 'mail.thread'

    @api.model
    def add_vacaciones(self):

        hoy = datetime.today()
        vacacioneslist = []
        datosCorreo = []

        for empleado in self.env['hr.employee'].search(['&',('active','=',True),('department_id.name', '!=','Docentes'),('department_id','!=',"Inactivos")]):

            contrato = self.env['contrato.empleado'].search([('empleado_id','=',empleado.id)])

            if contrato:
                if not self.env['contrato.empleado.add.vacaciones.line'].search(['&',('fechaCorteAcumulacion','=',hoy.date()),('empleado_id','=',empleado.id)]):
                    if hoy.day == contrato.fechaContratacion.day:
                        vals = {
                            'contratoEmpleado_id': contrato.id,
                            'empleado_id': empleado.id,
                            'fechaCorteAcumulacion': hoy.date(),
                            'razon': 'Acumulación automatica',
                            'vacacionesAcumuladas': 1,
                        }
                        datosCorreo.append({
                            'empleado': empleado.name
                        })
                        vacacioneslist.append(vals)
                        contrato.totalVacaciones += 1
                        contrato.vacacionesRestantes += 1
                        contrato.vacacionesAdd_ids = [(0, 0, vals)]

        if len(datosCorreo) > 0:
            template_id = self.env.ref('contrato.email_acumulacion_vacaciones').id
            template = self.env['mail.template'].browse(template_id)
            email_values = {'email_to': 'rsolanoa@universidadcentral.ac.cr',
                            'subject': "Vacaciones Añadidas"
                            }
            template.with_context(datosCorreo=datosCorreo).send_mail(contrato.id, email_values=email_values,force_send=True)










