# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Configuraciones(models.Model):
    _name="configuraciones"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Configuraciones de Pago"

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        readonly=True,
        default=lambda self: self.env.company.currency_id
    )
    name = fields.Char(
        string="Descripción",
        required=False,
    )
    #region Pagos Adicionales
    adicionales_ids = fields.One2many(
        comodel_name = "configuraciones.adicionales.line",
        inverse_name = "configuracion_id",
        string="Adicionales",
        required=False,
    )

    nameAdicional = fields.Char(
        string="Nombre",
    )

    montoAdicional = fields.Float(
        digits=(16,2),
        string="Costo",
        currency_field='currency_id'
    )

    @api.constrains('monto')
    def check_monto(self):
        """
            Al detectar un cambio en el field monto verifica que el monto este con el formato correcto
        :return:
        """
        if self.monto <= 0:
            raise ValidationError("El monto tiene que ser mayor a 0")

    def add_adicional(self):
        """
        Metodo para agregar un adiccional
        :return:
        """
        if not self.env['configuraciones.adicionales.line'].search(['&',('configuracion_id','=',self.id),('name','=',self.nameAdicional)]):
            self.adicionales_ids = [(0, 0, {'configuracion_id': self.id,
                                            'name': self.nameAdicional,
                                            'monto': self.montoAdicional,
                                            'montoSinPrestaciones': round(self.montoAdicional/self.factor),
                                            })]
        else:
            raise ValidationError("Ya existe un adicional con el mismo nombre")

    #endregion

    #region Ajustes de Pago

    ajustes_ids = fields.One2many(
        comodel_name = "configuraciones.ajuste.pago.line",
        inverse_name = "configuracion_id",
        string="Adicionales",
        required=False,
    )

    nameAjuste = fields.Char(
        string="Nombre",
        required=False,
        tracking=True
    )
    def add_ajuste(self):
        """
        Metodo para agregar un ajuste
        :return:
        """
        if not self.env['configuraciones.ajuste.pago.line'].search(['&',('configuracion_id','=',self.id),('name','=',self.nameAjuste)]):
            self.ajustes_ids = [(0, 0, {'configuracion_id': self.id,
                                        'name': self.nameAjuste,})]
        else:
            raise ValidationError("Ya existe un ajuste con el mismo nombre")
    #endregion

    #region Reposiciones

    reposiciones_ids = fields.One2many(
        comodel_name = "configuraciones.reposiciones.line",
        inverse_name = "configuracion_id",
        string="Adicionales",
        required=False,
    )

    nameReposiciones = fields.Char(
        string="Nombre",
        required=False,
        tracking=True
    )
    def add_reposiciones(self):
        """
        Metodo para agregar una reposicion
        :return:
        """
        if not self.env['configuraciones.reposiciones.line'].search(['&',('configuracion_id','=',self.id),('name','=',self.nameReposiciones)]):
            self.reposiciones_ids = [(0, 0, {'configuracion_id': self.id,
                                        'name': self.nameReposiciones,})]
        else:
            raise ValidationError("Ya existe una reposicion con el mismo nombre")
    #endregion

    # region Renta
    desde0 = fields.Float(
        string="Desde",
        required=False,
        currency_field='currency_id'
    )
    hasta0 = fields.Float(
        string="Hasta",
        required=False,
        currency_field='currency_id'
    )
    porciento0 = fields.Float(
        string="%",
        required=False,
    )

    desde1 = fields.Float(
        string="Desde",
        required=False,
        currency_field='currency_id'
    )
    hasta1 = fields.Float(
        string="Hasta",
        required=False,
        currency_field='currency_id'
    )
    porciento1 = fields.Float(
        string="%",
        required=False,
    )
    desde2 = fields.Float(
        string="Desde",
        required=False,
        currency_field='currency_id'
    )
    hasta2 = fields.Float(
        string="Hasta",
        required=False,
        currency_field='currency_id'
    )
    porciento2 = fields.Float(
        string="%",
        required=False,
    )
    desde3 = fields.Float(
        string="Desde",
        required=False,
        currency_field='currency_id'
    )
    hasta3 = fields.Float(
        string="Hasta",
        required=False,
        currency_field='currency_id'
    )
    porciento3 = fields.Float(
        string="%",
        required=False,
    )
    # endregion

    # region Embargo
    salarioBase = fields.Float(
        string="Salario",
        required=False,
        currency_field='currency_id'
    )
    porcientoRebajoEmbargo = fields.Float(
        string="% de rebajo",
        required=False,
    )
    # endregion

    # region CCSS
    CCSSNormal = fields.Float(
        string="CCSS",
        required=False,
    )
    CCSSPensionado = fields.Float(
        string="CCSS pensionado",
        required=False,
    )
    # endregion

    # region Prestaciones
    aguinaldo = fields.Float(
        string="Aguinaldo",
        required=False,
    )
    # cesantia = fields.Float(
    #     string="Cesantia ",
    #     required=False,
    # )
    # preaviso = fields.Float(
    #     string=" Preaviso ",
    #     required=False,
    # )
    vacaciones = fields.Float(
        string="Vacaciones ",
        required=False,
    )
    # endregion

    #region Tutorias
    tutorias_ids = fields.One2many(
        comodel_name = "configuraciones.tutorias.line",
        inverse_name = "configuracion_id",
        string="Tutorias",
        required=False,
    )
    semanaMarcatutorias_ids = fields.One2many(
        comodel_name = "configuraciones.tutorias.semana.line",
        inverse_name = "configuracion_id",
        string="Tutorias",
        required=False,
    )

    descripcionTutoria = fields.Char(
        string="Descripcion",
        required=False,
    )

    numeroEstudiantes = fields.Integer(
        string="Cantidad de estudiantes",
        required=True,
    )
    semanasTutoria = fields.Integer(
        string="Semanas de Tutoria",
        required=True,
    )

    cantiadadHorasTutorias = fields.Integer(
        string="Horas de Tutoria",
        required=True,
    )
    def add_tutoria(self):
        """
        Metodo para agregar una confgiuracion de tutoria
        :return:
        """
        if not self.env['configuraciones.tutorias.line'].search(['&',('configuracion_id','=',self.id),('numeroEstudiantes','=',self.numeroEstudiantes)]):
            self.tutorias_ids = [(0, 0, {'configuracion_id': self.id,
                                        'name': self.descripcionTutoria +" - Estudiantes: "+str(self.numeroEstudiantes),
                                        'numeroEstudiantes': self.numeroEstudiantes,
                                        'semanasTutoria': self.semanasTutoria,
                                        'cantiadadHorasTutorias': self.cantiadadHorasTutorias,
                                        })]
        else:
            raise ValidationError("Ya existe una configuracion de tutorias con la misma cantidad de estudiantes")
    #endregion

    #region Rebajos
    rebajos_ids = fields.One2many(
        comodel_name = "configuraciones.rebajos.line",
        inverse_name = "configuracion_id",
        string="Rebajos",
        required=False,
    )
    nameRebajos = fields.Char(
        string="Nombre",
        required=False,
        tracking=True
    )
    def add_rebajos(self):
        """
        Metodo para agregar un tipo de rebajo
        :return:
        """
        if not self.env['configuraciones.rebajos.line'].search(['&',('configuracion_id','=',self.id),('name','=',self.nameRebajos)]):
            self.rebajos_ids = [(0, 0, {'configuracion_id': self.id,
                                        'name': self.nameRebajos,})]
        else:
            raise ValidationError("Ya existe un rebajo con el mismo nombre")
    #endregion

    #region Otros
    factor = fields.Float(
        string="Factor",
        required=False,
        digits=(16, 5),
    )
    honorariosTesis = fields.Float(
        string="Honorarios de Tesis",
        required=False,
        digits=(16, 5),
    )
    honorariosCursosLibre = fields.Float(
        string="Honorarios de Cursos Libres",
        required=False,
        digits=(16, 5),
    )
    #endregion

    @api.model
    def create(self,vals):
        """
            Metodos para crear un registro de contrato
        :param vals: valroes que se optiens del form
        :return:
        """
        cantidad = self.env['configuraciones'].search_count([])
        if cantidad == 0:
            vals['name'] = 'Configuraciones de Nomina'
            res = super(Configuraciones, self).create(vals)
            return res

