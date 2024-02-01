# -*- coding:utf-8 -*-
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError
from odoo import api, fields, models, _


class PeriodoGraduacion(models.Model):
    _name = "sa.periodo.graduacion"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description= "Periodo de graduación"

    name = fields.Char(
        string="Nombre",
        required=True,
        tracking=True,
    )

    activo = fields.Boolean(
        string="Activo",
        default=True,
        tracking=True,
    )

    year_buscar = fields.Char(
        string="Nombre",
        required=True,
        tracking=True,
    )

    year = fields.Selection(
        string='Año',
        required=True,
        selection='_get_years'
    )

    fecha_incio = fields.Date(
        string="Fecha de inicio",
        required=True,
        tracking=True,
    )

    fecha_final = fields.Date(
        string="Fecha de finalización",
        required=True,
        tracking=True,
    )

    def _get_years(self):
        """
             Funcion para optener 4 años siguientes apartir del actual
        :return:
            :: Genera 4 años sumando al años actual
        """
        lsi = []
        anno = datetime.today()
        sumYear = int(anno.year)
        for a in range(5):
            lsi.append((str(sumYear + a), (str(sumYear + a))))
        return lsi

    @api.onchange('year')
    def _onchange_year(self):
        self.year_buscar = self.year





