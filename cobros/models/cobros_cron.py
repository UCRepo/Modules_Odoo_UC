# -*- coding: utf-8 -*-
from datetime import datetime

import pytz
import requests
from datetime import *
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CobrosCron(models.Model):
    _name="cobros.cron"

    @api.model
    def actualizar_letras(self):
        cobros = self.env['cobros.periodo.pago'].search([('activo','=',True)])

        for data in cobros:
            data.get_datos_cobros_actualizados()

    @api.model
    def cargar_letras(self):
        cobros = self.env['cobros.periodo.pago'].search([('activo','=',True)])

        for data in cobros:
            data.get_datos_cobros()

    @api.model
    def bloquear_usuarios(self):
        cobros = self.env['cobros.periodo.pago'].search(['&',('fechaInicioBloqueo','<=',datetime.today().date()),('activo','=',True)])

        for data in cobros:
            data.set_bloqueo_estudiantes()

    @api.model
    def desbloquear_usuarios(self):
        cobros = self.env['cobros.periodo.pago'].search(['&',('fechaInicioBloqueo','<=',datetime.today().date()),('activo','=',True)])

        for data in cobros:
            data.set_desbloqueo_estudiantes()

    @api.model
    def notificacion_incumplimiento_arreglo(self):
        cobros = self.env['cobros.periodo.pago'].search(['&',('activo','=',True)])

        for data in cobros:
            data.notificacion_incumplimiento_arreglo()

    @api.model
    def notificacion_letra_vencida(self):
        cobros = self.env['cobros.periodo.pago'].search([('activo','=',True)])

        for data in cobros:
            data.send_notificaciones()

