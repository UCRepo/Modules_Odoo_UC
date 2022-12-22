# -*- coding:utf-8 -*-

from odoo import api, fields, models

class HorarioEmpleado(models.Model):
    _name = "horario.empleado"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Horarios Empleado"

    empleado_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Empleado",
        required=True,
        tracking=True
    )
    name = fields.Char(
        string="Nombre",
        required=False,
    )

    horarioEmpleado_ids = fields.One2many(
        comodel_name="horario.empleado.line",
        inverse_name="horarioEmpleado_id",
        string="Horario",
        required=False,
    )

    horarioSearch = fields.Many2one(
        comodel_name="horario.empleado.line",
        string="Busqueda de Horario",
        domain="[('horarioEmpleado_id','=', id)]",
        required=False,
    )

    def edit_horario(self):
        if len(self.horarioSearch) == 1:
            horarioID = self.horarioSearch.id
            self.horarioSearch = False
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'horario.empleado.line',
                'res_id': horarioID,
                'target': 'new',
                'context': {
                    'form_view_initial_mode':  'edit',
                },
            }

    @api.model
    def create(self, vals):
        vals['name'] = 'Horario de: '+ self.env['hr.employee'].browse(vals['empleado_id']).name
        res = super(HorarioEmpleado, self).create(vals)
        return res
class HorarioEmpleadoLine(models.Model):
    _name = "horario.empleado.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Horarios Empleado"

    horarioEmpleado_id = fields.Many2one(
        comodel_name="horario.empleado",
        string="",
        required=False,
        ondelete="cascade"
    )
    name = fields.Char(
        string="Busqueda",
        required=False,
    )
    fechaDesde = fields.Date(
        string="Desde",
        required=True,
    )
    fechaHasta = fields.Date(
        string="Hasta",
        required=True,
    )
    horaInicioLunes = fields.Datetime(
        string="Entrada lunes",
        required=False,
    )
    horaFinalLunes = fields.Datetime(
        string="Salida lunes ",
        required=False,
    )
    horaInicioMartes = fields.Datetime(
        string="Entrada martes",
        required=False,
    )
    horaFinalMartes = fields.Datetime(
        string="Salida martes",
        required=False,
    )
    horaInicioMiercoles = fields.Datetime(
        string="Entrada miercoles",
        required=False,
    )
    horaFinalMiercoles = fields.Datetime(
        string="Salida miercoles",
        required=False,
    )
    horaInicioJueves = fields.Datetime(
        string="Entrada jueves",
        required=False,
    )
    horaFinalJueves = fields.Datetime(
        string="Salida jueves",
        required=False,
    )
    horaInicioViernes = fields.Datetime(
        string="Entrada viernes",
        required=False,
    )
    horaFinalViernes = fields.Datetime(
        string="Salida viernes",
        required=False,
    )
    horaInicioSabado = fields.Datetime(
        string="Entrada sabado",
        required=False,
    )
    horaFinalSabado = fields.Datetime(
        string="Salida sabado",
        required=False,
    )
    horaInicioDomingo = fields.Datetime(
        string="Entrada domingo",
        required=False,
    )
    horaFinalDomingo= fields.Datetime(
        string="Salida domingo",
        required=False,
    )