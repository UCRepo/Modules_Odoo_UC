# -*- coding: utf-8 -*-
import base64
import pytz
import requests
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime

class PlanillaTesis(models.Model):
    _name="planilla.tesis"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Planilla Tesis"

    name = fields.Char(
        string="Nombre",
        required=False,
    )

    cuatrimestrePlanilla_id = fields.Many2one(
        string='Cuatrimestre',
        tracking=True,
        required=True,
        comodel_name='periodo.cuatrimestre',
    )

    miembrosPlanilla_id = fields.One2many(
        string='Miembros',
        comodel_name='planilla.tesis.line',
        inverse_name='planillaTesis_id',
    )

    def generar_planilla(self):

        tesisList = self.env['tesis.docente'].search([('cuatrimestre_id','=',self.cuatrimestrePlanilla_id.id)])
        carrerasTarifaList = self.env['configuraciones.tarifa.tesis.carrera'].search([])
        calculosPlanilla = self.env['configuraciones'].search([])

        for data in self.env['hr.employee'].search([('department_id.name','=','Docentes')]):
            renta = 0
            CCSSDocente = 0
            embargo = 0
            agregar = False
            contratoDocente = self.env['contrato.empleado'].search([('empleado_id', '=', data.id)])

            totalTutor = list(filter(lambda x: (x.tutor.id == data.id) , tesisList))
            totalLector = list(filter(lambda x: (x.lector.id == data.id) , tesisList))
            totalDelegado = list(filter(lambda x: (x.delegado.id == data.id) , tesisList))

            montototalTutor = 0
            montototalLector = 0
            montototalDelegado = 0

            if len(totalTutor) > 0:
                for monto in totalTutor:
                    carrera = list(filter(lambda x: (x.carrera == monto.carrera), carrerasTarifaList))
                    montototalTutor += carrera[0].tarifaTutor
                    agregar = True
            if len(totalLector) > 0:
                for monto in totalLector:
                    carrera = list(filter(lambda x: (x.carrera == monto.carrera), carrerasTarifaList))
                    montototalLector += carrera[0].tarifaLector
                    agregar = True
            if len(totalDelegado) > 0:
                for monto in totalDelegado:
                    carrera = list(filter(lambda x: (x.carrera == monto.carrera), carrerasTarifaList))
                    montototalDelegado += carrera[0].tarifaDelegado
                    agregar = True

            calculo = (montototalTutor + montototalLector + montototalDelegado) / calculosPlanilla.honorariosTesis

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
                preCalculo  = calculo - (calculosPlanilla.salarioBase * 2 )
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
                'docente_id': data.id,
                'cuatrimestre_id': self.cuatrimestrePlanilla_id.id,
                'nombreDocente': data.name,
                'correoDocente': data.work_email,
                'cedulaDocente': data.identification_id,
                'telefonoDocente': data.work_phone,
                'cantidadTutor': len(totalTutor),
                'cantidadLector': len(totalLector),
                'cantidadDelegado': len(totalDelegado),
                'totalDocente': calculo,
                'brutoDocente': (montototalTutor + montototalLector + montototalDelegado),
                'CCSSDocente': CCSSDocente,
                'rentaDocente': renta,
                'aguinaldoDocente': aguinaldo,
                'cesantiaDocente': cesantia,
                'preavisoDocente': preaviso,
                'vacacionesDocente':vacaciones,
                'pagoEfectuado': False,
                'embargo': embargo,
                'cuentaBac': contratoDocente.cuentaBac,
                'cuentaBacActiva': contratoDocente.cuentaBacActiva,
            }
            if agregar == True:
                tesis = list(filter(lambda x: (x.docente_id.id == vals['docente_id']), self.miembrosPlanilla_id))
                if tesis:
                    if tesis[0].cantidadTutor != vals['cantidadTutor'] or tesis[0].cantidadLector != vals['cantidadLector'] or tesis[0].cantidadDelegado != vals['cantidadDelegado']:
                        tesis[0].pagoEfectuado = False
                        self.miembrosPlanilla_id =  [(1, tesis[0].id,vals)]
                else:
                    self.miembrosPlanilla_id = [(0, 0, vals)]

    def generar_reporte_excel_pago(self):
        if self.miembrosPlanilla_id.search_count(['&',('totalDocente','>',0),('pagoEfectuado','=',False),('docente_id','=',self.id)]) > 0:
            return {
                'type': 'ir.actions.act_url',
                'url': '/planilla/report_excel_planilla_tesis/%s' % (self.id),
                'target': 'new',
            }
        else:
            raise ValidationError("No existen nuevos docentes para agregar al pago")

    @api.model
    def create(self, vals):
        """
             Funcion que retorna el registro de la pre planilla con los cursos asignados para poder ser creado
             Evalua que el valor de warning sea False el cual en este estado significa que no se tiene ningun error en el registro para poder ser creado
        :return:
            :: retorna el registro
        """
        vals['name'] = 'Planilla Tesis : ' + str(self.env['periodo.cuatrimestre'].browse(vals['cuatrimestrePlanilla_id']).name)
        res = super(PlanillaTesis, self).create(vals)
        return res

class PlanillaCuatrimestreLine(models.Model):
    _name="planilla.tesis.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Docente Planilla Tesis Line"

    planillaTesis_id = fields.Many2one(
        string='Docentes Linea',
        comodel_name='planilla.tesis',
        ondelete="cascade"
    )
    docente_id = fields.Many2one(
        required=False,
        comodel_name='hr.employee',
    )
    cuatrimestre_id = fields.Many2one(
        required=False,
        comodel_name='periodo.cuatrimestre',
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
    cantidadTutor = fields.Integer(
        string="Cant. Veces Tutor",
        required=False,
    )
    cantidadLector = fields.Integer(
        string="Cant. Veces Lector",
        required=False,
    )
    cantidadDelegado = fields.Integer(
        string="Cant. Veces Delegado",
        required=False,
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
