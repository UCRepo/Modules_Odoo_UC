# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError

class PlanillaPersonalPeriodoPago(models.Model):
    _name = "planilla.personal.empleados.planilla"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Empleados Planilla"

    #region Campos General
    name = fields.Char(
        string="Nombre",
        required=False,
    )
    empleado_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Empleado",
        required=True,
        tracking=True,
    )
    pago = fields.Char(
        string="Pago",
        required=False,
    )
    peridoPago_id = fields.Many2one(
        comodel_name="planilla.personal.periodo.pago",
        string="Periodo de Pago",
        required=True,
        tracking=True,
    )
    salarioBase = fields.Float(
        string="Salario Base",
        required=True,
        digits=(16, 1),
        deafult=0.0,
        currency_field='currency_id'
    )
    diasPagoCompleto = fields.Integer(
        string="Dias de pago",
        required=False,
        store=True,
    )
    diasPagoMitad = fields.Integer(
        string="Dias medio pago",
        required=False,
        store=True,
    )
    diasSinPago = fields.Integer(
        string="Dias sin pago",
        required=False,
        store=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        readonly=True,
        default=lambda self: self.env.company.currency_id
    )

    def _compute_diasPagoCompleto(self):
        restaDias = 0
        diasCompletos = 15

        for rec in self.incapacidades_ids:
            restaDias += rec.diasIncapacidad

        self.diasPagoCompleto = diasCompletos - restaDias

    def _compute_diasPagoMitad(self):
        dias = 0
        for rec in self.incapacidades_ids:
            dias += rec.diasIncapacidad

        self.diasPagoMitad = dias

    def _compute_diasSinPago(self):
        dias = 0

        for rec in self.incapacidades_ids:
            dias += rec.diasIncapacidadRebajas

        self.diasSinPago = dias


    #endregion

    #region Incapacidades
    incapacidades_ids = fields.Many2many(
        comodel_name="contrato.empleado.incapacidad.line",
        relation='planilla_administrativa_contrato_incapacidades_rel',
        string="Incapacidades",
        required=True,
        tracking=True,
    )
    def _compute_add_incapacidades(self):
        if self.desde != False and self.hasta != False:
            vals = self.env['contrato.empleado.incapacidad.line'].search(['&',('fechaInicioIncapacidad', '>=', self.desde),('fechaFinIncapacidad','<=',self.hasta),('empleado_id','=',self.empleado_id.id)])
            if vals.id != False:
                self.incapacidades_ids =  [[ 4, vals.id]]
            else:
                self.incapacidades_ids = None

    #endregion

    #region Vacaciones
    vacaciones_ids = fields.Many2many(
        comodel_name="contrato.empleado.vacaciones.line",
        relation='planilla_administrativa_contrato_vacaciones_rel',
        string="Incapacidades",
        required=True,
        tracking=True,
    )

    def add_vacaciones(self):
        """
        Agrega vacciones a la lista
        :return:
        """
        if self.diasVacaciones >= 0:
            vacacionesRestantes  = self.env['contrato.empleado'].search([('empleado_id','=',self.empleado_id.id)]).vacacionesRestantes
            if vacacionesRestantes >= self.diasVacaciones:
                self.vacaciones_ids = [(0, 0, {'empleado_id': self.empleado_id.id,
                                               'periodoPago_id': self.peridoPago_id.id,
                                               'fechaInicioVacaciones': self.fechaInicioVacaciones,
                                               'fechaFinVacaciones': self.fechaFinVacaciones,
                                               'diasVacaciones': self.diasVacaciones,
                                               })]

                contrato = self.env['contrato.empleado'].search([('empleado_id', '=', self.empleado_id.id)])
                contrato.vacacionesTomadas += self.diasVacaciones
                contrato.vacacionesRestantes -= self.diasVacaciones


                self.fechaInicioVacaciones = False
                self.fechaFinVacaciones = False
                self.diasVacaciones = 0
            else:
                raise ValidationError("Ud solo tiene "+str(vacacionesRestantes)+" dias restantes de vacaciones")

    @api.onchange('fechaInicioVacaciones')
    def _onchangeFechaInicioVacaciones(self):
        """
        Al detectar un cambio en el field fechaInicioVacaciones determina los dias de vacaciones
        :return:
        """
        if self.fechaFinVacaciones != False:
            diasVacaciones = ((self.fechaFinVacaciones -self.fechaInicioVacaciones).days)+1
            if diasVacaciones <= 0:
                raise ValidationError("Los dias de vacaiones no pueden ser menores o igual a 0")
            else:
                self.diasVacaciones = diasVacaciones

    @api.onchange('fechaFinVacaciones')
    def _onchangeFechaFinVacaciones(self):
        """
        Al detectar un cambio en el field fechaInicioVacaciones determina los dias de vacaciones
        :return:
        """
        if self.fechaFinVacaciones != False:
            diasVacaciones = ((self.fechaFinVacaciones -self.fechaInicioVacaciones).days)+1
            if diasVacaciones <= 0:
                raise ValidationError("Los dias de vacaiones no pueden ser menores o igual a 0")
            else:
                self.diasVacaciones = diasVacaciones
    #endregion

    #region Licencias
    licecnias_ids = fields.Many2many(
        comodel_name="contrato.empleado.licencias.line",
        relation='planilla_administrativa_contrato_licencias_rel',
        string="Licencias",
        required=True,
        tracking=True,
    )
    #endregion

    #region Prestamos
    prestamos_ids = fields.One2many(
        string='Prestamos',
        tracking=True,
        comodel_name='planilla.personal.prestamos.line',
        inverse_name='empleadosPlanillaLine_id',
    )
    #endregion

    #region Fechas de Pago
    desde = fields.Date(
        string="Desde",
        required=False,
    )
    hasta = fields.Date(
        string="Hasta",
        required=False,
    )

    #endregion

    #region Pension
    montoPension = fields.Float(
        string="Monto de pensión",
        required=True,
        digits=(16, 1),
        deafult=0.0,
        currency_field='currency_id'
    )
    #endregion

    #region Asistencia
    asistencia_line_ids = fields.One2many(
        comodel_name="planilla.administrativa.asistencia.line",
        inverse_name="asistencia_id",
        string="",
        required=False,
    )
    #endregion

    #region Tiempo Extra a Pagar
    timepoExtraPagar_id = fields.One2many(
        string='Tiempo Extra a Pagar',
        tracking=True,
        comodel_name='planilla.administrativa.tiempo.extra.line',
        inverse_name='empleadosPlanillaLine_id',
    )
    tiempoAcumuladoDisponible = fields.Float(
        string="Tiempo acumulado disponible",
        required=False,
        compute='_get_tiempo_acumulado'
    )
    tiempoAcumuladoPagar = fields.Float(
        string="Tiempo a pagar",
        required=False,
    )
    def _get_tiempo_acumulado(self):
        self.tiempoAcumuladoDisponible = self.env['contrato.empleado.add.tiempo.acumulado.line'].search(['&',('empleado_id','=',self.empleado_id.id),
                                                                                                         ('periodoPago','=',self.name)]).tiempoAcumulado
    def agregar_tiempo_acumulado_pagar(self):
        if self.tiempoAcumuladoDisponible > 0 and self.tiempoAcumuladoPagar <= self.tiempoAcumuladoDisponible:
            tiempoAdd = self.env['contrato.empleado.add.tiempo.acumulado.line'].search(['&', ('empleado_id', '=', self.empleado_id.id),('periodoPago', '=', self.name)])
            contrato = self.env['contrato.empleado'].search([('empleado_id','=',self.empleado_id.id)])
            salarioXdia = (contrato.salario / 30)
            salarioXhora = (salarioXdia / 8)
            salarioXminuto = salarioXhora / 60
            totalTimepoAcumuladoPagar = (salarioXminuto * 1.5) * self.tiempoAcumuladoPagar

            vals = {
                'empleadosPlanillaLine_id' : self.id,
                'empleado_id': self.empleado_id.id,
                'periodoPago_id':self.peridoPago_id.id,
                'tiempoExtra':self.tiempoAcumuladoPagar,
                'totalTimepoAcumuladoPagar': totalTimepoAcumuladoPagar
            }
            self.timepoExtraPagar_id = [(0, 0, vals)]
            tiempoAdd.tiempoAcumulado -= self.tiempoAcumuladoPagar
            tiempoAdd.tiempoPagoExtra += self.tiempoAcumuladoPagar
            self.tiempoAcumuladoPagar = False
    #endregion

    @api.onchange('empleado_id')
    def _get_salario(self):
        self.salarioBase = 00

    @api.model
    def create(self,vals):
        res = super(PlanillaPersonalPeriodoPago, self).create(vals)
        return res

