# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class NominaContratoCuatrimestre(models.Model):
    _name = "contrato.cuatrimestre"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Contrato"

    
    name = fields.Char(
        string='Name',
    )
    

    tipo = fields.Selection(
        string='Nombre Contrato',
        required=True,
        tracking=True,
        selection=[
            ('medicina', 'Contrato Medicina'), 
            ('farmacia', 'Contrato Farmacia'),
            ('general', 'Contrato General')
            ]
    )
    
    tarifa = fields.Float(        
        digits=(16,2),
        required=True,
        tracking=True,   
        string='Tarifa por Hora'
    )
        
    horas  = fields.Float(
        digits=(2,1),
        required=True,
        tracking=True,
        string='Horas Semanales'
    )

    cuatrimestre_id = fields.Many2one(
        string='Cuatrimestre',
        required=True,
        tracking=True,
        comodel_name='periodo.cuatrimestre'
    )

    reference = fields.Char(string='Referencia ', required=True, copy=False, readonly=True,
                            default=lambda self: _('New'))

    active = fields.Boolean(
        string='Activo',
        tracking=True,
        default= True,
    )

    @api.model
    def create(self, vals):
        if vals.get('reference', _('New')) == _('New'):
            if vals['tipo'] == 'medicina':
                vals['reference'] = self.env['ir.sequence'].next_by_code('contrato.cuatrimestre.medicina') or _('New')
                vals['name'] = "["+vals['reference']+"] Contrato de Medicina"
            elif vals['tipo'] == 'farmacia':
                vals['reference'] = self.env['ir.sequence'].next_by_code('contrato.cuatrimestre.farmacia') or _('New')
                vals['name'] = "["+vals['reference']+"] Contrato de Farmacia"
            elif vals['tipo'] == 'general':
                vals['reference'] = self.env['ir.sequence'].next_by_code('contrato.cuatrimestre.general') or _('New')
                vals['name'] = "["+vals['reference']+"] Contrato de General"
            vals['tarifa'] = float(vals['tarifa'])/float('1.16163213964')
        res = super(NominaContratoCuatrimestre, self).create(vals)
        return res
    
    
