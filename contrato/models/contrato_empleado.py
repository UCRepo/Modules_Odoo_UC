# -*- coding:utf-8 -*-

from dateutil.relativedelta import relativedelta
from datetime import date, timedelta, datetime
from odoo.exceptions import ValidationError
from odoo import api, fields, models


class ContratoEmpleado(models.Model):
    _name = "contrato.empleado"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description= "Contrato de empleado"

    #region Campos Generales
    puestoTrabajo = fields.Many2one(
        comodel_name="hr.job",
        string="Puesto",
        required=True,
        tracking=True
    )
    name = fields.Char(
        string="Nombre",
        required=False,
    )
    empleado_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Empleado",
        required=True,
        tracking=True
    )
    jefaturaInmediata_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Jefatura inmediata",
        tracking=True
    )
    jefaturaInmediataDelegado_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Delegado",
        tracking=True
    )
    jefaturaRH_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Jefatura RH",
        tracking=True
    )
    salario = fields.Monetary(
        string="Salario",
        required=True,
        tracking=True,
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        readonly=True,
        default=lambda self: self.env.company.currency_id
    )
    otrosCargos = fields.Float(
        string="Otros Cargos",
        required=True,
        tracking=True
    )
    jornadaLaboral = fields.Float(
        string="Jornada Semanal",
        required=False,
    )
    tiempoAlmuerzo = fields.Selection(
        string="Tiempo de almuerzo",
        selection=[
            ('30', '30min'),
            ('45', '45min'),
            ('60', '1h'),
            ('90', '1:30h'),
        ],
        required=False,
    )
    fechaContratacion = fields.Date(
        string="Fecha contratacion",
        required=True,
        tracking=True
    )
    fechaSalida = fields.Date(
        string="Fecha de salida",
        tracking=True
    )
    condicionSalida = fields.Selection(
        string="Condicion de salida",
        selection=[
            ('conRes', 'Con responsabilidad patronal'),
            ('sinRes', 'Sin responsabilidad patronal'),
            ('renun', 'Renuncia'),
        ],
        required=False,
    )
    comentarioSalida = fields.Text(
        string="Comentario de salida",
        required=False,
    )

    totalVacaciones = fields.Float(
        string="Total de vacaciones",
        required=False,
        store=True,
    )
    vacacionesTomadas = fields.Float(
        string="Vacaciones tomadas",
        required=False,
    )
    vacacionesRestantes = fields.Float(
        string="Vacaciones Restantes",
        required=False,
        store=True,
    )
    pensionado = fields.Boolean(
        string="Pensionado",
        default = False
    )
    embargo = fields.Boolean(
        string="Embargo",
        default = False
    )
    pensionAlimenticia = fields.Boolean(
        string="Pensión Alimenticia",
        default = False
    )
    codigoMarca = fields.Integer(
        string="Codigo marca",
        required=False,
    )
    marca = fields.Boolean(
        string="Marca",
        default = True,
    )
    almuerzo = fields.Boolean(
        string="Utiliza Almuerzo",
        default = True,
    )
    tiempoAcumuladoTotal = fields.Float(
        string="Tiempo Total",
        required=False,
    )
    tiempoAcumuladoTomado = fields.Float(
        string="Tiempo Tomado",
        required=False,
    )
    tiempoAcumuladoRestante = fields.Float(
        string="Tiempo Restante",
        required=False,
    )

    manejoHorario = fields.Many2many(
        comodel_name="hr.employee",
        relation="contrato_empleado_horarios_rel",
        string="Manejo de Horarios",
    )

    cuentaBac = fields.Char(
        string="Cuenta BAC",
        required=False,
    )
    cuentaBacActiva = fields.Boolean(
        string="Cuenta BAC Activa",
        default = True
    )
    justificaMarca = fields.Boolean(
        string="Justifica Marca",
        default = False
    )
    cargaAdicionales = fields.Boolean(
        string="Carga Adicionales",
        default = False
    )
    cargaAjustes = fields.Boolean(
        string="Carga Ajustes",
        default = False
    )
    #endregion

    #region MovimientosLaborales
    movimientosLaborales = fields.One2many(
        comodel_name="contrato.empleado.movimientos.laborales.line",
        inverse_name="contrato_id",
        string="Movimientos Laborales",
        required=False,
    )
    nuevoPuesto = fields.Many2one(
        comodel_name="hr.job",
        string="Nuevo Puesto",
        required=False,
    )
    condicionMovimiento = fields.Selection(
        string="Condicion movimiento",
        selection=[
            ('Ascenso', 'Ascenso'),
            ('Traslado', 'Traslado'),
            ('Ajuste Salarial', 'Ajuste Salarial'),
        ],
        required=False,
    )
    fechaMovimiento = fields.Date(
        string="Fecha Movimiento",
        required=False,
    )

    def add_movimiento_laborar(self):
        """
            Metodo para aregar los movimientos laborales
        :return:
        """
        self.movimientosLaborales = [(0, 0, {'contrato_id':self.id,
                                             'empleado_id': self.empleado_id.id,
                                             'tipoMovimiento': self.condicionMovimiento,
                                             'salario': self.salario,
                                             'fechaMovimiento': self.fechaMovimiento,
                                             'nuevoPuesto': self.nuevoPuesto.id
                                             })]

    #endregion

    #region Prestamos
    prestamos_ids = fields.One2many(
        comodel_name="contrato.empleado.prestamos.line",
        inverse_name="contrato_id",
        string="Prestamos",
        required=False,
    )
    fechaCreacionPrestamo = fields.Date(
        string="Fecha de creacion",
        required=False,
    )
    descripcion = fields.Text(
        string="Descripcion",
        required=False,
    )
    montoTotal = fields.Float(
        string="Monto Total",
        required=False,
    )
    numeroPagos = fields.Integer(
        string="Numero de pagos",
        required=False,
    )

    def add_prestamo(self):
        """
        Agerega un Prestamo al contrato del empleado
        :return:
        """
        montoPago = self.montoTotal / self.numeroPagos

        self.prestamos_ids = [(0, 0, {'contrato_id': self.id,
                                      'empleado_id': self.empleado_id.id,
                                      'fechaCreacion': self.fechaCreacionPrestamo,
                                      'descripcion': self.descripcion,
                                      'montoTotal': self.montoTotal,
                                      'numeroPagos': self.numeroPagos,
                                      'montoPago': montoPago,
                                      'totalCancelado': 0,
                                      'pagoFinalizado': False,
                                      })]
    #endregion

    #region Vacaciones

    #region Vacaciones Solicitdas
    vacaciones_ids = fields.One2many(
        comodel_name="contrato.empleado.vacaciones.line",
        inverse_name="contratoEmpleado_id",
        string="Vacaciones",
        required=False,
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
        string="Dias de Vacaciones",
        required=False,
    )

    def add_vacaciones(self):
        """
        Agrega vacciones a la lista
        :return:
        """
        for solicitudVacaciones in self.vacaciones_ids:
            datas = {
                'vacacionesid': solicitudVacaciones.id,
            }
        if self.diasVacaciones >= 0:
            vacacionesRestantes  = self.vacacionesRestantes
            if vacacionesRestantes >= self.diasVacaciones:
                self.vacaciones_ids = [(0, 0, {'contratoEmpleado_id': self.id,
                                               'empleado_id': self.empleado_id.id,
                                               'fechaInicioVacaciones': self.fechaInicioVacaciones,
                                               'fechaFinVacaciones': self.fechaFinVacaciones,
                                               'diasVacaciones': self.diasVacaciones,
                                               'estado': 'En proceso',
                                               'peticion': True,
                                               'aceptaionJefatura': False,
                                               'aceptaionJefaturaRH': False,
                                               'razon': '',
                                               })]

                self.vacacionesTomadas += self.diasVacaciones
                self.vacacionesRestantes -= self.diasVacaciones


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

    #region Vacaciones Agregadas
    vacacionesAdd_ids = fields.One2many(
        comodel_name="contrato.empleado.add.vacaciones.line",
        inverse_name="contratoEmpleado_id",
        string="Vacaciones",
        required=False,
    )
    fechaCorteAcumulacionVacaciones = fields.Date(
        string="Fecha de corte",
        required=False,
    )

    razon = fields.Char(
        string="Razón",
        required=False,
    )

    vacacionesAcumuladas = fields.Float(
        string="Vacaciones a acumular",
        required=False,
    )

    def add_acumulacion_vacaciones(self):
        """
            Metodo para aregar vacaciones  por corte de mes
        :return:
        """
        self.vacacionesAdd_ids = [(0, 0, {'contratoEmpleado_id':self.id,
                                          'empleado_id': self.empleado_id.id,
                                          'fechaCorteAcumulacion': self.fechaCorteAcumulacionVacaciones,
                                          'razon': self.razon,
                                          'vacacionesAcumuladas': self.vacacionesAcumuladas,
                                          })]
        self.totalVacaciones += self.vacacionesAcumuladas
        self.vacacionesRestantes += self.vacacionesAcumuladas
        self.fechaCorteAcumulacion = False
        self.razon = False
        self.vacacionesAcumuladas = False
    #endregion

    #endregion

    #region Incapacidades
    incapacidades_ids = fields.One2many(
        string='Incapacidades',
        tracking=True,
        required=False,
        comodel_name='contrato.empleado.incapacidad.line',
        inverse_name='contratoEmpleado_id',
    )
    fechaInicioIncapacidad = fields.Date(
        string="Fecha de inicio de incapacidad",
        required=False,
    )
    fechaFinIncapacidad = fields.Date(
        string="Fecha de finalizacion de incapacidad",
        required=False,
    )
    numeroBoletaIncapacidad = fields.Char(
        string="Numero de boleta",
        required=False,
    )
    tipoIncapacidad = fields.Selection(
        string="Tipo de incapacidad",
        selection=[
            ('INS', 'INS'),
            ('MAT', 'MAT'),
            ('SEM', 'SEM'),
        ],
        required=False,
    )

    def add_incapacidad(self):
        """
            Agrega una incapacidad a la lista
        :return:
        """
        totalDiasIncapacidad = (self.fechaFinIncapacidad - self.fechaInicioIncapacidad).days+1
        totalDiasPaga = 0
        totalDiasNoPago = 0
        if self.tipoIncapacidad == 'INS':
            totalDiasNoPago = totalDiasIncapacidad
        elif self.tipoIncapacidad == 'MAT':
            print('dfff')
        else:
            if totalDiasIncapacidad <= 3:
                totalDiasPaga = totalDiasIncapacidad
            else:
                totalDiasPaga = 3
                totalDiasNoPago = totalDiasIncapacidad -3

        self.incapacidades_ids = [(0, 0, { 'contratoEmpleado_id': self.id,
                                           'empleado_id': self.empleado_id.id,
                                           'tipoIncapacidad': self.tipoIncapacidad,
                                           'numeroBoletaIncapacidad': self.numeroBoletaIncapacidad,
                                           'totalDiasIncapacidad': totalDiasIncapacidad,
                                           'diasIncapacidad': totalDiasPaga,
                                           'diasIncapacidadRebajas': totalDiasNoPago,
                                           'fechaInicioIncapacidad': self.fechaInicioIncapacidad,
                                           'fechaFinIncapacidad': self.fechaFinIncapacidad
                                           })]
        self.tipoIncapacidad = False
        self.fechaInicioIncapacidad = False
        self.fechaFinIncapacidad = False
        self.numeroBoletaIncapacidad = ""

    #endregion

    # region Licencias
    licencias_ids = fields.One2many(
        string='Licencias',
        tracking=True,
        required=False,
        comodel_name='contrato.empleado.licencias.line',
        inverse_name='contratoEmpleado_id',
    )
    tipoLicencia = fields.Selection(
        string="Tipo de Licencia",
        selection=[
            ('Sin goce salarial', 'Sin goce salarial'),
            ('Con goce salarial', 'Con goce salarial'),
            ('Matrimonio', 'Matrimonio'),
            ('Muerte de un familiar', 'Muerte de un familiar'),
            ('Paternidad', 'Paternidad'),
            ('Maternidad', 'Maternidad'),
        ],
        required=False,
    )
    fechaInicioLicencia = fields.Date(
        string="Fecha de inicio de licencia",
        required=False,
    )
    fechaFinLicencia = fields.Date(
        string="Fecha de finalizacion de licencia",
        required=False,
    )
    tipoPago = fields.Selection(
        string="Tipo de Pago",
        selection=[
            ('Sin pago', 'Sin pago'),
            ('Pago medio', 'Pago medio'),
            ('Pago completo', 'Pago completo'),
        ],
        required=False,
    )

    def add_licencia(self):
        """
            Agrega una incapacidad a la lista
        :return:
        """

        self.licencias_ids = [(0, 0, {'empleado_id': self.empleado_id.id,
                                      'tipoLicencia': self.tipoLicencia,
                                      'fechaInicioLicencia': self.fechaInicioLicencia,
                                      'fechaFinLicencia': self.fechaFinLicencia,
                                      'tipoPago': self.tipoPago,
                                      })]
        self.tipoLicencia = False
        self.fechaInicioLicencia = False
        self.fechaFinLicencia = False
        self.tipoPago = False

    # endregion

    #region Timepo Acumulado

    #region Tiempo Acumulado Tomado
    timepoAcumulado_ids = fields.One2many(
        comodel_name="contrato.empleado.tiempo.acumulado.line",
        inverse_name="contratoEmpleado_id",
        string="Timepo Acumulado",
        required=False,
    )
    fechaTiempoAcumulado = fields.Date(
        string="Fecha",
        required=False,
    )
    tiempoTomar = fields.Selection(
        string="Tiempo a tomar",
        selection=[
            ('30', '0,5h'),
            ('60', '1h'),
            ('90', '1,5h'),
            ('120', '2h'),
            ('150', '2,5h'),
            ('180', '3h'),
            ('210', '3,5h'),
            ('240', '4h'),
            ('270', '4,5h'),
            ('300', '5h'),
            ('330', '5,5h'),
            ('360', '6h'),
            ('390', '6,5h'),
            ('420', '7h'),
            ('450', '7,5h'),
            ('480', '8h'),
            ('510', '8,5h'),
            ('540', '9h'),
            ('570', '9,5h'),
            ('600', '10h'),
        ],
        required=False,
    )
    inicioFinJornada= fields.Selection(
        string="Jornada",
        selection=[
            ('inicioJornada', 'Inicio de jornada'),
            ('finJornada', 'Fin de jornada'),
        ],
        required=False,
    )

    def add_tiempo_acumulado(self):
        """
        Agrega tiempo acomulado a la lista
        :return:
        """
        if float(self.tiempoTomar) > 0:
            tiempoAcumuladoRestante  = self.tiempoAcumuladoRestante
            if tiempoAcumuladoRestante >= float(self.tiempoTomar):
                self.timepoAcumulado_ids = [(0, 0, {'contratoEmpleado_id': self.id,
                                                    'empleado_id': self.empleado_id.id,
                                                    'fechaTiempoAcumulado': self.fechaTiempoAcumulado,
                                                    'tiempoAcumuladoTomado': float(self.tiempoTomar),
                                                    'inicioFinJornada': self.inicioFinJornada,
                                                    'estado': 'En proceso',
                                                    'peticion': True,
                                                    'aceptaionJefatura': False,
                                                    'aceptaionJefaturaRH': False,
                                                    'razon': '',
                                                    })]

                self.tiempoAcumuladoTomado += float(self.tiempoTomar)
                self.tiempoAcumuladoRestante -= float(self.tiempoTomar)


                self.fechaTiempoAcumulado = False
                self.tiempoTomar = 0
            else:
                raise ValidationError("Ud solo tiene "+str(tiempoAcumuladoRestante)+" h restantes de tiempo acumulado")
    #endregion

    #region Tiempo Acumulado Agregado
    timepoAcumuladoAdd_ids = fields.One2many(
        comodel_name="contrato.empleado.add.tiempo.acumulado.line",
        inverse_name="contratoEmpleado_id",
        string="Timepo Acumulado",
        required=False,
    )
    tiempoAgregar = fields.Selection(
        string="Tiempo a tomar",
        selection=[
            ('30', '0,5h'),
            ('60', '1h'),
            ('90', '1,5h'),
            ('120', '2h'),
            ('150', '2,5h'),
            ('180', '3h'),
            ('210', '3,5h'),
            ('240', '4h'),
            ('270', '4,5h'),
            ('300', '5h'),
            ('330', '5,5h'),
            ('360', '6h'),
            ('390', '6,5h'),
            ('420', '7h'),
            ('450', '7,5h'),
            ('480', '8h'),
            ('510', '8,5h'),
            ('540', '9h'),
            ('570', '9,5h'),
            ('600', '10h'),
        ],
        required=False,
    )

    fechaCorteAcumulacion = fields.Date(
        string="Fecha de corte",
        required=False,
    )

    def set_tiempo_agregado_agregar(self):
        """
            Metodo para aregar el tiempo cumulado por corte de planilla
        :return:
        """
        self.timepoAcumuladoAdd_ids = [(0, 0, {'contratoEmpleado_id':self.id,
                                               'empleado_id': self.empleado_id.id,
                                               'fechaCorteAcumulacion': self.fechaCorteAcumulacion,
                                               'periodoPago': 'Movimiento RH',
                                               'tiempoAcumulado': float(self.tiempoAgregar),
                                               })]
        self.tiempoAcumuladoTotal += float(self.tiempoAgregar)
        self.tiempoAcumuladoRestante += float(self.tiempoAgregar)
    #endregion

    #endregion

    #region Embargos

    #region Embargo
    embargo_ids = fields.One2many(
        comodel_name="contrato.empleado.embargos.line",
        inverse_name="contratoEmpleado_id",
        string="Timepo Acumulado",
        required=False,
    )
    expediente = fields.Char(
        string="Expediente",
        required=False,
    )
    identificacionEmbargo = fields.Char(
        string="Identificación",
        required=False,
    )
    depositante = fields.Char(
        string="Depositante",
        required=False,
    )
    beneficiario = fields.Char(
        string="Beneficiario",
        required=False,
    )
    montoEmbargo = fields.Float(
        string="",
        required=False,
    )

    def add_embargo(self):
        if self.expediente != False and self.identificacionEmbargo != False and self.depositante != False and self.beneficiario != False and self.montoEmbargo != False:
            vals = {
                'name': self.depositante + ' Monto:' + ' ₡ '+"{:,}".format(self.montoEmbargo),
                'contratoEmpleado_id': self.id,
                'empleado_id': self.empleado_id.id,
                'expediente': self.expediente,
                'identificacion': self.identificacionEmbargo,
                'depositante': self.depositante,
                'beneficiario': self.beneficiario,
                'montoTotal': self.montoEmbargo,
                'monto': self.montoEmbargo,
            }

            self.embargo_ids = [(0,0,vals)]

            self.expediente = False
            self.identificacionEmbargo = False
            self.depositante = False
            self.beneficiario = False
            self.montoEmbargo = False
    #endregion

    #region Historial Pago Embargo
    embargoHistorialPago_ids = fields.One2many(
        comodel_name="contrato.empleado.embargos.historial.pago.line",
        inverse_name="contratoEmpleado_id",
        string="Timepo Acumulado",
        required=False,
    )
    embargo_id = fields.Many2one(
        required=False,
        comodel_name='contrato.empleado.embargos.line',
    )
    montoPagadoEmbargo = fields.Float(
        string="Monto a deducir",
        required=False,
    )

    def add_embargo_historial_pago(self):
        if self.empleado_id != False and self.montoPagadoEmbargo != False:
            vals = {
                'contratoEmpleado_id': self.id,
                'embargo_id': self.embargo_id.id,
                'empleado_id': self.empleado_id.id,
                'montoPagado': self.montoPagadoEmbargo,
                'fechaPago': datetime.date(),
            }
            self.embargoHistorialPago_ids = [(0,0,vals)]

            self.embargo_id.monto -= self.montoPagadoEmbargo

            self.embargo_id = False
            self.montoPagadoEmbargo = False


    #endregion

    #endregion

    #region metodos model
    @api.model
    def create(self,vals):
        """
            Metodos para crear un registro de contrato
        :param vals: valroes que se optiens del form
        :return:
        """
        if not self.movimientosLaborales:
            vals['movimientosLaborales'] = [(0, 0, {'empleado_id': vals['empleado_id'],
                                                    'tipoMovimiento': "Inicio",
                                                    'salario': vals['salario'],
                                                    'fechaMovimiento': vals['fechaContratacion'],
                                                    'nuevoPuesto': vals['puestoTrabajo']
                                                    })]
            vals['name'] = 'Contrato ' + self.env['hr.employee'].search([('id','=',vals['empleado_id'])]).name
            res = super(ContratoEmpleado, self).create(vals)
            return res
        else:
            raise ValidationError("No se puede guardar el registro")

    def write(self,vals):
        if 'vacaciones_ids' in vals:
            for data in vals['vacaciones_ids']:
                if data[0] == 2:
                    cantidadVacaionesEliminadas = self.env['contrato.empleado.vacaciones.line'].search([('id','=',data[1])]).diasVacaciones
                    contrato = self.env['contrato.empleado'].search([('empleado_id','=',self.empleado_id.id)])
                    contrato.vacacionesTomadas -=  cantidadVacaionesEliminadas
                    contrato.vacacionesRestantes += cantidadVacaionesEliminadas

        if 'vacacionesAdd_ids' in vals:
            for data in vals['vacacionesAdd_ids']:
                if data[0] == 2:
                    cantidadVacaionesEliminadas = self.env['contrato.empleado.add.vacaciones.line'].search([('id','=',data[1])]).vacacionesAcumuladas
                    contrato = self.env['contrato.empleado'].search([('empleado_id','=',self.empleado_id.id)])
                    contrato.totalVacaciones -=  cantidadVacaionesEliminadas
                    contrato.vacacionesRestantes -= cantidadVacaionesEliminadas

        if 'timepoAcumulado_ids' in vals:
            for data in vals['timepoAcumulado_ids']:
                if data[0] == 2:
                    cantidadTiempoAcumuladoEliminadas = self.env['contrato.empleado.tiempo.acumulado.line'].search([('id','=',data[1])]).tiempoAcumuladoTomado
                    contrato = self.env['contrato.empleado'].search([('empleado_id','=',self.empleado_id.id)])
                    contrato.tiempoAcumuladoTomado -=  cantidadTiempoAcumuladoEliminadas
                    contrato.tiempoAcumuladoRestante += cantidadTiempoAcumuladoEliminadas

        if 'timepoAcumuladoAdd_ids' in vals:
            for data in vals['timepoAcumuladoAdd_ids']:
                if data[0] == 2:
                    cantidadTiempoAcumuladoEliminadas = self.env['contrato.empleado.add.tiempo.acumulado.line'].search([('id','=',data[1])]).tiempoAcumulado
                    contrato = self.env['contrato.empleado'].search([('empleado_id','=',self.empleado_id.id)])
                    contrato.tiempoAcumuladoTotal -=  cantidadTiempoAcumuladoEliminadas
                    contrato.tiempoAcumuladoRestante -= cantidadTiempoAcumuladoEliminadas

        if 'embargoHistorialPago_ids' in vals:
            for data in vals['embargoHistorialPago_ids']:
                if data[0] == 2:
                    montoHistorialEmbargo = self.env['contrato.empleado.embargos.historial.pago.line'].search([('id','=',data[1])]).montoPagado
                    embargo = self.env['contrato.empleado.embargos.line'].search([('empleado_id','=',self.empleado_id.id)])
                    embargo.monto += montoHistorialEmbargo

        res = super(ContratoEmpleado, self).write(vals)

        return res

    @api.model
    def default_get(self, fields):
        vals = super(ContratoEmpleado, self).default_get(fields)
        empleado_id = self.env['hr.employee'].search([('id','=',self.env.context.get('active_id'))])
        if empleado_id:
            vals.update({
                'puestoTrabajo':empleado_id.job_id,
                'empleado_id':empleado_id.id,
            })
        return vals

    @api.constrains('salario')
    def _constrainsSalario(self):
        """
        Verifica que el salario sea correcto
        :return:
        """
        if self.salario <= 0 :
            raise ValidationError("El Salario no puede ser menor igual a 0")

    @api.onchange('fechaContratacion')
    def _onchangeFechaContratacion(self):
        """
            Al detectar un cambio de estado en la fecha de contratacion calcula las vacaciones
        :return:
        """
        if self.fechaContratacion != False:
            hoy = date.today()
            diasVacaciones = 0
            if hoy.day >= self.fechaContratacion.day:
                diasVacaciones = (hoy.year - self.fechaContratacion.year) * 12 + (
                        hoy.month - self.fechaContratacion.month)
            else:
                diasVacaciones = (hoy.year - self.fechaContratacion.year) * 12 + (
                        hoy.month - self.fechaContratacion.month) - 1

            self.totalVacaciones = diasVacaciones

    @api.onchange('vacacionesTomadas')
    def _vacaciones_restantes(self):
        self.vacacionesRestantes = self.totalVacaciones - self.vacacionesTomadas

    #endregion

