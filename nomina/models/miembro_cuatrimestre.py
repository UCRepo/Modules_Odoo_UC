# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class NominaMiembroCuatrimestre(models.Model):
    _name = "miembro.cuatrimestre"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Miembros"
     
    
    cuatrimestre_id = fields.Many2one(
        string='Cuatrimestre',
        tracking=True,
        required=True,
        comodel_name='periodo.cuatrimestre',
        ondelete='restrict',
    ) 
        
    contrato_id = fields.Many2one(
        'contrato.cuatrimestre',
        string='Contrato',
        tracking=True,
        required=True
    )
    
    docentes_ids = fields.Many2many(
        'hr.employee',
        String ='Docentes',
        tracking=True
    )
    