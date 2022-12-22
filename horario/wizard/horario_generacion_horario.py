# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, timedelta, datetime
import calendar

class PlanillaPersonalGenerarEmpleadosPlanilla(models.TransientModel):
    _name = "horario.generacion.horario.wizard"
    _description = "Generar los hoarios para los empleados"


    departamento_id = fields.Many2one(
        comodel_name="hr.department",
        string="Departamento",
        required=False,
    )
    empleados_list_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Empleados",
    )
    horarioPredeterminado_id = fields.Many2one(
        comodel_name="horario.horario.predeterminado",
        string="Horario",
        required=True,
    )
    segundoHorarioPredeterminado_id = fields.Many2one(
        comodel_name="horario.horario.predeterminado",
        string="Segundo Horario",
    )
    fechaInicioHorario = fields.Date(
        string="Fecha inicio horario",
        required=True,
    )
    tipoHorario = fields.Selection(
        string="Tipo de horario",
        selection=
        [
            ('N_Semanas', 'N° Semanas'),
            ('Cuatrimestral', 'Cuatrimestral'),
            ('Fijo', 'Fijo'),
        ],
        required=True,
    )
    cantidadSemanas = fields.Integer(
        string="Cantidad de semanas",
        required=False,
    )

    horarioCombinado = fields.Boolean(
        string="Horario Combinado",
    )


    def generar_horario(self):
        step = timedelta(1)
        vals = {}
        semanas = 0
        fechaFinal = any

        if self.tipoHorario == 'N_Semanas':
            fechaFinal = self.fechaInicioHorario + timedelta(weeks=self.cantidadSemanas)
            semanas = self.cantidadSemanas - 1

        elif self.tipoHorario == 'Cuatrimestral':
            fechaFinal = self.fechaInicioHorario + timedelta(weeks=16)
            semanas = 16-1

        elif self.tipoHorario == 'Fijo':
            fechaFinal = date(self.fechaInicioHorario.year, 12, 31)
            semanas = (52 - self.fechaInicioHorario.isocalendar()[1])


        list = []
        horarioSet = self.horarioPredeterminado_id
        for empleado in self.empleados_list_ids:
            fechaHorario = self.fechaInicioHorario
            fechaHorarioT = self.fechaInicioHorario + (timedelta(days=6))
            semanasWhile = 0
            while semanasWhile <= semanas:
                if self.horarioCombinado:
                    if semanasWhile % 2 == 0:
                        horarioSet = self.horarioPredeterminado_id
                    else:
                        horarioSet = self.segundoHorarioPredeterminado_id


                vals = {
                    'name': 'Horario desde: '+ str(fechaHorario) + ' hasta: ' + str(fechaHorarioT),
                    'fechaDesde': fechaHorario,
                    'fechaHasta': fechaHorarioT
                }
                while fechaHorario <= fechaHorarioT:

                    if fechaHorario.weekday() == 0:
                        horarioLine = self.env['horario.horario.predeterminado.line'].search(['&', ('diaHorario', '=', 'Lunes'),('horarioPredeterminado_id', '=', horarioSet.id)])
                        if horarioLine:
                            vals.update({
                                'horaInicioLunes': datetime.strptime(str(fechaHorario) + ' ' + str(horarioLine.horaEntrada + ':00'),
                                    "%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                                'horaFinalLunes': datetime.strptime(str(fechaHorario) + ' ' + str(horarioLine.horaSalida + ':00'),
                                    "%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                            })
                    elif fechaHorario.weekday() == 1:
                        horarioLine = self.env['horario.horario.predeterminado.line'].search(['&', ('diaHorario', '=', 'Martes'),('horarioPredeterminado_id', '=', horarioSet.id)])
                        if horarioLine:
                            vals.update({
                                'horaInicioMartes': datetime.strptime(
                                    str(fechaHorario) + ' ' + str(horarioLine.horaEntrada + ':00'),
                                    "%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                                'horaFinalMartes': datetime.strptime(
                                    str(fechaHorario) + ' ' + str(horarioLine.horaSalida + ':00'),
                                    "%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                            })
                    elif fechaHorario.weekday() == 2:
                        horarioLine = self.env['horario.horario.predeterminado.line'].search(['&', ('diaHorario', '=', 'Miercoles'),('horarioPredeterminado_id', '=', horarioSet.id)])
                        if horarioLine:
                            vals.update({
                                'horaInicioMiercoles': datetime.strptime(
                                    str(fechaHorario) + ' ' + str(horarioLine.horaEntrada + ':00'),
                                    "%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                                'horaFinalMiercoles': datetime.strptime(
                                    str(fechaHorario) + ' ' + str(horarioLine.horaSalida + ':00'),
                                    "%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                            })
                    elif fechaHorario.weekday() == 3:
                        horarioLine = self.env['horario.horario.predeterminado.line'].search(
                            ['&', ('diaHorario', '=', 'Jueves'),
                             ('horarioPredeterminado_id', '=', horarioSet.id)])
                        if horarioLine:
                            vals.update({
                                'horaInicioJueves': datetime.strptime(
                                    str(fechaHorario) + ' ' + str(horarioLine.horaEntrada + ':00'),
                                    "%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                                'horaFinalJueves': datetime.strptime(
                                    str(fechaHorario) + ' ' + str(horarioLine.horaSalida + ':00'),
                                    "%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                            })
                    elif fechaHorario.weekday() == 4:
                        horarioLine = self.env['horario.horario.predeterminado.line'].search(
                            ['&', ('diaHorario', '=', 'Viernes'),
                             ('horarioPredeterminado_id', '=', horarioSet.id)])
                        if horarioLine:
                            vals.update({
                                'horaInicioViernes': datetime.strptime(
                                    str(fechaHorario) + ' ' + str(horarioLine.horaEntrada + ':00'),
                                    "%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                                'horaFinalViernes': datetime.strptime(
                                    str(fechaHorario) + ' ' + str(horarioLine.horaSalida + ':00'),
                                    "%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                            })
                    elif fechaHorario.weekday() == 5:
                        horarioLine = self.env['horario.horario.predeterminado.line'].search(
                            ['&', ('diaHorario', '=', 'Sabado'),
                             ('horarioPredeterminado_id', '=', horarioSet.id)])
                        if horarioLine:
                            vals.update({
                                'horaInicioSabado': datetime.strptime(
                                    str(fechaHorario) + ' ' + str(horarioLine.horaEntrada + ':00'),
                                    "%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                                'horaFinalSabado': datetime.strptime(
                                    str(fechaHorario) + ' ' + str(horarioLine.horaSalida + ':00'),
                                    "%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                            })
                    elif fechaHorario.weekday() == 6:
                        horarioLine = self.env['horario.horario.predeterminado.line'].search(
                            ['&', ('diaHorario', '=', 'Domingo'),
                             ('horarioPredeterminado_id', '=', horarioSet.id)])
                        if horarioLine:
                            vals.update({
                                'horaInicioDomingo': datetime.strptime(str(fechaHorario) + ' ' + str(horarioLine.horaEntrada + ':00'),"%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                                'horaFinalDomingo': datetime.strptime(str(fechaHorario) + ' ' + str(horarioLine.horaSalida + ':00'),"%Y-%m-%d %H:%M:%S") + timedelta(hours=6),
                            })

                    fechaHorario += step

                horarioEmpleado = self.env['horario.empleado'].search([('empleado_id','=',empleado.id)])

                if horarioEmpleado:
                    fechasearch = (fechaHorario) - timedelta(weeks=1)
                    if not self.env['horario.empleado.line'].search([('fechaDesde','=',fechasearch),('horarioEmpleado_id','=',horarioEmpleado.id)]):
                        vals.update({
                            'horarioEmpleado_id': horarioEmpleado.id,
                        })
                        horarioEmpleado.horarioEmpleado_ids = [(0, 0, vals)]
                else:
                    valsEmpleado = {
                        'empleado_id': empleado.id
                    }
                    res = self.env['horario.empleado'].sudo().create(valsEmpleado)
                    vals.update({
                        'horarioEmpleado_id': res.id,
                    })
                    res.horarioEmpleado_ids = [(0, 0, vals)]

                semanasWhile += 1
                fechaHorarioT += timedelta(weeks=1)

    def default_administrativos(self):
        empleadosList = []
        empleado = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
        contrato = self.env['contrato.empleado'].search([('empleado_id','=',empleado.id)])
        if contrato.manejoHorario:
            for empleadosHorario in contrato.manejoHorario:
                empleadosList.append(empleadosHorario.id)
        res = {}
        res['domain'] = {'empleados_list_ids':[('id','=',empleadosList)]}
        return res