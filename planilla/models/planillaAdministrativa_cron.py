# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date, timedelta, datetime
import calendar

class PlanillaAdministrativaCron(models.Model):
    _name = "planialla.administrativa.cron"
    _inherit = 'mail.thread'

    @api.model
    def _send_correo_cumpleanos(self):
        hoy = datetime.today()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        empleados =  self.env['hr.employee'].search(['&',('active','=',True),('department_id.name', '!=','Docentes'),('department_id','!=',"Inactivos")])

        for empleado in empleados:
            if empleado.birthday:
                dia = str(empleado.birthday.year)+'-'+str(hoy.month)+'-'+str(hoy.day)
                cumple = datetime.strptime(dia,"%Y-%m-%d")

                if empleado.birthday ==  cumple.date():

                    datosCorreo = {
                        'empleadoNombre': empleado.name
                    }
                    template_id = self.env.ref('planilla.email_correo_cumple').id
                    template = self.env['mail.template'].browse(template_id)
                    email_values = {'email_to': 'ggamboaf@uia.ac.cr',
                                    'email_from': ICPSudo.get_param('planilla.correoEnvioCumple'),
                                    'subject': 'FELIZ CUMPLEAÑOS'
                                    }

                    template.with_context(datosCorreo=datosCorreo).send_mail(self.id, email_values=email_values,force_send=True)