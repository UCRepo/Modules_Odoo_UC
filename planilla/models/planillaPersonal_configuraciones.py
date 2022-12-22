# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PlanillaPersonalConfiguraciones(models.Model):
    _name = "planilla.personal.configuraciones"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description="Configuracion Empleados Planilla"

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        readonly=True,
        default=lambda self: self.env.company.currency_id
    )

    #region Renta
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
    #endregion

    #region Embargo
    salarioBase = fields.Float(
        string="Salario",
        required=False,
        currency_field='currency_id'
    )
    porcientoRebajoEmbargo = fields.Float(
        string="% de rebajo",
        required=False,
    )
    #endregion

    #region CCSS
    CCSSNormal = fields.Float(
        string="CCSS",
        required=False,
    )
    CCSSPensionado = fields.Float(
        string="CCSS pensionado",
        required=False,
    )
    #endregion

    #region Prestaciones
    aguinaldo = fields.Float(
        string="Aguinaldo",
        required=False,
    )
    cesantia  = fields.Float(
        string="Cesantia ",
        required=False,
    )
    preaviso = fields.Float(
        string=" Preaviso ",
        required=False,
    )
    vacaciones  = fields.Float(
        string="Vacaciones ",
        required=False,
    )
    #endregion

class ConfiguracionesAjustesPlanillaAdministrativa(models.TransientModel):
    _inherit = 'res.config.settings'

    correoEnvioAdministrativos = fields.Char(string="Direccion de correo maviso para administrativos", required=False, )
    correoEnvioCumple = fields.Char(string="Correo de envio de nofiticacion de cumpleaños", required=False, )
    planillaAPI = fields.Char(
        string="API",
        required=False,
    )

    def set_values(self):
        """
            Asigna los valores de la configuracion guardada
        :return: valores de la configuracion
        """
        res = super(ConfiguracionesAjustesPlanillaAdministrativa, self).set_values()
        self.env['ir.config_parameter'].set_param('planilla.correoEnvioAdministrativos', self.correoEnvioAdministrativos)
        self.env['ir.config_parameter'].set_param('planilla.correoEnvioCumple', self.correoEnvioCumple)
        self.env['ir.config_parameter'].set_param('planilla.planillaAPI', self.planillaAPI)
        return  res

    @api.model
    def get_values(self):
        """
            obtiene los valores de la configuracion para ser guardados
        :return: valores asignados
        """
        res = super(ConfiguracionesAjustesPlanillaAdministrativa, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        correoEnvioAdministrativos = ICPSudo.get_param('planilla.correoEnvioAdministrativos')
        correoEnvioCumple = ICPSudo.get_param('planilla.correoEnvioCumple')
        planillaAPI = ICPSudo.get_param('planilla.planillaAPI')
        res.update(
            correoEnvioAdministrativos = correoEnvioAdministrativos,
            correoEnvioCumple = correoEnvioCumple,
            planillaAPI = planillaAPI,
        )
        return  res