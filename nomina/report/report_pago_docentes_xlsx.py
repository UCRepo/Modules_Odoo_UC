# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class PagoDocentesXLSX(models.AbstractModel):
    _name = 'report.nomina.report_pago_docentes_xlsx_id'


    @api.model
    def _get_report_values(self, docids, data):
        docente_pago_report = self.env['ir.actions.report']._get_report_from_name('nomina.report_pago_docentes_xlsx_id')
        return {
            'doc_ids': self.ids,
            'doc_model': docente_pago_report.model,
            'get_pagos': self.get_pagos(data['planilla_cuatrimestre_id']),
        }

    def get_pagos(self,planilla_cuatrimestre_id):
        dataPago = self.env['planilla.cuatrimestre.line'].search([('idcuatrimestre','=',1)])

        dataReport = []
        dataReport.append('id,nombre,monto')
        for data in dataPago:
            dataReport.append(str(data.cedulaDocente)+','+data.nombreDocente+','+str(data.totalDocente))

        return dataReport