class ContratoEmpleadoMovimientosLaboralesLine(models.Model):
    _name="contrato.empleado.movimientos.laborales.line"

    contrato_id = fields.Many2one(
        comodel_name="contrato.empleado",
        string="Movimientos",
        tracking=True,
        ondelete="cascade"
    )
    empleado_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Empleado",
        tracking=True
    )
    tipoMovimiento = fields.Char(
        string="Tipo movimiento",
        required=False,
    )
    salario = fields.Float(
        string="Salario",
        required=False,
    )
    fechaMovimiento = fields.Date(
        string="Fecha de movimiento",
        required=False,
    )
    nuevoPuesto = fields.Many2one(
        comodel_name="hr.job",
        string="Puesto",
        tracking=True
    )

class ContratoEmpleadoPrestamosLine(models.Model):
    _name="contrato.empleado.prestamos.line"

    contrato_id = fields.Many2one(
        comodel_name="contrato.empleado",
        string="Prestamos",
        tracking=True,
        ondelete="cascade"
    )
    empleado_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Empleado",
        tracking=True
    )
    fechaCreacion = fields.Date(
        string="Fecha de creacion",
        required=False,
    )
    descripcion = fields.Text(
        string="Descripcion",
        required=False,
    )
    montoTotal = fields.Float(
        string="Monto Total",
        required=False,
    )
    numeroPagos = fields.Integer(
        string="Cantidad de pagos",
        required=False,
    )
    montoPago = fields.Float(
        string="Monto del pago",
        required=False,
    )
    totalCancelado = fields.Float(
        string="Total Cancelado",
        required=False,
    )
    pagoFinalizado = fields.Boolean(
        string="Pago Finalizado",
        default=False
    )