class ConfiguracionesAdicionalesLine(models.Model):
    _name = "configuraciones.adicionales.line"

    configuracion_id = fields.Many2one(
        comodel_name="configuraciones",
        string="Configuracion",
        ondelete="cascade"
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        readonly=True,
        default=lambda self: self.env.company.currency_id
    )
    name = fields.Char(
        string="Nombre",
    )

    monto = fields.Float(
        digits=(16,2),
        string="Costo",
    )
    montoSinPrestaciones = fields.Float(
        digits=(16,2),
        string="Costo sin prestaciones",
    )

class ConfiguracionesAjustesPago(models.Model):
    _name="configuraciones.ajuste.pago.line"

    configuracion_id = fields.Many2one(
        comodel_name="configuraciones",
        string="Configuracion",
        ondelete="cascade"
    )

    name = fields.Char(
        string="Nombre",
        required=False,
    )

class ConfiguracionesReposiciones(models.Model):
    _name="configuraciones.reposiciones.line"

    configuracion_id = fields.Many2one(
        comodel_name="configuraciones",
        string="Configuracion",
        ondelete="cascade"
    )

    name = fields.Char(
        string="Nombre",
        required=False,
    )

class ConfiguracionesRebajos(models.Model):
    _name="configuraciones.rebajos.line"

    configuracion_id = fields.Many2one(
        comodel_name="configuraciones",
        string="Configuracion",
        ondelete="cascade"
    )

    name = fields.Char(
        string="Nombre",
        required=False,
    )

