# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    salarioDocente = fields.Float(string="Salario",  required=False,tracking=True )
    marcas = fields.Boolean(string="Registra Marca",tracking=True, help='comentario' )
    pensionado = fields.Boolean(string="CCSS Pensionado", tracking=True, help='comentario' )