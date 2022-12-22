# -*- coding: utf-8 -*-
import base64
import pytz
import requests
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime

class PlanillaCursosLibre(models.Model):
    _name = 'planilla.cursos.libre'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Cursos Libre de Docentes"

    name = fields.Char(
        string="Nombre",
        required=False,
    )

    periodo_id = fields.Many2one(
        string='Periodo',
        tracking=True,
        required=True,
        comodel_name='periodo.cursos.libre',
    )

    miembrosPlanilla_id = fields.One2many(
        string='Miembros',
        comodel_name='planilla.cursos.libre.line',
        inverse_name='planillaCursosLibre_id',
    )
    fechaPago510 = fields.Date(
        string="Fecha Pago Cursos 10 Semanas",
        required=False,
    )
    fechaPago715 = fields.Date(
        string="Fecha Pago Cursos 15 Semanas",
        required=False,
    )
    pago = fields.Char(
        string="Pago",
        required=False,
    )

    @api.onchange('periodo_id')
    def _onchangeCuatrimestrePlanillaID(self):
        """
         Al detectar un cambio en el field periodo_id para poder asignar el pago al cuatrimestre
        :return:
        """

        if self.periodo_id.id != False:
            datoPago = self.env['planilla.cursos.libre'].search([('periodo_id', '=', self.periodo_id.id)])
            if len(datoPago) == 0:
                self.pago = 'Primer Pago'
                self.fechaPago715 = self.periodo_id.fechaPrimerPago15Semanas
                self.fechaPago510 =  self.periodo_id.fechaPrimerPago10Semanas
            elif len(datoPago) == 1:
                self.pago = 'Segundo Pago'
                self.fechaPago715 = self.periodo_id.fechaSegundoPago15Semanas
                self.fechaPago510 =  self.periodo_id.fechaSegundoPago10Semanas
            else:
                raise ValidationError("Ya se crearon los 2 pagos para este periodo")

    def crear_planilla(self):

        if self.periodo_id:

            for data in self.env['cursos.libre.docente'].search([('periodo_id','=',self.periodo_id.id)]):
                contratoDocente = self.env['contrato.empleado'].search([('empleado_id', '=', data.docente_id.id)])
                calculosPlanilla = self.env['configuraciones'].search([])
                renta = 0
                CCSSDocente = 0
                embargo = 0
                bruto = 0

                for dataCurso in data.cursos_lines_ids:

                    cursoLibre = self.env['configuraciones.cursos.libre'].search([('codigoCurso','=',dataCurso.codigoCurso)])
                    if cursoLibre.pagoTracto:
                        fecha = datetime.today().date()
                        if fecha > self.fechaPago510 or fecha > self.fechaPago715:
                            bruto += (cursoLibre.pagoDocente / 2) / calculosPlanilla.honorariosTesis
                    else:
                        if dataCurso.estadoActa == 'Entregada':
                            bruto += cursoLibre.pagoDocente / calculosPlanilla.honorariosTesis

                calculo = bruto

                if contratoDocente.pensionado == False:
                    CCSSDocente = calculo * calculosPlanilla.CCSSNormal
                else:
                    CCSSDocente = calculo * calculosPlanilla.CCSSPensionado

                if calculo > calculosPlanilla.desde0 and calculo < calculosPlanilla.hasta0:
                    renta += (calculo - calculosPlanilla.desde0) * calculosPlanilla.porciento0

                elif calculo > calculosPlanilla.desde1 and calculo < calculosPlanilla.hasta1:

                    renta += (calculosPlanilla.hasta0 - calculosPlanilla.desde0) * calculosPlanilla.porciento0
                    renta += (calculo - calculosPlanilla.desde1) * calculosPlanilla.porciento1

                elif calculo > calculosPlanilla.desde2 and calculo < calculosPlanilla.hasta2:

                    renta += (calculosPlanilla.hasta0 - calculosPlanilla.desde0) * calculosPlanilla.porciento0
                    renta += (calculosPlanilla.hasta1 - calculosPlanilla.desde1) * calculosPlanilla.porciento1
                    renta += (calculo - calculosPlanilla.desde2) * calculosPlanilla.porciento2

                elif calculo > calculosPlanilla.desde3:

                    renta += (calculosPlanilla.hasta0 - calculosPlanilla.desde0) * calculosPlanilla.porciento0
                    renta += (calculosPlanilla.hasta1 - calculosPlanilla.desde1) * calculosPlanilla.porciento1
                    renta += (calculosPlanilla.hasta2 - calculosPlanilla.desde2) * calculosPlanilla.porciento2
                    renta += (calculo - calculosPlanilla.desde3) * calculosPlanilla.porciento3

                if contratoDocente.embargo:
                    preCalculo = calculo - (calculosPlanilla.salarioBase * 2)
                    if preCalculo > 1000:
                        embargo = preCalculo * calculosPlanilla.porcientoRebajoEmbargo

                calculo -= embargo
                totalDeducciones = (CCSSDocente + renta)
                aguinaldo = (calculo) * calculosPlanilla.aguinaldo
                cesantia = (calculo) * calculosPlanilla.cesantia
                preaviso = (calculo) * calculosPlanilla.preaviso
                vacaciones = (calculo) * calculosPlanilla.vacaciones
                calculo = (calculo + aguinaldo + cesantia + preaviso + vacaciones) - totalDeducciones

                vals = {
                    'docente_id': data.docente_id.id,
                    'periodo_id': self.periodo_id.id,
                    'nombreDocente': data.docente_id.name,
                    'correoDocente': data.docente_id.work_email,
                    'cedulaDocente': data.docente_id.identification_id,
                    'telefonoDocente': data.docente_id.work_phone,
                    'totalDocente': calculo,
                    'brutoDocente': bruto,
                    'CCSSDocente': CCSSDocente,
                    'rentaDocente': renta,
                    'aguinaldoDocente': aguinaldo,
                    'cesantiaDocente': cesantia,
                    'preavisoDocente': preaviso,
                    'vacacionesDocente': vacaciones,
                    'pagoEfectuado': False,
                    'embargo': embargo,
                    'cuentaBac': contratoDocente.cuentaBac,
                    'cuentaBacActiva': contratoDocente.cuentaBacActiva,
                }
                if calculo > 0:
                    lineaPlanilla = list(filter(lambda  x: (x.docente_id.id == data.docente_id.id) and
                                                           (x.periodo_id.id == self.periodo_id.id) and
                                                           (x.planillaCursosLibre_id.id == self.id), self.miembrosPlanilla_id))

                    if lineaPlanilla:
                        self.miembrosPlanilla_id = [(1, lineaPlanilla[0].id, vals)]
                    else:
                        self.miembrosPlanilla_id = [(0, 0, vals)]

    def generar_reporte_excel_pago(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/planilla/report_excel_planilla_cursos_libres/%s' % (self.id),
            'target': 'new',
        }

    @api.model
    def create(self, vals):
        """
             Funcion que retorna el registro de la pre planilla con los cursos asignados para poder ser creado
             Evalua que el valor de warning sea False el cual en este estado significa que no se tiene ningun error en el registro para poder ser creado
        :return:
            :: retorna el registro
        """
        vals['name'] = 'Planilla Cursos Libres : ' + str(self.env['periodo.cursos.libre'].browse(vals['periodo_id']).name) +' '+vals['pago']
        res = super(PlanillaCursosLibre, self).create(vals)
        return res