class PlanillaPersonalIncapacidadLine(models.Model):
    _name = "planilla.personal.incapacidad.line"
    _description = "Incapacidades del Empleado"

    empleadosPlanillaLine_id = fields.Many2one(
        string='Empleado Line',
        required=True,
        comodel_name='planilla.personal.empleados.planilla',
        ondelete="cascade"
    )
    empleado_id = fields.Many2one(
        required=True,
        comodel_name='hr.employee',
    )
    periodoPago_id = fields.Many2one(
        required=True,
        comodel_name='planilla.personal.periodo.pago',
    )

    tipoIncapacidad = fields.Char(
        string="Tipo Incapacidad",
        required=False,
    )
    totalDiasIncapacidad = fields.Integer(
        string="Total de dias de incapacidad",
        required=True,
    )
    diasIncapacidad = fields.Integer(
        string="Dias de incapacidad",
        required=True,
    )
    diasIncapacidadRebajas = fields.Integer(
        string="Dias de Rebaja Total",
        required=True,
    )
    fechaInicioIncapacidad = fields.Date(
        string="Fecha de inicio de incapacidad",
        required=True,
    )
    fechaFinIncapacidad = fields.Date(
        string="Fecha de finalizacion de incapacidad",
        required=True,
    )
    numeroBoletaIncapacidad = fields.Char(
        string="Numero de boleta",
        required=True,
    )

