"""
    Module Periodo Cutrimestre
"""
# -*- coding: utf-8 -*-
from datetime import date, timedelta, datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PeriodoCursosLibre(models.Model):
    _name = "periodo.cursos.libre"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Periodo Cuatrimestre"

    name = fields.Char(
        string='Nombre',
        tracking=True
    )

    decripcion = fields.Selection(
        string='Descripción',
        tracking=True,
        required=True,
        selection=[
            ('62', 'Cursos Libres Primero'),
            ('63', 'Cursos Libres Segundo'),
            ('64', 'Cursos Libres Tercero ')]
    )

    year = fields.Selection(
        string='Año',
        tracking=True,
        required=True,
        selection='_get_years'
    )

    anno = fields.Char(
        string="Año",
        required=False,
    )


    active = fields.Boolean(
        string='Activo',
        default= True,
        tracking=True
    )

    fechaInicioCuatrimestre = fields.Date(
        string="Inicio Periodo",
        required=True,
        tracking=True
    )

    fechaFinCuatrimestre = fields.Date(
        string="Fin Periodo",
        required=True,
        tracking=True
    )

    fechaPrimerPago15Semanas = fields.Date(
        string="Primer Pago",
        required=True,
        tracking=True
    )

    fechaSegundoPago15Semanas = fields.Date(
        string="Segundo Pago",
        required=True,
        tracking=True
    )

    fechaPrimerPago10Semanas = fields.Date(
        string="Primer Pago",
        required=True,
        tracking=True
    )

    fechaSegundoPago10Semanas = fields.Date(
        string="Segundo Pago",
        required=True,
        tracking=True
    )

    warning = fields.Boolean(default=False, store=False)

    def _get_years(self):
        """
             Funcion para optener 4 annos siguientes apartir del actual
        :return:
            :: Genera 4 años sumando al años actual
        """
        lsi = []
        anno = datetime.today()
        sumYear = int(anno.year)
        for a in range(5):
            lsi.append((str(sumYear+a), _(str(sumYear+a))))
        return lsi

    @api.model
    def create(self, vals):
        """
             Funcion que retorna el registro del cuatrimestre para poder ser creado
             Evalua que el valor de warning sea False el cual en este estado significa que no se tiene ningun error en el registro para poder ser creado
        :return:
            :: retorna el registro
        """
        if vals['warning'] != True:
            if not vals.get('name'):
                if vals['decripcion'] == '62':
                    vals['name'] = 'Cursos Libres Primero  ' + vals['year']
                elif vals['decripcion'] == '63':
                    vals['name'] = 'Cursos Libres Segundo  ' + vals['year']
                elif vals['decripcion'] == '64':
                    vals['name'] = 'Cursos Libres Tercero ' + vals['year']

                vals['anno'] = vals['year']
            res = super(PeriodoCursosLibre, self).create(vals)
            return res
        else:
            raise ValidationError(" No se puede guardar el registro ya que existe un un año con este periodo asignado")

    def write(self,vals):
        if 'year' in vals:
            vals['anno'] = vals['year']
        res = super(PeriodoCursosLibre, self).write(vals)
        return res

    @api.onchange('fechaInicioCuatrimestre')
    def _onchangeFechaInicioCuatrimestre(self):
        """
             Al detectar un cambio de estado en el Field fechaInicioCuatrimestre genera el fechaFinCuatrimestre
             y tambien gerena las fechas de los 3 pagos que se ralizan en el cuatrimestre segun las semanas que se van a pagar 4, 5 y 6
        """
        if self.fechaInicioCuatrimestre != False:
            self.fechaFinCuatrimestre = self.fechaInicioCuatrimestre+timedelta(weeks=15)

            self.fechaPrimerPago10Semanas = self.fechaInicioCuatrimestre + timedelta(weeks=4)
            self.fechaSegundoPago10Semanas = self.fechaInicioCuatrimestre + timedelta(weeks=9)

            self.fechaPrimerPago15Semanas = self.fechaInicioCuatrimestre + timedelta(weeks=6)
            self.fechaSegundoPago15Semanas = self.fechaInicioCuatrimestre + timedelta(weeks=14)


    @api.onchange('year')
    def _onchangeYear(self):
        """
             Al detectar un cambio de estado en el Field year evalua si existe un anno con el mismo cutrimestre asignado
        """
        if self.year != False:
            for data in self.env['periodo.cursos.libre'].search([]):
                if data.year  == self.year and data.decripcion == self.decripcion:
                    self.warning = True
                    break
                else:
                    self.anno = self.year
                    self.warning = False

    @api.onchange('decripcion')
    def _onchangeDecripcion(self):
        """
             Al detectar un cambio de estado en el Field decripcion evalua si existe un cuatrimestre con el mismo anno asignado
        """
        if self.decripcion != False:
            for data in self.env['periodo.cursos.libre'].search([]):
                if data.year  == self.year and data.decripcion == self.decripcion:
                    self.warning = True
                    break
                else:
                    self.warning = False