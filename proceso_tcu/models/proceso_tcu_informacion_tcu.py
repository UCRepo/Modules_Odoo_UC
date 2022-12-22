# -*- coding:utf-8 -*-

from dateutil.relativedelta import relativedelta
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError
from odoo import api, fields, models


class ContratoEmpleado(models.Model):
    _name = "proceso.tcu.informacion_tcu"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description= "Informacion de TCU"

    #region Informacion Estudiante
    nombreEstudiante = fields.Char(
        string="Nombre",
        required=False,
    )
    identificacionEstudiante = fields.Char(
        string="Nombre",
        required=False,
    )
    carreraEstudiante = fields.Char(
        string="Nombre",
        required=False,
    )
    #endregion
    #region Primera Fase
    cartaAceptacionInstitucionTCU = fields.Binary(
        string='Carta de aceptación de la institución',
        required=False,
    )
    anteproyectoTCU = fields.Binary(
        string='Anteproyecto',
        required=False,
    )
    cronogramaTCU = fields.Binary(
        string='Cronograma',
        required=False,
    )

    observacionesPrimeraEntrega = fields.Text(
        string="Observaciones",
        required=False,
    )

    aceptadoPrimeraEntrega = fields.Boolean(
        string="Aceptado",
    )
    #endregion

    #region Segunda Fase
    bitacora = fields.Binary(
        string='Bitácora',
        required=False,
    )
    cartaFinalizacion = fields.Binary(
        string='Carta de Finalización',
        required=False,
    )
    boletaFinalizacion = fields.Binary(
        string='Boleta de Finalización',
        required=False,
    )

    observacionesSegundaEntrega = fields.Text(
        string="Observaciones",
        required=False,
    )

    aceptadoSegundaEntrega = fields.Boolean(
        string="Aceptado",
    )
    #endregion