class PlanillaPersonalVacacionesLine(models.Model):
    _name = "planilla.personal.vacaciones.line"
    _description = "Vacaciones del Empleado"

    empleadosPlanillaLine_id = fields.Many2one(
        string='Empleado Line',
        required=True,
        comodel_name='planilla.personal.empleados.planilla',
        ondelete="cascade"
    )

    empleado_id = fields.Many2one(
        required=True,
        comodel_name='hr.employee',
    )
    periodoPago_id = fields.Many2one(
        required=True,
        comodel_name='planilla.personal.periodo.pago',
    )
    fechaInicioVacaciones = fields.Date(
        string="Fecha inicio de vacaciones",
        required=False,
    )
    fechaFinVacaciones = fields.Date(
        string="Fecha final de vacaciones",
        required=False,
    )
    diasVacaciones = fields.Integer(
        string="",
        required=False,
    )

class PlanillaPersonalPrestamosLine(models.Model):
    _name="planilla.personal.prestamos.line"
    _description = "Prestamos del Empleado"

    empleadosPlanillaLine_id = fields.Many2one(
        string='Empleado Line',
        comodel_name='planilla.personal.empleados.planilla',
        ondelete="cascade"
    )
    empleado_id = fields.Many2one(
        string='Empleado Line',
        required=False,
        comodel_name='hr.employee',
    )
    periodoPago_id = fields.Many2one(
        required=False,
        comodel_name='planilla.personal.periodo.pago',
    )
    descripcion = fields.Text(
        string="Descripcion",
        required=False,
    )
    montoPago = fields.Float(
        string="Monto del pago",
        required=False,
    )

class PlanillaAdministrativaAsistenciaLine(models.Model):
    _name="planilla.administrativa.asistencia.line"
    _description = "Asistencia del Empleado"

    asistencia_id = fields.Many2one(
        string='Empleado Line',
        required=True,
        comodel_name='planilla.personal.empleados.planilla',
        ondelete="cascade"
    )
    empleado_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Empleado",
        required=True,
    )
    aplicar = fields.Boolean(
        string="Aplicar",
    )
    diaMarca = fields.Date(
        string="Dia Marca",
        required=False,
    )
    horario = fields.Char(
        string="Horario",
        required=False,
    )
    entradaLaboral = fields.Datetime(
        string="Marca de entrada",
        required=False,
    )
    salidaLaboral = fields.Datetime(
        string="Marca de salida",
        required=False,
    )
    tiempoLaboral = fields.Float(
        string="Tiempo de laboral",
        required=False,
    )
    tiempoExtra = fields.Float(
        string="Tiempo de extra",
        required=False,
    )
    estado = fields.Char(
        string="Estado",
        required=False,
    )
    deduccionEntradaTardia = fields.Float(
        string="Monto Deduccion",
        required=False,
        digits=(16, 2)
    )
    deduccionSalidaTemprana = fields.Float(
        string="Monto Deduccion",
        required=False,
        digits=(16, 2)
    )
    deduccionOmisionMarca = fields.Float(
        string="Monto Deduccion",
        required=False,
        digits=(16, 2)
    )
    deduccionAusencia = fields.Float(
        string="Monto Deduccion",
        required=False,
        digits=(16, 2)
    )
    deduccionCafeM = fields.Float(
        string="Monto Deduccion Cafe Mañana",
        required=False,
        digits=(16, 2)
    )
    deduccionCafeT = fields.Float(
        string="Monto Deduccion Cafe Tarde",
        required=False,
        digits=(16, 2)
    )
    deduccionAlmuerzo = fields.Float(
        string="Monto Deduccion Almuerzo",
        required=False,
        digits=(16, 2)
    )
    deduccionTotal = fields.Float(
        string="Monto Deduccion",
        required=False,
        digits=(16, 2)
    )

class PlanillaAdministrativaTiempoExtra(models.Model):
    _name="planilla.administrativa.tiempo.extra.line"
    _description = "Tiempo Extra del Empleado"

    empleadosPlanillaLine_id = fields.Many2one(
        string='Empleado Line',
        required=True,
        comodel_name='planilla.personal.empleados.planilla',
        ondelete="cascade"
    )

    empleado_id = fields.Many2one(
        required=True,
        comodel_name='hr.employee',
    )
    periodoPago_id = fields.Many2one(
        required=True,
        comodel_name='planilla.personal.periodo.pago',
    )

    tiempoExtra = fields.Float(
        string="Tiempo a Pagar",
        required=False,
    )
    totalTimepoAcumuladoPagar = fields.Float(
        string="Total a pagar",
        required=False,
    )