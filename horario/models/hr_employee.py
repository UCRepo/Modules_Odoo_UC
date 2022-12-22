# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    cantidadHorarios = fields.Integer(string="", required=False,compute='_get_cantidad_horarios')

    def _get_cantidad_horarios(self):
        self.cantidadHorarios = self.env['horario.empleado'].search_count([('empleado_id','=',self.id)])