class ContratoEmpleadoVacacionesLine(models.Model):
    _name = "contrato.empleado.vacaciones.line"
    _description = "Vacaciones del Empleado"

    contratoEmpleado_id = fields.Many2one(
        string='Empleado Line',
        required=True,
        comodel_name='contrato.empleado',
        ondelete="cascade"
    )

    empleado_id = fields.Many2one(
        required=True,
        comodel_name='hr.employee',
    )
    activo = fields.Boolean(
        string="Activo",
        default=True,
    )
    fechaInicioVacaciones = fields.Date(
        string="Fecha inicio de vacaciones",
        required=False,
    )
    fechaFinVacaciones = fields.Date(
        string="Fecha final de vacaciones",
        required=False,
    )
    fechaMedioDia = fields.Date(
        string="Fecha Medio Dia",
        required=False,
    )
    tipoMedioDia = fields.Selection(
        string="Tipo Jornada",
        selection=[
            ('Inicio de Jornada', 'Inicio de Jornada'),
            ('Fin de Jornada', 'Fin de Jornada'),
        ],
        required=False,
    )
    diasVacaciones = fields.Float(
        string="Dias",
        required=False,
    )
    razon = fields.Text(
        string="Razón",
        required=False,
    )
    estadoJefatura = fields.Selection(
        string="Tipo de Pago",
        selection=[
            ('Revisión pendiente', 'Revisión pago pendiente'),
            ('Aceptado', 'Aceptado'),
            ('Rechazado', 'Rechazado'),
        ],
        default="Revisión pendiente",
        required=False,
    )
    estadoRH = fields.Selection(
        string="Tipo de Pago",
        selection=[
            ('Revisión pendiente', 'Revisión pago pendiente'),
            ('Aceptado', 'Aceptado'),
            ('Rechazado', 'Rechazado'),
        ],
        default="Revisión pendiente",
        required=False,
    )
    fechaFirmaEmpleado = fields.Datetime(
        string="",
        required=False,
    )
    fechaFirmaJefatura = fields.Datetime(
        string="",
        required=False,
    )
    fechaFirmaRH= fields.Datetime(
        string="",
        required=False,
    )
    detailVacaciones_ids = fields.One2many(
        comodel_name="contrato.empleado.vacaciones.line.detail",
        inverse_name="masterVacacionesLine_id",
        string="Vacaciones",
        required=False,
    )