class PlanillaCursosLibreLine(models.Model):
    _name="planilla.cursos.libre.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Docente Planilla Cursos Libre Line"

    planillaCursosLibre_id = fields.Many2one(
        string='Docentes Linea',
        comodel_name='planilla.cursos.libre',
        ondelete="cascade"
    )
    docente_id = fields.Many2one(
        required=False,
        comodel_name='hr.employee',
    )
    periodo_id = fields.Many2one(
        required=False,
        comodel_name='periodo.cursos.libre',
    )
    nombreDocente = fields.Char(
        string='Nombre Docente',
    )
    correoDocente = fields.Char(
        string='Correo Docente',
    )
    cedulaDocente = fields.Char(
        string='Cedula Docente',
    )
    telefonoDocente = fields.Char(
        string='Telefono Docente',
    )
    totalDocente = fields.Float(
        digits=(16,2),
        string='Total'
    )
    brutoDocente = fields.Float(
        digits=(16,2),
        string='Bruto'
    )
    CCSSDocente = fields.Float(
        digits=(16,2),
        string='CCSS'
    )
    rentaDocente = fields.Float(
        digits=(16,2),
        string='Renta'
    )
    aguinaldoDocente = fields.Float(
        digits=(16,2),
        string='Aguinaldo'
    )
    cesantiaDocente = fields.Float(
        digits=(16,2),
        string='Cesantia'
    )
    preavisoDocente = fields.Float(
        digits=(16, 2),
        string='Preaviso'
    )
    vacacionesDocente = fields.Float(
        digits=(16, 2),
        string='Vacaciones'
    )
    pagoEfectuado = fields.Boolean(
        string="Pago efectuado",
    )
    embargo = fields.Float(
        string="Embargo",
        digits=(16, 2),
        required=False,
    )
    cuentaBac = fields.Char(
        string="Cuenta BAC",
        required=False,
    )
    cuentaBacActiva = fields.Boolean(
        string="Cuenta BAC Activa",
        default = False
    )