# -*- coding: utf-8 -*-
from datetime import datetime

import pytz
import requests
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CoborosAsigancionLetras(models.Model):
    _name="cobros.asignacion.letras"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Asignacion de Letras"

    name = fields.Char(
        string="",
        required=False,
    )
    cuatrimestre_id = fields.Many2one(
        string='Periodo',
        tracking=True,
        required=True,
        comodel_name='periodo.cuatrimestre',
    )



    @api.model
    def create(self, vals):
        vals['name'] = 'Asignacion ' + str(self.env['periodo.cuatrimestre'].browse(vals['cuatrimestre_id']).name)
        res = super(CoborosAsigancionLetras, self).create(vals)
        return res


    letrasCobro_ids = fields.One2many(
        comodel_name="cobros.asignacion.letras.line",
        inverse_name="asignacionLetra_id",
        string="Letras",
        required=False,
    )


class CobrosPeriodoPagoLine(models.Model):
    _name="cobros.asignacion.letras.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Letras Estudiantes"


    asignacionLetra_id = fields.Many2one(
        comodel_name="cobros.asignacion.letras",
        ondelete="cascade"
    )

    numeroLetra = fields.Char(
        string="Letra",
        required=False,
    )

    miembroAsignado_id = fields.Many2one(
        string='Miembro Asignado',
        tracking=True,
        comodel_name='res.users',
    )