class ConfiguracionesCursos(models.Model):
    _name = "configuraciones.cursos"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Configuraciones de Cursos"

    name = fields.Char(string="Nombre", tracking=True)

    descripcion = fields.Char(string="Descripcion",required=True, tracking=True )

    codigoCurso = fields.Char(string="Codigo Curso",required=True, tracking=True )

    cantiadadHoras  = fields.Integer(string="Horas de Curso", required=True, tracking=True)

    @api.model
    def create(self,vals):
        """
            Evalua que la cantidad de horas de curso tenga el formato correcto para poder crear el registro

        :param vals: Valores que se reciben a la hora de ser creado el registro
        :return: retorna el valor para ser creado
        """
        if vals['cantiadadHoras'] >= 0:
            vals['name'] = vals['descripcion']+'-'+vals['codigoCurso']
            res = super(ConfiguracionesCursos,self).create(vals)
            return res
        else:
            raise ValidationError("La cantidad de horas tiene que ser mayor a 0")


    @api.constrains('cantiadadHoras')
    def check_cantiadadHoras(self):
        """
            Al detectar un cambio en el field cantiadadHoras evalua que tenga el formato correcto para poder ser guardado
        :return:
        """
        if self.cantiadadHoras <= 0:
            raise ValidationError("La cantidad de horas tiene que sermayor a 0")

class ConfiguracionesCursosMedicina(models.Model):
    _name = 'configuraciones.cursos.medicina'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Configuraciones de Cursos de Medicina"

    name = fields.Char(
        string="Nombre",
        tracking=True
    )

    descripcion = fields.Char(
        string="Descripcion",
        required=True,
        tracking=True
    )

    codigoCurso = fields.Char(
        string="Codigo Curso",
        required=True,
        tracking=True
    )

    cantiadadHoras  = fields.Integer(
        string="Horas de Curso",
        required=True,
        tracking=True
    )

    tarifaCurso = fields.Float(
        string="",
        digits=(16,2),
        required=False,
    )
    planillaExterna = fields.Boolean(
        string="Planilla Externa",
        default=False
    )

    @api.model
    def create(self,vals):
        """
            Evalua que la cantidad de horas de curso tenga el formato correcto para poder crear el registro

        :param vals: Valores que se reciben a la hora de ser creado el registro
        :return: retorna el valor para ser creado
        """
        if vals['cantiadadHoras'] >= 0 and vals['tarifaCurso'] >= 0:
            vals['name'] = vals['descripcion']+' - '+vals['codigoCurso']
            vals['tarifaCurso'] = vals['tarifaCurso']/self.env['configuraciones'].search([]).factor
            res = super(ConfiguracionesCursosMedicina,self).create(vals)
            return res
        else:
            raise ValidationError("La cantidad de horas tiene que ser mayor a 0")

    def write(self,vals):
        """
            Evalua que la cantidad de horas de curso tenga el formato correcto para poder crear el registro

        :param vals: Valores que se reciben a la hora de ser creado el registro
        :return: retorna el valor para ser creado
        """
        if 'tarifaCurso' in vals:
            if vals['tarifaCurso'] > 0:
                vals['tarifaCurso'] = vals['tarifaCurso']/self.env['configuraciones'].search([]).factor
                res = super(ConfiguracionesCursosMedicina,self).write(vals)
                return res
            else:
                raise ValidationError("La cantidad de horas tiene que ser mayor a 0")
        else:
            res = super(ConfiguracionesCursosMedicina, self).write(vals)
            return res

