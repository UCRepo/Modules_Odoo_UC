# -*- coding: utf-8 -*-
import pytz
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime
from odoo.addons.base.models.res_partner import _tz_get

class CursosLibreDocente(models.Model):
    _name="cursos.libre.docente"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Cursos Libre del Docente"

    name = fields.Char(
        string="Nombre",
        required=False,
    )
    docente_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Docente",
        required=False,
        tracking=True
    )
    periodo_id = fields.Many2one(
        comodel_name="periodo.cursos.libre",
        string="Periodo",
        required=False,
        tracking=True
    )
    cursos_ids = fields.Many2one(
        comodel_name="configuraciones.cursos.libre",
        string="Curso",
        required=False,
    )
    cantidadEstudiantes = fields.Integer(
        string="Cant. Estudiantes",
        required=False,
    )
    estadoActa = fields.Selection(
        string="Estado de Acta",
        selection=[
            ('Abierta', 'Abierta'),
            ('Enviada', 'Enviada'),
            ('Entregada', 'Entregada'),
            ('Auditada', 'Auditada'),
        ],
        required=False,
    )

    cursos_lines_ids = fields.One2many(
        comodel_name="cursos.libre.docente.line",
        inverse_name="cursosLibreDocente_id",
        string="Cursos",
        required=False,
    )

    def action_add_curso(self):
        if self.docente_id != False and self.cantidadEstudiantes != False and self.estadoActa != False:
            vals = {
                'docente_id': self.docente_id.id,
                'periodo_id': self.periodo_id.id,
                'name': self.cursos_ids.name,
                'descripcion': self.cursos_ids.descripcionCurso,
                'codigoCurso': self.cursos_ids.codigoCurso,
                'alumnos': self.cantidadEstudiantes,
                'estadoActa': self.estadoActa,
                'cursoActivo': True,
            }
            self.cursos_lines_ids = [(0, 0, vals)]

            self.cursos_ids = False
            self.cantidadEstudiantes = False
            self.estadoActa = False

    @api.model
    def create(self, vals):
        """
             Funcion que retorna el registro del docente con los cursos asignados para poder ser creado
        :return:
            :: retorna el registro
        """
        res = super(CursosLibreDocente, self).create(vals)
        vals['name'] = vals['docente_id']
        return res


    def write(self,vals):
        res = super(CursosLibreDocente, self).write(vals)
        return res

class CursosDocenteLines(models.Model):
    _name="cursos.libre.docente.line"
    _description = "Docentes por contrato"

    docente_id = fields.Many2one(
        required=True,
        comodel_name='hr.employee'
    )
    planillaPago_id = fields.Many2one(
        required=True,
        comodel_name='planilla.cursos.libre'
    )
    periodo_id = fields.Many2one(
        required=True,
        comodel_name='periodo.cursos.libre',
    )

    cursosLibreDocente_id = fields.Many2one(
        comodel_name="cursos.libre.docente",
        ondelete="cascade"
    )

    name = fields.Char(
        string="Nombre"
    )

    descripcion = fields.Char(
        string="Descripcion",
        required=False,
    )

    codigoCurso = fields.Char(
        string="Codigo Curso",
        required=True
    )

    alumnos = fields.Integer(
        string="Alumnos",
        required=False,
    )
    estadoCurso = fields.Char(
        string="Estado del Curso",
        required=False,
    )
    estadoActa = fields.Char(
        string="Estado de Acta",
        required=False,
    )
    cursoActivo = fields.Boolean(
        string="Curso Activo",
        default=True,
    )
    fechaCambioCurso = fields.Date(
        string="Fecha de Cambio",
        required=False,
    )
    fechaInicioPago = fields.Date(
        string="Fecha Inicio de Pago",
        required=False,
    )

