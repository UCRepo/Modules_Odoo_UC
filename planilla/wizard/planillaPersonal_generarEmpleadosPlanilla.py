# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PlanillaPersonalGenerarEmpleadosPlanilla(models.TransientModel):
    _name = "planilla.personal.generar.docentes.planilla.wizard"
    _description = "Generar la planilla para los empleados"

    periodoPago_id = fields.Many2one(
        comodel_name="planilla.personal.periodo.pago",
        string="Periodo Pago",
        required=True,
    )

    def generar_planilla(self):
        res = any
        for data in self.env['hr.employee'].search(['&',('active','=',True),('department_id','!=',"Docentes"),('department_id','!=',"Inactivos")]):
            if not self.env['planilla.personal.empleados.planilla'].search(['&',('empleado_id','=', data.id),('peridoPago_id','=',self.periodoPago_id.id)]):
                pago = ["Primer Pago","Segundo Pago"]
                for dat in pago:
                    vals = {
                        'name': self.periodoPago_id.name+" "+dat,
                        'empleado_id': data.id,
                        'peridoPago_id': self.periodoPago_id.id,
                        'salarioBase': self.env['contrato.empleado'].search([('empleado_id','=', data.id)]).salario,
                        'diasPagoCompleto': 15,
                        'pago': dat
                    }
                    res = self.env['planilla.personal.empleados.planilla'].sudo().create(vals)

                    for datosPrestamos in self.env['contrato.empleado.prestamos.line'].search(['&',('empleado_id','=',data.id),('pagoFinalizado','=',False)]):
                        res.prestamos_ids = [(0, 0, {'empleadosPlanillaLine_id': res.id,
                                                     'empleado_id': data.id,
                                                     'periodoPago_id': self.periodoPago_id.id,
                                                     'montoPago': datosPrestamos.montoPago,
                                                     'descripcion': datosPrestamos.descripcion,
                                                     })]

        return res