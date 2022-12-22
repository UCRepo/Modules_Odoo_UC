# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class EquipoCobrosConfiguraciones(models.TransientModel):
    _inherit = 'res.config.settings'

    equipoTrabajo = fields.Many2many(
        comodel_name="res.users",
        relation="configuraciones_equipo_cobros",
        string="Equipo de Trabajo",
    )
    cobrosURLAPI = fields.Char(
        string="Url de WS de odoo",
        required=False,
    )

    def set_values(self):
        """
            Asigna los valores de la configuracion guardada
        :return: valores de la configuracion
        """
        idsUsuarios = ''
        res = super(EquipoCobrosConfiguraciones, self).set_values()
        for data in self.equipoTrabajo:
            idsUsuarios += str(data.id)+","
        self.env['ir.config_parameter'].set_param('cobros.equipoTrabajo', idsUsuarios)
        self.env['ir.config_parameter'].set_param('cobros.cobrosURLAPI', self.cobrosURLAPI)
        return  res

    @api.model
    def get_values(self):
        """
            obtiene los valores de la configuracion para ser guardados
        :return: valores asignados
        """
        res = super(EquipoCobrosConfiguraciones, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        cobrosURLAPI = ICPSudo.get_param('cobros.cobrosURLAPI')
        usuariosList = []
        lines = []
        if ICPSudo.get_param('cobros.equipoTrabajo'):
            for data in ICPSudo.get_param('cobros.equipoTrabajo').split(','):
                if data:
                    usuariosList.append(self.env['res.users'].search([('id','=',data)]).id)

            lines  = [(6, 0, usuariosList)]

        res.update(
            equipoTrabajo=lines,
            cobrosURLAPI=cobrosURLAPI,
        )
        return  res