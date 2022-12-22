# -*- coding: utf-8 -*-
import pytz
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime
from odoo.addons.base.models.res_partner import _tz_get

class PlanillaSuficiencia(models.Model):
    _name = 'planilla.suficiencias'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Suficiencias de Docentes"

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
        comodel_name='planilla.suficiencias.line',
        inverse_name='planillaSuficiencias_id',
    )

    def generar_planilla(self):

        res = any
        cantiadadHoras = any
        cantiadadHorasSemana = any
        planillaActual = any
        ICPSudo = self.env['ir.config_parameter'].sudo()
        url = 'https://localhost:44305/api/CursosDocente/getSuficienciaDocente'
        user_tz = pytz.timezone(self.env.user.tz)
        anno = pytz.utc.localize(datetime.today()).astimezone(user_tz)
        vals = {}

        cuatrimestre = self.env['periodo.cuatrimestre'].search(['&', ('year', '=', self.cuatrimestre_id.year), ('decripcion', '=', self.cuatrimestre_id.decripcion)])

        if self.cuatrimestre_id:
            dataJSon = {
                'Anno': self.cuatrimestre_id.year,
                'Periodo': self.cuatrimestre_id.decripcion.replace('Q', ''),
            }
            header = {
                'Content-Type': 'application/json',
                'Accept': 'text/plain'
            }
            response = requests.post(url, headers=header, json=dataJSon, verify=False)

            if response.status_code == 200:
                print('s')
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
                self.miembrosPlanilla_id = [(0, 0, vals)]
    @api.model
    def create(self, vals):
        """
             Funcion que retorna el registro de la pre planilla con los cursos asignados para poder ser creado
             Evalua que el valor de warning sea False el cual en este estado significa que no se tiene ningun error en el registro para poder ser creado
        :return:
            :: retorna el registro
        """
        vals['name'] = 'Planilla Suficiencias : ' + str(self.env['periodo.cuatrimestre'].browse(vals['cuatrimestrePlanilla_id']).name)
        res = super(PlanillaSuficiencia, self).create(vals)
        return res

class PlanillaSuficiencia(models.Model):
    _name="planilla.suficiencias.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Docente Planilla Suficiencias Line"

    planillaSuficiencias_id = fields.Many2one(
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

    cantExamenes = fields.Integer(
        string="Cant. de Examenes",
        required=False,
    )