class ConfiguracionesCursosTalleGraduacion(models.Model):
    _name = 'configuraciones.cursos.taller.graduacion'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Configuraciones de Cursos de Medicina"

    name = fields.Char(
        string="Nombre",
        tracking=True
    )

    descripcion = fields.Char(
        string="Descripcion",
        required=True,
        tracking=True
    )

    codigoCurso = fields.Char(
        string="Codigo Curso",
        required=True,
        tracking=True
    )

    @api.model
    def create(self, vals):
        """
            Evalua que la cantidad de horas de curso tenga el formato correcto para poder crear el registro

        :param vals: Valores que se reciben a la hora de ser creado el registro
        :return: retorna el valor para ser creado
        """
        vals['name'] = vals['descripcion'] + ' - ' + vals['codigoCurso']
        res = super(ConfiguracionesCursosTalleGraduacion, self).create(vals)
        return res

class ConfiguracionesCursosConPuente(models.Model):
    _name = "configuraciones.cursos.puente"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Configuraciones de Cursos"

    name = fields.Many2one(comodel_name="configuraciones.cursos", string="Nombre", required=True, tracking=True)

    codigoCurso = fields.Char(string="Codigo Curso",required=True, tracking=True)

    cursos_ids = fields.Many2many(comodel_name="configuraciones.cursos",
                                  tracking=True,
                                  required=True,
                                  string="Cursos Puente", )

    @api.onchange('name')
    def _onchangeCuatrimestre(self):
        """
            Noc por que hice esto pero funciona !NO TOCAR!
        :return:
        """
        for data in self.name:
            self.codigoCurso = data.codigoCurso

class ConfiguracionesTarifaTesisCarrera(models.Model):
    _name = 'configuraciones.tarifa.tesis.carrera'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Configuraciones de Tarifa de Tesis Segun Carrera"

    name = fields.Char(
        string="Nombre",
        tracking=True
    )

    carrera = fields.Char(
        string="Carrera",
        required=True,
        tracking=True
    )

    tarifaTutor = fields.Float(
        string="Tarifa de Tutor",
        digits=(16,2),
        required=True,
        tracking=True
    )

    tarifaLector = fields.Float(
        string="Tarifa de Lector",
        digits=(16,2),
        required=True,
        tracking=True
    )

    tarifaDelegado = fields.Float(
        string="Tarifa de Delegado",
        digits=(16,2),
        required=True,
        tracking=True
    )

    @api.onchange('tarifaTutor')
    def _tarifa_tutor(self):
        if self.tarifaTutor > 0:
            self.tarifaTutorFinal = self.tarifaTutor  / self.env['configuraciones'].search([]).factor

    @api.onchange('tarifaLector')
    def _tarifa_lector(self):
        if self.tarifaLector > 0:
            self.tarifaLectorFinal = self.tarifaLector / self.env['configuraciones'].search([]).factor

    @api.onchange('tarifaDelegado')
    def _tarifa_delegado(self):
        if self.tarifaDelegado > 0:
            self.tarifaDelegadoFinal = self.tarifaDelegado / self.env['configuraciones'].search([]).factor


    @api.model
    def create(self,vals):
        """
            Evalua que la cantidad de horas de curso tenga el formato correcto para poder crear el registro

        :param vals: Valores que se reciben a la hora de ser creado el registro
        :return: retorna el valor para ser creado
        """
        if vals['tarifaTutor'] >= 0 and vals['tarifaLector'] >= 0 and vals['tarifaDelegado'] >= 0:
            vals['name'] = vals['carrera']
            res = super(ConfiguracionesTarifaTesisCarrera,self).create(vals)
            return res
        else:
            raise ValidationError("La cantidad de horas tiene que ser mayor a 0")

class ConfiguracionesCursosLibre(models.Model):
    _name = 'configuraciones.cursos.libre'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Configuraciones de Cursos Libres"

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        readonly=True,
        default=lambda self: self.env.company.currency_id
    )

    name = fields.Char(
        string="Nombre",
        tracking=True
    )

    codigoCurso = fields.Char(
        string="Codigo",
        required=True,
        tracking=True
    )

    descripcionCurso = fields.Char(
        string="Descripción",
        required=True,
        tracking=True
    )

    pagoTracto = fields.Boolean(
        string="Pago en 2 Tractos",
        default=False,
        tracking=True
    )

    pagoDocente = fields.Float(
        string="Pago del Docente",
        required=True,
        tracking=True
    )
    semanasPago = fields.Selection(
        string="Semanas de Pago",
        selection=[
            ('Semana 5 y 10', 'Semana 5 y 10'),
            ('Semana 7 y 15', 'Semana 7 y 15'),
        ],
        required=False,
        tracking=True,
    )

    @api.model
    def create(self,vals):
        """
            Evalua que la cantidad de horas de curso tenga el formato correcto para poder crear el registro

        :param vals: Valores que se reciben a la hora de ser creado el registro
        :return: retorna el valor para ser creado
        """

        vals['name'] = vals['descripcionCurso'] + ' - ' + vals['codigoCurso']
        res = super(ConfiguracionesCursosLibre, self).create(vals)
        return res

