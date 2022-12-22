# -*- coding: utf-8 -*-
import pytz
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta, datetime
from odoo.addons.base.models.res_partner import _tz_get

class CursosDocente(models.Model):
    _name="cursos.docente"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Cursos del Docente"

    warning = fields.Boolean(default=False, store=False)

    name = fields.Char(string="Nombre", required=False, )

    #region Fields Many2one
    adicionales_id = fields.Many2one(comodel_name="configuraciones.adicionales.line",string="Pagoadicional")

    cuatrimestre_id = fields.Many2one(comodel_name="periodo.cuatrimestre", string="Cuatrimestre", required=False,tracking=True  )

    docente_id = fields.Many2one(comodel_name="hr.employee", string="Docente", required=False, tracking=True)

    puesto = fields.Char(string="Puesto", required=False,)

    cursos_ids = fields.Many2one(comodel_name="configuraciones.cursos",string="Cursos", required=False, )

    ajustes_ids = fields.Many2one(comodel_name="configuraciones.ajuste.pago.line", string="Ajuste", required=False, )

    reposiciones_ids = fields.Many2one(comodel_name="configuraciones.reposiciones.line", string="Reposicion", required=False, )

    rebajo_id = fields.Many2one(comodel_name="configuraciones.rebajos.line", string="Rebajos", required=False,tracking=True)

    autoriza_ids = fields.Many2one(comodel_name="hr.employee", string="Persona que Autoriza", required=False, )
    #endregion

    #region Fields One2many
    cursos_lines_ids = fields.One2many(comodel_name="cursos.docente.line", inverse_name="cursos_id", string="Cursos", required=False, )
    #region Fields de cursos_lines_ids
    dia1 = fields.Selection(
        string="Dia Clases #1",
        selection=[('L', 'Lunes'),
                   ('K', 'Martes'),
                   ('M', 'Miercoles'),
                   ('J', 'Jueves'),
                   ('V', 'Viernes'),
                   ('S', 'Sabado'),
                   ('D', 'Domingo'),
                   ('N/A', 'Sin'),
                   ],
        default='N/A',
        tracking=True,

    )
    dia2 = fields.Selection(
        string="Dia Clases #2",
        selection=[('L', 'Lunes'),
                   ('K', 'Martes'),
                   ('M', 'Miercoles'),
                   ('J', 'Jueves'),
                   ('V', 'Viernes'),
                   ('S', 'Sabado'),
                   ('D', 'Domingo'),
                   ('N/A', 'Sin'),
                   ],
        default='N/A',
        tracking=True,

    )
    dia3 = fields.Selection(
        string="Dia Clases #3",
        selection=[('L', 'Lunes'),
                   ('K', 'Martes'),
                   ('M', 'Miercoles'),
                   ('J', 'Jueves'),
                   ('V', 'Viernes'),
                   ('S', 'Sabado'),
                   ('D', 'Domingo'),
                   ('N/A', 'Sin'),
                   ],
        default='N/A',
        tracking=True,

    )
    horaInicio = fields.Integer(
        string="Hora Inicio",
        tracking=True,

    )
    minutoInicio = fields.Selection(string="Minuto Inicio", selection=[
        ('00', '00'),
        ('15', '15'),
        ('30', '30'),
        ('45', '45')
    ], required=False,
                                    )

    ampmInicio = fields.Selection(
        string="Inicio AM/PM",
        selection=[('am', 'am'),
                   ('pm', 'pm'),
                   ],
        required=False,
        tracking=True,

    )
    horaFinal = fields.Integer(
        string="Hora Final",
        required=False,
        tracking=True,

    )

    minutoFinal =  fields.Selection(string="Minuto Final", selection=[
        ('00', '00'),
        ('15', '15'),
        ('30', '30'),
        ('45', '45')
    ], required=False,
                                    )
    ampmFinal = fields.Selection(
        string=" Final AM/PM",
        selection=[('am', 'am'),
                   ('pm', 'pm'),
                   ],
        required=False,
        tracking=True,

    )
    #endregion

    adicionales_lines_ids = fields.One2many(comodel_name="adicionales.docente.line", inverse_name="adicionales_id", string="", required=False, )

    ajustes_lines_ids = fields.One2many(comodel_name="ajustes.pago.docente.line", inverse_name="ajustes_id", string="", required=False, )
    #region Fields ajustes_lines_ids

    monto_ajustes = fields.Float(string="Monto Fijo",  required=False,  )

    horas_ajustes = fields.Integer(string="Cantidad de Horas", required=False,  )

    minutos_ajustes  = fields.Selection(string="Cantidad de Minutos", selection=[
        ('00', '00'),
        ('15', '15'),
        ('30', '30'),
        ('45', '45')
    ], required=False,
                                        )
    descripcion_ajustes = fields.Text(string="Descripcion", required=False,  )

    documento_autorizacion_ajuste = fields.Binary(string='Autorizacion')

    fechaAjuste = fields.Date(
        string="Fecha de Ajuste",
        required=False,
    )
    #endregion

    reposiciones_lines_ids = fields.One2many(comodel_name="reposiciones.clases.line", inverse_name="reposiciones_id", string="",required=False, )
    #region Fields reposiciones_lines_ids
    monto_reposiciones = fields.Float(string="Monto Fijo",  required=False,  )

    horas_reposiciones = fields.Integer(string="Cantidad de Horas", required=False,  )

    minutos_reposiciones = fields.Selection(string="Cantidad de Minutos", selection=[
        ('00', '00'),
        ('15', '15'),
        ('30', '30'),
        ('45', '45')
    ], required=False,
                                            )

    descripcion_reposiciones = fields.Text(string="Descripcion", required=False, )
    #endregion

    rebajos_lines_ids = fields.One2many(comodel_name="rebajos.manuales.line", inverse_name="rebajos_id", string="",required=False, )
    #region Fields rebajos manuales
    monto_rebajos= fields.Float(
        string="Monto",
        required=False,
    )
    #endregion

    asistencia_line_ids = fields.One2many(comodel_name="asistencia.docente.line", inverse_name="asistencia_id", string="", required=False, )

    #endregion

    def action_add_curso(self):
        """
             Agrega un curso al field cursos_lines_ids
        """
        if self.check_agregarCurso():
            nombreCurso = self.cursos_ids.name
            descripcion = self.cursos_ids.descripcion
            codigoCurso = self.cursos_ids.codigoCurso
            cantiadadHoras = self.cursos_ids.cantiadadHoras
            cantiadadHorasSemana = 0.0
            if self.dia1 != 'N/A':
                horario = self.dia1
                cantiadadHorasSemana = cantiadadHoras
                if self.dia2 != 'N/A':
                    horario += self.dia2
                    cantiadadHorasSemana = cantiadadHoras * 2
                    if self.dia3 != 'N/A':
                        horario += self.dia3
                        cantiadadHorasSemana = cantiadadHoras * 3
            horario += '( ' + str(self.horaInicio) + ':' + str(self.minutoInicio) + ' ' + self.ampmInicio + ' - ' + str(
                self.horaFinal) + ':' + str(self.minutoFinal) + ' ' + self.ampmFinal + ' )'

            self.cursos_lines_ids = [(0, 0, {'docente_id': self.docente_id.id,
                                             'cursos_id': self.id,
                                             'cuatrimestre_id': self.cuatrimestre_id.id,
                                             'name': nombreCurso,
                                             'descripcion': descripcion,
                                             'codigoCurso': codigoCurso,
                                             'cantiadadHoras': cantiadadHoras,
                                             'cantiadadHorasSemana': cantiadadHorasSemana,
                                             'horario': horario,
                                             'dia1': self.dia1,
                                             'dia2': self.dia2,
                                             'dia3': self.dia3,
                                             'horaInicio': self.horaInicio,
                                             'minutoInicio': self.minutoInicio,
                                             'horaFinal': self.horaFinal,
                                             'minutoFinal': self.minutoFinal,
                                             'ampmFinal': self.ampmFinal,
                                             'ampmInicio': self.ampmInicio
                                             })]

    def action_add_adicional(self):
        """
             Agrega un adicional al field adicionales_lines_ids y evalua si ya esta para sumarlo
        """
        if self.check_agregarAdicionales():
            nombreAdicionales = self.adicionales_id.name
            pagoAdicionales = self.adicionales_id.montoSinPrestaciones
            agregar = True
            idModificar = 0
            if len(self.adicionales_lines_ids) > 0:

                for data in self.adicionales_lines_ids:
                    if data.adicionalId == self.adicionales_id.id:
                        agregar = False
                        idModificar = data.id

                if agregar == True:
                    self.adicionales_lines_ids = [(0, 0, {'adicionalId': self.adicionales_id.id,
                                                          'name': nombreAdicionales,
                                                          'sinPrestaciones': pagoAdicionales,
                                                          'cantidad': 1,
                                                          'totalAdicionales': pagoAdicionales,
                                                          'cuatrimestre_id': self.cuatrimestre_id.id,
                                                          'docente_id': self.docente_id.id,
                                                          'pagoEfectuado': False,
                                                          'fechaAdicional': pytz.utc.localize(datetime.today()).astimezone(user_tz)
                                                          })]
                else:
                    self.adicionales_lines_ids = [(1, idModificar, {'cantidad': data.cantidad + 1,
                                                                    'totalAdicionales': (
                                                                                                    data.cantidad + 1) * data.sinPrestaciones})]


            else:
                self.adicionales_lines_ids = [(0, 0, {'adicionalId': self.adicionales_id.id,
                                                      'name': nombreAdicionales,
                                                      'sinPrestaciones': pagoAdicionales,
                                                      'cantidad': 1,
                                                      'totalAdicionales': pagoAdicionales,
                                                      'cuatrimestre_id': self.cuatrimestre_id.id,
                                                      'docente_id': self.docente_id.id,
                                                      'pagoEfectuado': False
                                                      })]

    def action_add_ajustes(self):
        """
             Agrega un ajuste para ya sea por monto fijo o por horas el ultimo se agarran las horas y se multiplica
                por el salario del docente
        """
        ajuste_id = self.ajustes_ids.id
        monto = self.monto_ajustes
        horas = self.horas_ajustes
        minutos = self.minutos_ajustes
        cuatrimestre_id = self.cuatrimestre_id.id
        docente_id = self.docente_id.id
        descripcion = self.descripcion_ajustes
        autoriza_id = self.autoriza_ids.id
        total = any
        user_tz = pytz.timezone( self.env.user.tz)
        if self.check_agregarAjustesPago():
            if monto > 0:
                total = monto /  self.env['configuraciones'].search([]).factor
            else:
                m = int(minutos)
                total = (self.env['contrato.empleado'].search([('empleado_id','=',self.docente_id.id)]).salario / 60) * ((horas + (m / 60)) * 60)
            self.ajustes_lines_ids = [(0, 0, {
                'ajuste_id': ajuste_id,
                'name': self.ajustes_ids.name,
                'monto': monto,
                'horas': horas,
                'minutos': minutos,
                'cuatrimestre_id': cuatrimestre_id,
                'docente_id': docente_id,
                'descripcion': descripcion,
                'total': total,
                'autoriza_id': autoriza_id,
                'fechaAjuste':self.fechaAjuste,
                'pagoEfectuado': False
            })]

    def action_add_reposiciones(self):
        """
             Agrega una reposicion para ya sea por monto fijo o por horas el ultimo se agarran las horas y se multiplica
                por el salario del docente
        """
        reposicion_id = self.reposiciones_ids.id
        monto = self.monto_reposiciones
        horas = self.horas_reposiciones
        minutos = self.minutos_reposiciones
        cuatrimestre_id = self.cuatrimestre_id.id
        docente_id = self.docente_id.id
        descripcion = self.descripcion_reposiciones
        autoriza_id = self.autoriza_ids.id
        user_tz = pytz.timezone(self.env.user.tz)
        if self.check_agregarReposicion():
            if monto > 0:
                total = monto / self.env['configuraciones'].search([]).factor
            else:
                m = int(minutos)
                total = (self.env['contrato.empleado'].search([('empleado_id','=',self.docente_id.id)]).salario/ 60) * ((horas + (m / 60)) * 60)

            self.reposiciones_lines_ids = [(0, 0, {
                'reposiciones_id': reposicion_id,
                'name': self.reposiciones_ids.name,
                'monto': monto,
                'horas': horas,
                'minutos': minutos,
                'cuatrimestre_id': cuatrimestre_id,
                'docente_id': docente_id,
                'descripcion': descripcion,
                'total': total,
                'autoriza_id': docente_id,
                'fechaRepocicion': pytz.utc.localize(datetime.today()).astimezone(user_tz),
                'pagoEfectuado': False
            })]

    def action_add_rebajo(self):
        user_tz = pytz.timezone(self.env.user.tz)
        if self.monto_rebajos > 0:
            self.rebajos_lines_ids = [(0, 0, {
                'name': self.rebajo_id.name,
                'docente_id': self.docente_id.id,
                'cuatrimestre_id': self.cuatrimestre_id.id,
                'rebajos_id': self.rebajo_id.id,
                'monto': self.monto_rebajos,
                'fechaRebajo': pytz.utc.localize(datetime.today()).astimezone(user_tz),
                'pagoEfectuado': False
            })]

    @api.model
    def create(self, vals):
        """
             Funcion que retorna el registro del docente con los cursos asignados para poder ser creado
             Evalua que el valor de warning sea False el cual en este estado significa que no se tiene ningun error en el registro para poder ser creado
        :return:
            :: retorna el registro
        """
        if vals['warning'] != True:
            res = super(CursosDocente, self).create(vals)
            res.puesto = res.docente_id.job_title
            return res
        else:
            raise ValidationError(" No se puede guardar el registro ya que este docente ya tiene cursos en el cuatrimestre selecionado")

    def write(self,vals):
        res = super(CursosDocente, self).write(vals)
        return res

    #region Metodos de Verificacion

    @api.onchange('docente_id')
    def _onchangedocenteId(self):
        """
             Al detectar un cambio de estado en el Field docente_id evalua que no exista ningun
                docente asignado ya ese cuatrimestre
        """
        if self.docente_id.id != False:
            for data in self.env['cursos.docente'].search([]):
                if data.docente_id.id == self.docente_id.id and self.cuatrimestre_id.id == data.cuatrimestre_id.id:
                    self.warning = True
                    break
                else:
                    self.warning = False

    #region Metodo de Verificacion de agregar Curso

    def check_agregarCurso(self):
        """
             Metodo que verifica que los campos de agregar curso esten de forma correcta
        """
        message = 'Se detectaron los siguientes errores : \n'
        countError = 0
        if self.cursos_ids.codigoCurso == False:
            message += "Se tiene que selecionar un Curso \n"
            countError += 1
        if self.dia1 == 'N/A':
            message += "El Dia Clases #1 no puede quedar vacio \n"
            countError += 1
        if self.dia2 == False:
            message += "El Dia Clases #2 no puede ser vacio \n"
            countError += 1
        if self.dia3 == False:
            message += "El Dia Clases #3 no puede ser vacio \n"
            countError += 1
        if self.horaInicio > 12 or self.horaInicio <= 0:
            message += "La hora de inicio no puede superar las 12h o ser igual o menor a 0\n"
            countError += 1
        if self.minutoInicio == False:
            message += "El minuto de inicio no puede estar vacio \n"
            countError += 1
        if self.ampmInicio == False:
            message += "Selecione AM o PM de Inicio \n"
            countError += 1
        if self.horaFinal > 12 or self.horaInicio <= 0:
            message += "La hora final no puede superar las 12h o ser igual o menor a 0 \n"
            countError += 1
        if self.minutoFinal == False:
            message += "El minuto final no puede estar vacio \n"
            countError += 1
        if self.ampmFinal == False:
            message += "Selecione AM o PM Final \n"
            countError += 1

        if countError > 1:
            raise ValidationError(message)
            return False
        else:
            return True

    #endregion

    #region Metodos de Verificacion de Adicionales
    def check_agregarAdicionales(self):
        """
            Metodo que verifica que se selecione exista un adocional selecionado para poder ser agregado
        :return:
        """
        message = 'Se detectaron los siguientes errores : \n'
        countError = 0
        if self.adicionales_id.name == False:
            message += "Se tiene que seleecionar un tipo de adicional para agregar\n"
            countError += 1

        if countError > 1:
            raise ValidationError(message)
            return False
        else:
            return True
    #endregion

    #region Metodos de Verificacion de Ajistes de Pago
    def check_agregarAjustesPago(self):
        """
            Metodo que verifica que los campos de ajuste de pago este con el formato correcto para poder ser agreagado
        :return:
        """
        message = 'Se detectaron los siguientes errores : \n'
        countError = 0
        if self.ajustes_ids.name == False:
            message += "Se tiene que seleecionar un tipo de adicional para agregar \n"
            countError += 1
        elif self.autoriza_ids.name == False:
            message += "Se tiene que seleecionar una persona para autorizar el ajuste \n"
            countError += 1
        elif self.descripcion_ajustes == False:
            message += "Se tiene que escribir una pequeña descripcion de pór que se autoriza el ajuste \n"
            countError += 1
        elif self.monto_ajustes <= 0 and self.horas_ajustes <= 0:
            message += "Se tiene que colocar ya sea una hora mayor a 0 o un monto fijo mayor a 0 \n"
            countError += 1
        elif self.monto_ajustes > 0 and self.horas_ajustes > 0:
            message += "Solo se puede agregar un ajuste por monto fijo o por horas no por los 2 medios\n"
            countError += 1

        if countError >= 1:
            raise ValidationError(message)
            return False
        else:
            return True

    #endregion

    #region Metodos de Verificacion de Reposicion
    def check_agregarReposicion(self):
        """
            Metodo que verifica que los campos de Reposicion de pago este con el formato correcto para poder ser agreagado
        :return:
        """
        message = 'Se detectaron los siguientes errores : \n'
        countError = 0
        if self.reposiciones_ids.name == False:
            message += "Se tiene que seleecionar un tipo de adicional para agregar \n"
            countError += 1
        if self.autoriza_ids.name == False:
            message += "Se tiene que seleecionar una persona para autorizar el ajuste \n"
            countError += 1
        if self.descripcion_reposiciones == False:
            message += "Se tiene que escribir una pequeña descripcion de pór que se autoriza el ajuste \n"
            countError += 1
        if self.monto_reposiciones <= 0 and self.horas_reposiciones <= 0:
            message += "Se tiene que colocar ya sea una hora mayor a 0 o un monto fijo mayor a 0 \n"
            countError += 1
        elif self.monto_reposiciones > 0 and self.horas_reposiciones > 0:
            message += "Solo se puede agregar una reposicion por monto fijo o por horas no por los 2 medios\n"
            countError += 1

        if countError >= 1:
            raise ValidationError(message)
            return False
        else:
            return True
    #endregion


    #endregion

