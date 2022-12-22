# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class ConfiguracionesAjustes(models.TransientModel):
    _inherit = 'res.config.settings'

    empleado_id = fields.Many2one(
        required=False,
        comodel_name='hr.employee',
    )

    def set_values(self):
        """
            Asigna los valores de la configuracion guardada
        :return: valores de la configuracion
        """
        res = super(ConfiguracionesAjustes, self).set_values()
        self.env['ir.config_parameter'].set_param('uia_portal.empleado_id', self.empleado_id.id)
        return  res

    @api.model
    def get_values(self):
        """
            obtiene los valores de la configuracion para ser guardados
        :return: valores asignados
        """
        res = super(ConfiguracionesAjustes, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        empleado_id = self.env['hr.employee'].browse(int(ICPSudo.get_param('uia_portal.empleado_id')))
        res.update(
            empleado_id = empleado_id,
        )
        return  res

