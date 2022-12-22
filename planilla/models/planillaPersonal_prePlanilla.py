# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime
import socket
import requests
import json
import base64

class PlanillaAdministrativaPrePlanilla(models.Model):
    _name = "planilla.administrativa.pre.planilla"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Planilla Administrativa"

    periodoPago_id = fields.Many2one(
        string='Periodo de pago',
        tracking=True,
        required=True,
        comodel_name='planilla.personal.periodo.pago',
    )
    planillaCuatrimestre_id = fields.Many2one(
        string='Calculo renta docente',
        tracking=True,
        required=False,
        comodel_name='planilla.cuatrimestre',
    )
    miembrosPlanilla_id = fields.One2many(
        string='Miembros',
        comodel_name='planilla.administrativa.pre.planilla.line',
        inverse_name='prePlanilla_id',
    )
    pago = fields.Char(
        string="",
        required=False,
    )
    desde = fields.Date(
        string="Desde",
        required=False,
    )
    hasta = fields.Date(
        string="Hasta",
        required=False,
    )

    def generar_pre_planilla(self):

        empleadosPlanilla = self.env['planilla.personal.empleados.planilla'].search(['&',('pago','=',self.pago),('peridoPago_id','=',self.periodoPago_id.id)])
        calculosPlanilla = self.env['configuraciones'].search([])

        for empleado in empleadosPlanilla:

            contratoEmpleado = self.env['contrato.empleado'].search([('empleado_id', '=', empleado.empleado_id.id)])

            deduccionAsistencia = 0
            tiempoExtraPagar = 0
            deduccionPrestamos = 0
            embargo = 0
            renta = 0
            if empleado.asistencia_line_ids:
                vals = {
                    'prePlanilla_id': self.id,
                    'empleado_id': empleado.empleado_id.id,
                    'periodo_id': self.periodoPago_id.id,
                    'nombreEmpleado': empleado.empleado_id.name,
                    'correoEmpleado': empleado.empleado_id.work_email,
                    'cedulaEmpleado': empleado.empleado_id.identification_id,
                    'telefonoEmpleado': empleado.empleado_id.work_phone,
                    'salarioBruto': empleado.salarioBase,
                    'diasPagoCompleto': empleado.diasPagoCompleto,
                    'diasPagoMedio': empleado.diasPagoMitad,
                    'diasPagoNulo': empleado.diasSinPago,
                    'pagoEfectuado': False
                }
                for asistencia in empleado.asistencia_line_ids:
                    if asistencia.aplicar == True:
                        deduccionAsistencia += asistencia.deduccionTotal

                for extra in empleado.timepoExtraPagar_id:
                    tiempoExtraPagar += extra.totalTimepoAcumuladoPagar

                salarioBruto = empleado.salarioBase
                salarioBruto /= 2
                salarioBruto += tiempoExtraPagar
                salarioBruto -= deduccionAsistencia

                salarioNeto = salarioBruto
                if contratoEmpleado.pensionado == False:
                    vals.update({
                        'CCSSEmpleado': salarioBruto * calculosPlanilla.CCSSNormal
                    })

                else:
                    vals.update({
                        'CCSSEmpleado': salarioBruto * calculosPlanilla.CCSSNormal
                    })

                salarioNeto -= vals['CCSSEmpleado']


                sumaRentaDocente = empleado.salarioBase
                if self.planillaCuatrimestre_id != False:
                    sumaRentaDocente += self.env['planilla.cuatrimestre.line'].search(['&',('docentesLinea_id','=',self.planillaCuatrimestre_id.id),
                                                                                      ('cedulaDocente','=',empleado.empleado_id.identification_id),
                                                                                      ('rentaDocente','<=',0)]).totalDocente


                renta = (self._get_renta(calculosPlanilla,empleado.salarioBase))/2
                rentaDocente =  (self._get_renta(calculosPlanilla,sumaRentaDocente) - renta) / 2

                vals.update({
                    'rentaEmpleado':renta,
                    'rentaEmpleadoDocente':rentaDocente,
                })
                salarioNeto -= empleado.montoPension

                for prestamo in empleado.prestamos_ids:
                        deduccionPrestamos += asistencia.montoPago

                salarioNeto -= deduccionPrestamos


                if contratoEmpleado.embargo:
                    preCalculo  = salarioNeto - calculosPlanilla.salarioBase
                    if preCalculo > 1000:
                        embargo = preCalculo * calculosPlanilla.porcientoRebajoEmbargo
                        contratoEmpleado.embargoHistorialPago_ids
                        val = {
                            'contratoEmpleado_id': contratoEmpleado.id,
                            'embargo_id': contratoEmpleado.embargo_id.id,
                            'empleado_id': contratoEmpleado.empleado_id.id,
                            'montoPagado': embargo,
                            'fechaPago': datetime.today() + timedelta(hours=6),
                        }
                        contratoEmpleado.embargoHistorialPago_ids = [(0,0,val)]

                salarioNeto -= embargo
                salarioNeto -= renta
                salarioNeto -= rentaDocente

                vals.update({
                    'salarioNeto': salarioNeto,
                    'embargo': embargo,
                    'pension': empleado.montoPension,
                    'deduccionAsistencia': deduccionAsistencia,
                    'totalDeduccion': embargo + renta + rentaDocente + deduccionAsistencia + vals['CCSSEmpleado'] ,
                })
                miembros = self.miembrosPlanilla_id
                empleadoPrePlanilla = list(filter(lambda x: (x.empleado_id.id == vals['empleado_id']),miembros))
                if empleadoPrePlanilla:
                    self.miembrosPlanilla_id = [(1, empleadoPrePlanilla[0].id, vals)]
                else:
                    self.miembrosPlanilla_id = [(0, 0, vals)]

    def _get_renta(self,calculosPlanilla,salarioNeto):
        renta = 0
        vals = {
            'rentaEmpleado': 0
        }
        if salarioNeto > calculosPlanilla.desde0 and salarioNeto < calculosPlanilla.hasta0:

            renta += (salarioNeto - calculosPlanilla.desde0) * calculosPlanilla.porciento0

        elif salarioNeto > calculosPlanilla.desde1 and salarioNeto < calculosPlanilla.hasta1:

            renta += (calculosPlanilla.hasta0 - calculosPlanilla.desde0) * calculosPlanilla.porciento0
            renta += (salarioNeto - calculosPlanilla.desde1) * calculosPlanilla.porciento1

        elif salarioNeto > calculosPlanilla.desde2 and salarioNeto < calculosPlanilla.hasta2:

            renta += (calculosPlanilla.hasta0 - calculosPlanilla.desde0) * calculosPlanilla.porciento0
            renta += (calculosPlanilla.hasta1 - calculosPlanilla.desde1) * calculosPlanilla.porciento1
            renta += (salarioNeto - calculosPlanilla.desde2) * calculosPlanilla.porciento2

        elif salarioNeto > calculosPlanilla.desde3:

            renta += (calculosPlanilla.hasta0 - calculosPlanilla.desde0) * calculosPlanilla.porciento0
            renta += (calculosPlanilla.hasta1 - calculosPlanilla.desde1) * calculosPlanilla.porciento1
            renta += (calculosPlanilla.hasta2 - calculosPlanilla.desde2) * calculosPlanilla.porciento2
            renta += (salarioNeto - calculosPlanilla.desde3) * calculosPlanilla.porciento3
        return renta

    def generar_excel_pago(self):
            return {
                'type': 'ir.actions.act_url',
                'url': '/planillaAdministrativa/excel_report/%s' % (self.id),
                'target': 'new',
            }

    def envio_colilla_pago(self):
        self.id
        ICPSudo = self.env['ir.config_parameter'].sudo()
        for data in self.miembrosPlanilla_id:
            if data.salarioNeto > 0 and data.salarioNeto != False:
                vals = {
                    'dataPago': data,
                }
                report_template_id =   self.env.ref('planilla.report_detalle_pago_administrativo')._render_qweb_pdf(self,data=vals)
                data_record = base64.b64encode(report_template_id[0])
                ir_values = {
                    'name': "Comprobante de Pago " + data.nombreEmpleado + ".pdf",
                    'type': 'binary',
                    'datas': data_record,
                    'store_fname': data_record,
                    'mimetype': 'application/x-pdf',
                }
                # datosCorreo = {
                #     'urlEmail': ICPSudo.get_param('nomina.urlOdoo') + "/aceptacionesdocentes?cuatriID=" + str(
                #         self.cuatrimestrePlanilla_id.id) + "&docenteID=" + str(
                #         data.docente_id.id) + "&pago=" + self.pago,
                #     'docenteNombre': data.nombreDocente,
                #     'fechaInicioPago': str(self.fechaInicioPago),
                #     'fechaFinalPago': self.fechaFinalPago,
                # }
                data_id = self.env['ir.attachment'].create(ir_values)
                template_id = self.env.ref('planilla.email_comprobante_pago').id
                template = self.env['mail.template'].browse(template_id)
                template.attachment_ids = [(6, 0, [data_id.id])]
                email_values = {'email_to': 'ggamboaf@uia.ac.cr',
                                'subject': "Comprobante de Pago " + data.nombreEmpleado
                                }
                template.send_mail(self.id, email_values=email_values,force_send=True)
                template.attachment_ids = [(3, data_id.id)]

    @api.onchange('periodoPago_id')
    def onchange_periodoPago(self):
        if self.periodoPago_id.id !=  False:
            if self.env['planilla.administrativa.pre.planilla'].search([('periodoPago_id', '=', self.periodoPago_id.id)]):
                if not  self.env['planilla.administrativa.pre.planilla'].search(['&',('periodoPago_id', '=', self.periodoPago_id.id),('pago','=','Segundo Pago')]):
                    self.pago = 'Segundo Pago'
                    self.desde = self.periodoPago_id.fechaInicioSegundoPago
                    self.hasta = self.periodoPago_id.fechaFinSegundoPago
                else:
                    raise ValidationError("Ya existe los 2 pagos creados para este periodo")
            else:
                self.pago = 'Primer Pago'
                self.desde = self.periodoPago_id.fechaInicioPrimerPago
                self.hasta = self.periodoPago_id.fechaFinPrimerPago