class ContratoEmpleadoVacacionesLineDetail(models.Model):
    _name = "contrato.empleado.vacaciones.line.detail"
    _description = "Vacaciones del Empleado"

    masterVacacionesLine_id = fields.Many2one(
        string='Empleado Line',
        required=True,
        comodel_name='contrato.empleado.vacaciones.line',
        ondelete="cascade"
    )

    fechaInicioVacaciones = fields.Date(
        string="Fecha inicio de vacaciones",
        required=False,
    )
    fechaFinVacaciones = fields.Date(
        string="Fecha final de vacaciones",
        required=False,
    )
    fechaMedioDia = fields.Date(
        string="Fecha Medio Dia",
        required=False,
    )
    tipoMedioDia = fields.Selection(
        string="Tipo Jornada",
        selection=[
            ('Inicio de Jornada', 'Inicio de Jornada'),
            ('Fin de Jornada', 'Fin de Jornada'),
        ],
        required=False,
    )
    diasVacaciones = fields.Float(
        string="Dias",
        required=False,
    )

class ContratoEmpleadoAddVacacionesLine(models.Model):
    _name = "contrato.empleado.add.vacaciones.line"
    _description = "Vacaciones del Empleado"

    contratoEmpleado_id = fields.Many2one(
        string='Empleado Line',
        required=True,
        comodel_name='contrato.empleado',
        ondelete="cascade"
    )

    empleado_id = fields.Many2one(
        required=True,
        comodel_name='hr.employee',
    )
    activo = fields.Boolean(
        string="Activo",
        default=True,
    )

    fechaCorteAcumulacion = fields.Date(
        string="Fecha de corte",
        required=False,
    )

    razon = fields.Char(
        string="Razón",
        required=False,
    )

    vacacionesAcumuladas = fields.Float(
        string="Vacaciones a acumular",
        required=False,
    )

