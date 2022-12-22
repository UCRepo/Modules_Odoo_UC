# -*- coding: utf-8 -*-
import io

try:
    from odoo.tools.misc import xlsxwriter
except:
    import xlsxwriter
from datetime import date, timedelta, datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class PlanillaCuatrimestreAceptados(models.Model):
    _name = "planilla.cuatrimestre.aceptados"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Planilla Cuatrimestre Aceptados"

    name = fields.Char(
        string="Nombre",
        required=False,
    )

    planilla_cuatrimestre_id = fields.Many2one(comodel_name="planilla.cuatrimestre", string="Cuatrimestre", required=True, tracking=True )

    planila_cuatrimestre_lines_ids = fields.Many2many(comodel_name="planilla.cuatrimestre.line",string="Docentes pago aceptado", )

    docentes = fields.Char(string="Docentes", required=False, compute="_count_docentes_pago")

    warning = fields.Boolean(default=False,)


    def _count_docentes_pago(self):
        if self.planilla_cuatrimestre_id.id != False:
            ids = []
            count = 0
            for rec in self:
                rec.planila_cuatrimestre_lines_ids = [(5,0,0)]
            dataPlanillaAceptadaDocente = self.env['planilla.cuatrimestre.line'].search([('docentesLinea_id','=',self.planilla_cuatrimestre_id.id)])
            for data in dataPlanillaAceptadaDocente:
                count += 1
                if data.prePlanillaAceptada == True:
                    ids.append(data.id)
            self.docentes = str(len(ids)) + " / " + str(count)
            self.planila_cuatrimestre_lines_ids = [(6, 0, ids)]

    def createXLSXReport(self):

        if self.planila_cuatrimestre_lines_ids.search(['&',('prePlanillaAceptada','=',True),('pagoEfectuado','=',False),('docentesLinea_id','=',self.planilla_cuatrimestre_id.id)]):
            return {
                'type': 'ir.actions.act_url',
                'url': '/sale/excel_report/%s' % (self.id),
                'target': 'new',
            }
        else:
            raise ValidationError("No existen nuevos docentes para agregar al pago")


    @api.onchange('planilla_cuatrimestre_id')
    def _onchangeMiembrosPlanillaId(self):
        ids = []
        count = 0
        for rec in self:
            rec.planila_cuatrimestre_lines_ids = [(5,0,0)]
        dataPlanillaAceptadaDocente = self.env['planilla.cuatrimestre.line'].search([('docentesLinea_id','=',self.planilla_cuatrimestre_id.id)])
        for data in dataPlanillaAceptadaDocente:
            count += 1
            if data.prePlanillaAceptada == True:
                ids.append(data.id)
        self.docentes = str(len(ids)) + " / " + str(count)
        self.planila_cuatrimestre_lines_ids = [(6, 0, ids)]
