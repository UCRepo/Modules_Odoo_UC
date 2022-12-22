# -*- coding: utf-8 -*-
import pytz
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime
from odoo.addons.base.models.res_partner import _tz_get

class TesisDocente(models.Model):
    _name = 'tesis.docente'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Tesis de Docentes"


    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        readonly=True,
        default=lambda self: self.env.company.currency_id
    )
    cuatrimestre_id = fields.Many2one(
        comodel_name="periodo.cuatrimestre",
        string="Cuatrimestre",
        required=True,
        tracking=False,
    )
    estudiante = fields.Char(
        string="Estudiante",
        required=False,
    )
    tema = fields.Char(
        string="Tema",
        required=False,
    )
    carrera = fields.Char(
        string="Carrera",
        required=False,
    )
    director = fields.Many2one(
        comodel_name="hr.employee",
        string="Director",
        required=False,
    )
    activeDelegado = fields.Boolean(
        string="Pago Delegado",
        default=False
    )
    delegado = fields.Many2one(
        comodel_name="hr.employee",
        string="Delegado",
        required=False,
    )
    tutor = fields.Many2one(
        comodel_name="hr.employee",
        string="Tutor",
        required=False,
    )
    lector = fields.Many2one(
        comodel_name="hr.employee",
        string="Lector",
        required=False,
    )