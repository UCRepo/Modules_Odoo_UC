# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    cantidadContratos = fields.Integer(string="", required=False,compute='_get_cantidad_contratos')

    direccion = fields.Text(
        string="Dirección",
        required=False,
    )

    def _get_cantidad_contratos(self):
        self.cantidadContratos = self.env['contrato.empleado'].search_count([('empleado_id','=',self.id)])