#region Clases Lines
class CursosDocenteLines(models.Model):
    _name="cursos.docente.line"
    _description = "Docentes por contrato"

    docente_id = fields.Many2one(
        required=False,
        comodel_name='hr.employee'
    )
    cuatrimestre_id = fields.Many2one(
        required=False,
        comodel_name='periodo.cuatrimestre',
    )

    cursos_id = fields.Many2one(
        comodel_name="cursos.docente",
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

    cantiadadHoras  = fields.Float(
        string="Horas de Curso",
        required=True,
        digits=(12,2)
    )

    cantiadadHorasSemana  = fields.Float(
        string="Horas de Curso Por Semana",
        required=True,
        digits=(12,2)
    )

    horario = fields.Char(
        string="Horario",
        required=False,
    )

    dia1 = fields.Char(
        string="Dia Clases #1",
        required=True,
    )
    dia2 = fields.Char(
        string="Dia Clases #2",
        required=True,
    )
    dia3 = fields.Char(
        string="Dia Clases #3",
        required=True,
    )
    horaInicio = fields.Char(
        string="Hora Inicio",
        required=True,
    )
    minutoInicio = fields.Char(
        string="Minuto Inicio",
        required=True,
    )
    ampmInicio = fields.Selection(
        string="Inicio AM/PM",
        selection=[('am', 'am'),
                   ('pm', 'pm'),
                   ],
        required=True,
    )
    horaFinal = fields.Char(
        string="Hora Final",
        required=True,
    )
    minutoFinal = fields.Char(
        string="Minuto Final",
        required=True,
    )
    ampmFinal = fields.Selection(
        string=" Final AM/PM",
        selection=[('am', 'am'),
                   ('pm', 'pm'),
                   ],
        required=True,
    )
    estadoCurso = fields.Char(
        string="Estado del Curso",
        required=False,
    )
    alumnos = fields.Integer(
        string="Alumnos",
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

class RebajosManualesLines(models.Model):
    _name="rebajos.manuales.line"

    docente_id = fields.Many2one(
        required=False,
        comodel_name='hr.employee',
    )
    cuatrimestre_id = fields.Many2one(
        required=False,
        comodel_name='periodo.cuatrimestre',
    )
    rebajos_id = fields.Many2one(
        comodel_name="cursos.docente",
        ondelete="cascade"
    )
    name = fields.Char(
        string="Nombre"
    )
    monto = fields.Float(
        string="Monto",
        required=False,
    )
    fechaRebajo = fields.Date(
        string="Fecha",
        required=False,
    )
    pagoEfectuado = fields.Boolean(
        string="",
    )

class AdicionalesDocenteLines(models.Model):
    _name="adicionales.docente.line"
    _description = "Adicionales del Dodcente"

    docente_id = fields.Many2one(
        required=False,
        comodel_name='hr.employee',
    )
    cuatrimestre_id = fields.Many2one(
        required=False,
        comodel_name='periodo.cuatrimestre',
    )

    adicionales_id = fields.Many2one(
        comodel_name="cursos.docente",
        ondelete="cascade"
    )

    name = fields.Char(
        string="Nombre"
    )

    adicionalId = fields.Integer(
        comodel_name="configuraciones.adicionales.line",
        ondelete="cascade"
    )

    sinPrestaciones = fields.Float(
        digits=(16,2),
        string="Costo",
        required=True
    )

    cantidad = fields.Integer(
        string="Cantiada",
        required=False,
    )

    totalAdicionales = fields.Float(
        string="Total",
        required=False,
    )

    fechaAdicional = fields.Date(
        string="Fecha",
        required=False,
    )

    pagoEfectuado = fields.Boolean(
        string="",
    )

class AjustesPagosDocenteLines(models.Model):
    _name="ajustes.pago.docente.line"
    _description = "Ajustes de pago del Docente"

    docente_id = fields.Many2one(
        required=False,
        comodel_name='hr.employee',
        ondelete="cascade"
    )
    cuatrimestre_id = fields.Many2one(
        required=False,
        comodel_name='periodo.cuatrimestre',
    )

    ajustes_id = fields.Many2one(
        comodel_name="cursos.docente",
        ondelete="cascade"
    )

    ajuste_id = fields.Integer()

    name = fields.Char(
        string="",
        required=False,
    )

    monto = fields.Float(
        string="",
        required=False,
    )

    horas = fields.Integer(
        string="",
        required=False,
    )

    minutos = fields.Integer(
        string="",
        required=False,
    )

    total = fields.Float(
        string="",
        required=False,
    )

    descripcion = fields.Text(
        string="",
        required=False,
    )
    autoriza_id = fields.Integer(
        string="",
        required=False,
    )
    fechaAjuste = fields.Date(
        string="Fecha",
        required=False,
    )
    pagoEfectuado = fields.Boolean(
        string="",
    )

class ReposicionesClasesLines(models.Model):
    _name="reposiciones.clases.line"
    _description = "Ajustes de pago del Docente"

    docente_id = fields.Many2one(
        required=False,
        comodel_name='hr.employee'
    )
    cuatrimestre_id = fields.Many2one(
        required=False,
        comodel_name='periodo.cuatrimestre',
    )


    reposiciones_id = fields.Many2one(
        comodel_name="cursos.docente",
        ondelete="cascade"
    )

    name = fields.Char(
        string="",
        required=False,
    )

    horas = fields.Integer(
        string="",
        required=False,
    )

    minutos = fields.Integer(
        string="",
        equired=False,
    )

    monto = fields.Float(
        string="",
        required=False,
    )

    total = fields.Float(
        string="",
        required=False,
    )

    descripcion = fields.Text(
        string="",
        required=False,
    )

    autoriza_id = fields.Integer(
        string="",
        required=False,
    )
    fechaRepocicion = fields.Date(
        string="Fecha",
        required=False,
    )
    pagoEfectuado = fields.Boolean(
        string="",
    )

class AsistenciaClasesLine(models.Model):
    _name = 'asistencia.docente.line'
    _description = "Asistencia de Docente"

    docente_id = fields.Many2one(
        required=False,
        comodel_name='hr.employee'
    )
    cuatrimestre_id = fields.Many2one(
        required=False,
        comodel_name='periodo.cuatrimestre',
    )
    asistencia_id = fields.Many2one(
        comodel_name="cursos.docente",
        ondelete="cascade"
    )
    aplicar = fields.Boolean(
        string="Aplicar",
    )
    cursoMarca = fields.Char(
        string="Curso",
        required=False,
    )
    fechaCurso = fields.Date(
        string="Fecha de curso",
        required=False,
    )
    horarioCurso = fields.Char(
        string="Horario de curso",
        required=False,
    )
    entradaClases = fields.Datetime(
        string="Marca de entrada",
        required=False,
    )
    salidaClases = fields.Datetime(
        string="Marca de salida",
        required=False,
    )
    tiempoClases = fields.Float(
        string="Tiempo de calses",
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
    deduccionTotal = fields.Float(
        string="Monto Deduccion",
        required=False,
        digits=(16, 2)
    )
    marcaJustificada = fields.Boolean(
        string="Justificada",
        default=False
    )
    empleadoJustificacion = fields.Many2one(
        comodel_name="hr.employee",
        string="Docente Especifico",
        readonly=False
    )
    pagoMarca = fields.Char(
        string="Pago",
        required=False,
    )

#endregion