class ContratoEmpleadoIncapacidadLine(models.Model):
    _name = "contrato.empleado.incapacidad.line"
    _description = "Incapacidades del Empleado"

    contratoEmpleado_id = fields.Many2one(
        string='Empleado Line',
        required=True,
        comodel_name='contrato.empleado',
        ondelete="cascade"
    )
    empleado_id = fields.Many2one(
        required=True,
        comodel_name='hr.employee',
    )
    activo = fields.Boolean(
        string="Activo",
        default=True,
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

class ContratoEmpleadoLicenciasLine(models.Model):
    _name = "contrato.empleado.licencias.line"
    _description = "Incapacidades del Empleado"

    contratoEmpleado_id = fields.Many2one(
        string='Empleado Line',
        required=True,
        comodel_name='contrato.empleado',
        ondelete="cascade"
    )
    empleado_id = fields.Many2one(
        required=True,
        comodel_name='hr.employee',
    )
    activo = fields.Boolean(
        string="Activo",
        default=True,
    )
    tipoLicencia = fields.Selection(
        string="Tipo de Licencia",
        selection=[
            ('Sin goce salarial', 'Sin goce salarial'),
            ('Con goce salarial', 'Con goce salarial'),
            ('Matrimonio', 'Matrimonio'),
            ('Muerte de un familiar', 'Muerte de un familiar'),
            ('Paternidad', 'Paternidad'),
            ('Maternidad', 'Maternidad'),
        ],
        required=False,
    )
    fechaInicioLicencia = fields.Date(
        string="Fecha de inicio de licencia",
        required=False,
    )
    fechaFinLicencia = fields.Date(
        string="Fecha de finalizacion de licencia",
        required=False,
    )
    tipoPago = fields.Selection(
        string="Tipo de Pago",
        selection=[
            ('Sin pago', 'Sin pago'),
            ('Pago medio', 'Pago medio'),
            ('Pago completo', 'Pago completo'),
        ],
        required=False,
    )
    estadoJefatura = fields.Selection(
        string="Tipo de Pago",
        selection=[
            ('Revisión pendiente', 'Revisión pago pendiente'),
            ('Aceptado', 'Aceptado'),
            ('Rechazado', 'Rechazado'),
        ],
        default="Revisión pendiente",
        required=False,
    )
    estadoRH = fields.Selection(
        string="Tipo de Pago",
        selection=[
            ('Revisión pendiente', 'Revisión pago pendiente'),
            ('Aceptado', 'Aceptado'),
            ('Rechazado', 'Rechazado'),
        ],
        default="Revisión pendiente",
        required=False,
    )
    razon = fields.Text(
        string="Razón",
        required=False,
    )
    fechaFirmaEmpleado = fields.Datetime(
        string="",
        required=False,
    )
    fechaFirmaJefatura = fields.Datetime(
        string="",
        required=False,
    )
    fechaFirmaRH= fields.Datetime(
        string="",
        required=False,
    )
    fechaPaternidad_1 = fields.Date(
        string="Fecha Paternidad #1",
        required=False,
    )
    fechaPaternidad_2 = fields.Date(
        string="Fecha Paternidad #2",
        required=False,
    )
    fechaPaternidad_3 = fields.Date(
        string="Fecha Paternidad #3",
        required=False,
    )
    fechaPaternidad_4 = fields.Date(
        string="Fecha Paternidad #4",
        required=False,
    )
    fechaPaternidad_5 = fields.Date(
        string="Fecha Paternidad #5",
        required=False,
    )
    fechaPaternidad_6 = fields.Date(
        string="Fecha Paternidad #6",
        required=False,
    )
    fechaPaternidad_7 = fields.Date(
        string="Fecha Paternidad #7",
        required=False,
    )
    fechaPaternidad_8 = fields.Date(
        string="Fecha Paternidad #8",
        required=False,
    )

class ContratoEmpleadoTiempoAcumuladoTomadoLine(models.Model):
    _name = "contrato.empleado.tiempo.acumulado.line"
    _description = "Tiempo Acumulado del Empleado"

    contratoEmpleado_id = fields.Many2one(
        string='Empleado Line',
        required=True,
        comodel_name='contrato.empleado',
        ondelete="cascade"
    )

    empleado_id = fields.Many2one(
        required=True,
        comodel_name='hr.employee',
    )
    activo = fields.Boolean(
        string="Activo",
        default=True,
    )
    fechaDesdeTiempoAcumulado = fields.Date(
        string="Fecha",
        required=False,
    )
    fechaHastaTiempoAcumulado = fields.Date(
        string="Fecha",
        required=False,
    )
    tiempoAcumuladoTomado= fields.Float(
        string="Tiempo",
        required=False,
    )
    diasAcumuladoTomado= fields.Float(
        string="Tiempo",
        required=False,
    )
    inicioFinJornada = fields.Char(
        string="Jornada",
        required=False,
    )
    razon = fields.Text(
        string="Razón",
        required=False,
    )
    estado = fields.Char(
        string="Estado",
        required=False,
    )
    peticion = fields.Boolean(
        string="Peticion",
    )
    estadoJefatura = fields.Selection(
        string="Tipo de Pago",
        selection=[
            ('Revisión pendiente', 'Revisión pendiente'),
            ('Aceptado', 'Aceptado'),
            ('Rechazado', 'Rechazado'),
        ],
        default="Revisión pendiente",
        required=False,
    )
    estadoRH = fields.Selection(
        string="Tipo de Pago",
        selection=[
            ('Revisión pendiente', 'Revisión pendiente'),
            ('Aceptado', 'Aceptado'),
            ('Rechazado', 'Rechazado'),
        ],
        default="Revisión pendiente",
        required=False,
    )
    fechaFirmaEmpleado = fields.Datetime(
        string="",
        required=False,
    )
    fechaFirmaJefatura = fields.Datetime(
        string="",
        required=False,
    )
    fechaFirmaRH= fields.Datetime(
        string="",
        required=False,
    )

class ContratoEmpleadoAddTiempoAcumuladoLine(models.Model):
    _name = "contrato.empleado.add.tiempo.acumulado.line"
    _description = "Tiempo Acumulado del Empleado"

    contratoEmpleado_id = fields.Many2one(
        string='Empleado Line',
        required=True,
        comodel_name='contrato.empleado',
        ondelete="cascade"
    )

    empleado_id = fields.Many2one(
        required=True,
        comodel_name='hr.employee',
    )
    activo = fields.Boolean(
        string="Activo",
        default=True,
    )

    fechaCorteAcumulacion = fields.Date(
        string="Fecha de corte",
        required=False,
    )

    periodoPago = fields.Char(
        string="Periodo de pago",
        required=False,
    )

    tiempoAcumulado = fields.Float(
        string="Tiempo a acumular",
        required=False,
    )
    tiempoPagoExtra = fields.Float(
        string="Tiempo extra a pagar",
        required=False,
    )

class ContratoEmpleadoEmbargos(models.Model):
    _name = "contrato.empleado.embargos.line"
    _description = "Embargos del Empleado"

    name = fields.Char(
        string="Nombre",
        required=False,
    )

    contratoEmpleado_id = fields.Many2one(
        string='Empleado Line',
        required=True,
        comodel_name='contrato.empleado',
        ondelete="cascade"
    )

    empleado_id = fields.Many2one(
        required=True,
        comodel_name='hr.employee',
    )
    activo = fields.Boolean(
        string="Activo",
        default=False,
    )
    expediente = fields.Char(
        string="Expediente",
        required=False,
    )
    identificacion = fields.Char(
        string="Identificación",
        required=False,
    )
    depositante = fields.Char(
        string="Depositante",
        required=False,
    )
    beneficiario = fields.Char(
        string="Beneficiario",
        required=False,
    )
    montoTotal = fields.Float(
        string="Monto Total",
        required=False,
    )
    monto = fields.Float(
        string="Monto",
        required=False,
    )

class ContratoEmpleadoEmbargosHistorialPagos(models.Model):
    _name = "contrato.empleado.embargos.historial.pago.line"
    _description = "Embargos del Empleado"

    contratoEmpleado_id = fields.Many2one(
        string='Empleado Line',
        required=True,
        comodel_name='contrato.empleado',
        ondelete="cascade"
    )
    fechaPago = fields.Date(
        string="",
        required=False,
    )
    embargo_id = fields.Many2one(
        required=True,
        comodel_name='contrato.empleado.embargos.line',
    )
    empleado_id = fields.Many2one(
        required=True,
        comodel_name='hr.employee',
    )
    montoPagado = fields.Float(
        string="",
        required=False,
    )
    activo = fields.Boolean(
        string="Activo",
        default=True,
    )