class ConfiguracionesTutoriasLine(models.Model):
    _name="configuraciones.tutorias.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Configuracion Tutorias"

    configuracion_id = fields.Many2one(
        comodel_name="configuraciones",
        string="Configuracion",
        ondelete="cascade"
    )


    name = fields.Char(
        string="Descripcion",
        required=True,
    )

    numeroEstudiantes = fields.Integer(
        string="Cantidad de estudiantes",
        required=True,
    )
    semanasTutoria = fields.Integer(
        string="Semanas de Tutoria",
        required=True,
    )

    cantiadadHorasTutorias = fields.Integer(
        string="Horas de Tutoria",
        required=True,
    )


class ConfiguracionesTutoriasSemanaLine(models.Model):
    _name="configuraciones.tutorias.semana.line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Configuracion Tutorias"

    configuracion_id = fields.Many2one(
        comodel_name="configuraciones",
        string="Configuracion",
        ondelete="cascade"
    )

    tutoria_id = fields.Many2one(
        comodel_name="configuraciones.tutorias.line",
        string="Configuracion",
        ondelete="cascade"
    )

    semanaMarca = fields.Integer(
        string="Semana de Marca",
        required=True,
    )


class ConfiguracionesAjustes(models.TransientModel):
    _inherit = 'res.config.settings'

    correoEnvio = fields.Char(string="Correo de Envio", required=False, )
    correoEnvioHorarioErroneo = fields.Char(string="Correo de Envio Horarios Erroneos", required=False, )
    correoContactoPlanilla = fields.Char(string="Correo de Contacto de Planilla", required=False, )
    urlOdoo = fields.Char(string="Url de Aprobacion o Rechazo de Planilla", required=False, )
    correoAusencias = fields.Char(string="Correo de Reporte de Ausencias", required=False, )
    urlWSOdoo = fields.Char(string="Url de WS de odoo", required=False, )
    empleadosEnvioFaltaMarcas_ids = fields.Many2many(comodel_name="hr.employee", readonly=False)

    def set_values(self):
        """
            Asigna los valores de la configuracion guardada
        :return: valores de la configuracion
        """
        res = super(ConfiguracionesAjustes, self).set_values()
        self.env['ir.config_parameter'].set_param('nomina.correoEnvio', self.correoEnvio)
        self.env['ir.config_parameter'].set_param('nomina.correoContactoPlanilla', self.correoContactoPlanilla)
        self.env['ir.config_parameter'].set_param('nomina.correoAusencias', self.correoAusencias)
        self.env['ir.config_parameter'].set_param('nomina.urlOdoo', self.urlOdoo)
        self.env['ir.config_parameter'].set_param('nomina.urlWSOdoo', self.urlWSOdoo)
        self.env['ir.config_parameter'].set_param('nomina.correoEnvioHorarioErroneo', self.correoEnvioHorarioErroneo)
        self.env['ir.config_parameter'].set_param('nomina.empleadosEnvioFaltaMarcas_ids', self.empleadosEnvioFaltaMarcas_ids)
        return  res

    @api.model
    def get_values(self):
        """
            obtiene los valores de la configuracion para ser guardados
        :return: valores asignados
        """
        res = super(ConfiguracionesAjustes, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        correoEnvio = ICPSudo.get_param('nomina.correoEnvio')
        correoContactoPlanilla = ICPSudo.get_param('nomina.correoContactoPlanilla')
        correoAusencias = ICPSudo.get_param('nomina.correoAusencias')
        urlOdoo = ICPSudo.get_param('nomina.urlOdoo')
        urlWSOdoo = ICPSudo.get_param('nomina.urlWSOdoo')
        correoEnvioHorarioErroneo = ICPSudo.get_param('nomina.correoEnvioHorarioErroneo')
        res.update(
            correoEnvio = correoEnvio,
            correoContactoPlanilla = correoContactoPlanilla,
            correoAusencias=correoAusencias,
            urlOdoo = urlOdoo,
            urlWSOdoo = urlWSOdoo,
            correoEnvioHorarioErroneo = correoEnvioHorarioErroneo,
        )
        return  res

