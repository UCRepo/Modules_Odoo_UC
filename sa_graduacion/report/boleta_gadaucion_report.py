import pytz
import logging
from datetime import date, timedelta, datetime
from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)

class BoletaGraduacion(models.AbstractModel):
    _name='report.sa_graduacion.report_boleta_gradaucion_id'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sa.graduacion.estudiante'].sudo().browse(docids)
        f =  docs.mapped('tarifa_ids')
        return {
            'docs': f[0],
            'doc_model': 'sa.malla.curricular',
            'get_malla_curricular': self.get_malla_curricular(docs),
        }