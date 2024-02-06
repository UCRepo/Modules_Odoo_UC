# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ProcesoGraduacionConfiguraciones(models.TransientModel):
    _inherit = 'res.config.settings'

    procesoGraduacioncorreoEnvioNotificaciones = fields.Char(
        string="Correo de envio de notificaciones",
        required=False,
    )
    procesoGraduacionURLAPI = fields.Char(
        string="Url API",
        required=False,
    )

    def set_values(self):
        """
            Asigna los valores de la configuracion guardada
        :return: valores de la configuracion
        """
        idsUsuarios = ''
        res = super(ProcesoGraduacionConfiguraciones, self).set_values()
        self.env['ir.config_parameter'].set_param('sa_graduacion.procesoGraduacioncorreoEnvioNotificaciones', self.procesoGraduacioncorreoEnvioNotificaciones)
        self.env['ir.config_parameter'].set_param('sa_graduacion.procesoGraduacionURLAPI', self.procesoGraduacionURLAPI)
        return  res

    @api.model
    def get_values(self):
        """
            obtiene los valores de la configuracion para ser guardados
        :return: valores asignados
        """
        res = super(ProcesoGraduacionConfiguraciones, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        procesoGraduacioncorreoEnvioNotificaciones = ICPSudo.get_param('sa_graduacion.procesoGraduacioncorreoEnvioNotificaciones')
        procesoGraduacionURLAPI = ICPSudo.get_param('sa_graduacion.procesoGraduacionURLAPI')

        res.update(
            procesoGraduacioncorreoEnvioNotificaciones=procesoGraduacioncorreoEnvioNotificaciones,
            procesoGraduacionURLAPI=procesoGraduacionURLAPI,
        )
        return  res