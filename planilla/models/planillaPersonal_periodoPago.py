# -*- coding: utf-8 -*-
import calendar

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError

class PlanillaPersonalPeriodoPago(models.Model):
    _name = "planilla.personal.periodo.pago"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Periodo de pago"

    #region Metodos que llenan los fields
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
            lsi.append((str(sumYear + a), _(str(sumYear + a))))
        return lsi
    #endregion

    #region Fields
    name = fields.Char(
        string="Nombre",
        required=False,
    )
    year = fields.Selection(
        string='Año',
        tracking=True,
        required=True,
        selection=_get_years
    )

    mes = fields.Selection(
        string='Mes',
        tracking=True,
        required=True,
        selection=[
            ('Enero','Enero'),
            ('Febrero', 'Febrero'),
            ('Marzo', 'Marzo'),
            ('Abril', 'Abril'),
            ('Mayo', 'Mayo'),
            ('Junio', 'Junio'),
            ('Julio', 'Julio'),
            ('Agosto', 'Agosto'),
            ('Septiembre', 'Septiembre'),
            ('Octubre', 'Octubre'),
            ('Noviembre', 'Noviembre'),
            ('Diciembre', 'Diciembre')
        ]
    )

    fechaInicioMes = fields.Date(
        string="Fecha de Inicio",
        required=True,
        tracking=True, )

    fechaFinMes = fields.Date(
        string="Fecha de Fin",
        required=False,
        tracking=True, )

    fechaInicioPrimerPago = fields.Date(
        string="Inicio Primer Pago",
        required=True,
        tracking=True
    )

    fechaFinPrimerPago = fields.Date(
        string="Fin Primer Pago",
        required=True,
        tracking=True
    )

    fechaInicioSegundoPago = fields.Date(
        string="Inicio Segundo Pago",
        required=True,
        tracking=True
    )

    fechaFinSegundoPago = fields.Date(
        string="Fin Segundo Pago",
        required=True,
        tracking=True
    )

    active = fields.Boolean(
        string='Activo',
        default= True,
        tracking=True,
    )
    warning = fields.Boolean(
        default=False,
        store=False
    )
    #endregion

    #region Dias Libres
    diasLibres_ids = fields.One2many(
        comodel_name="planilla.personal.periodo.pago.dias.libres",
        inverse_name="periodoPago_id",
        string="Dias Libres",
        required=False,
    )
    fecha = fields.Date(
        string="Fecha",
        required=False,
    )
    razon = fields.Char(
        string="Razon",
        required=False,
    )

    def add_dia(self):
        if self.fecha != False and self.razon != False:
            vals = {
                'fecha': self.fecha,
                'razon': self.razon,
            }
            self.diasLibres_ids = [(0, 0, vals)]
            self.fecha = False
            self.razon = False
    #endregion

    #region Metodos generales

    #region Metodos onchange
    @api.onchange('year')
    def _onchangeyear(self):
        """
            Evalua que el field year y mes solo se repita una vez
        :return:
        """
        if self.year != False:
            if self.env['planilla.personal.periodo.pago'].search(['&',('year','=',self.year),('mes','=',self.mes)]):
                self.warning = True
                raise ValidationError("El año "+self.year+" ya esta asignado al mes "+self.mes+" porfavor elegir otro mes o año")
            else:
                self.warning = False

    @api.onchange('mes')
    def _onchangemes(self):
        """
            Evalua que el field year y mes solo se repita una vez
        :return:
        """
        if self.year != False:
            if self.env['planilla.personal.periodo.pago'].search(['&',('year','=',self.year),('mes','=',self.mes)]):
                self.warning = True
                raise ValidationError("El mes "+self.mes+" ya esta asignado al año "+self.year+" porfavor elegir otro mes o año")
            else:
                self.warning = False


    @api.onchange('fechaInicioMes')
    def _onchangefechaInicioMes(self):
        """
            Basado en la fecha selecionada en el field fechaInicioMes se asigna el final de mes y las fechas de pago
        :return:
        """
        if self.fechaInicioMes != False:
            no_of_days  = calendar.monthrange(self.fechaInicioMes.year, self.fechaInicioMes.month)

            self.fechaFinMes = self.fechaInicioMes+timedelta(days=(no_of_days[1]-1))

            self.fechaInicioPrimerPago = self.fechaInicioMes
            self.fechaFinPrimerPago = self.fechaInicioPrimerPago+timedelta(days=14)

            self.fechaInicioSegundoPago = self.fechaFinPrimerPago+timedelta(days=1)

            self.fechaFinSegundoPago = self.fechaFinMes

    #endregion

    #region Metodos override
    @api.model
    def create(self,vals):
        if vals['warning'] != True:
            if not vals.get('name'):
                vals['name'] = vals['mes']+' '+vals['year']
            res = super(PlanillaPersonalPeriodoPago, self).create(vals)
            return res
        else:
            raise ValidationError(" No se puede guardar el registro ya que existe un un año con este mes asignado")
    #endregion

    #endregion

class PlanillaPersonalPeriodoPagoDiasLibres(models.Model):
    _name = "planilla.personal.periodo.pago.dias.libres"
    _description = "Dias del periodo no laborados"

    periodoPago_id = fields.Many2one(
        string='Empleado Line',
        required=True,
        comodel_name='planilla.personal.periodo.pago',
        ondelete="cascade"
    )
    fecha = fields.Date(
        string="Fecha",
        required=False,
    )
    razon = fields.Char(
        string="Razon",
        required=False,
    )
