# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ConfiguracionesAjustes(models.TransientModel):
    _inherit = 'res.config.settings'

    correoEnvioNotificacionesPoliza = fields.Char(
        string="Correo de Envío de Notificaciones",
        required=False,
    )
    UrlAPI = fields.Char(
        string="URL de API",
        required=False,
    )

    def set_values(self):
        """
            Asigna los valores de la configuracion guardada
        :return: valores de la configuracion
        """
        res = super(ConfiguracionesAjustes, self).set_values()
        self.env['ir.config_parameter'].set_param('uia_poliza.correoEnvioNotificacionesPoliza', self.correoEnvioNotificacionesPoliza)
        self.env['ir.config_parameter'].set_param('uia_poliza.UrlAPI', self.UrlAPI)
        return  res

    @api.model
    def get_values(self):
        """
            obtiene los valores de la configuracion para ser guardados
        :return: valores asignados
        """
        res = super(ConfiguracionesAjustes, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        correoEnvioNotificacionesPoliza = ICPSudo.get_param('uia_poliza.correoEnvioNotificacionesPoliza')
        UrlAPI = ICPSudo.get_param('uia_poliza.UrlAPI')
        res.update(
            correoEnvioNotificacionesPoliza = correoEnvioNotificacionesPoliza,
            UrlAPI = UrlAPI,
        )
        return  res