class PlanillaAdministrativaPrePlanillaLine(models.Model):
    _name = "planilla.administrativa.pre.planilla.line"
    _description="Planilla Administrativa Line"

    prePlanilla_id = fields.Many2one(
        string='Docentes Linea',
        comodel_name='planilla.administrativa.pre.planilla',
        ondelete="cascade"
    )
    empleado_id = fields.Many2one(
        required=False,
        comodel_name='hr.employee',
    )

    periodo_id = fields.Many2one(
        required=False,
        comodel_name='planilla.personal.periodo.pago',
    )

    nombreEmpleado = fields.Char(
        string='Empleado',
    )

    correoEmpleado = fields.Char(
        string='Correo',
    )
    cedulaEmpleado = fields.Char(
        string='Identificacion',
    )
    telefonoEmpleado = fields.Char(
        string='Telefono',
    )
    salarioBruto = fields.Float(
        string="Salario bruto",
        digits=(16, 2),
        required=False,
    )
    diasPagoCompleto = fields.Float(
        string="Dias de pago completo",
        required=False,
    )
    diasPagoMedio = fields.Float(
        string="Dias de pago medio",
        required=False,
    )
    diasPagoNulo = fields.Float(
        string="Dias sin pago",
        required=False,
    )
    CCSSEmpleado = fields.Float(
        digits=(16,2),
        string='CCSS'
    )
    rentaEmpleado = fields.Float(
        digits=(16,2),
        string='Renta'
    )
    rentaEmpleadoDocente = fields.Float(
        digits=(16,2),
        string='Otro cargo Renta'
    )
    embargo = fields.Float(
        string="Embargo",
        required=False,
    )
    totalDeduccion = fields.Float(
        digits=(16, 2),
        string='Total deducciones'
    )
    deduccionAsistencia = fields.Float(
        digits=(16, 2),
        string='Deducciones asistencia'
    )
    rebajosNeto = fields.Float(
        string="Rebajos Netos",
        required=False,
    )
    embargo = fields.Float(
        digits=(16,2),
        string='Embargo'
    )
    pension = fields.Float(
        digits=(16,2),
        string='Pensión'
    )
    # preavisoEmpleado = fields.Float(
    #     digits=(16, 2),
    #     string='Preaviso'
    # )
    # vacacionesEmpleado = fields.Float(
    #     digits=(16, 2),
    #     string='Vacaciones'
    # )
    salarioNeto = fields.Float(
        string="Salario Neto",
        digits=(16, 2),
        required=False,
    )
    pagoEfectuado = fields.Boolean(
        string="Pago Efectuado",
        default=False,
    )
    fechaCorte = fields.Date(
        string="Fecha de Corte",
        required=False,
    )