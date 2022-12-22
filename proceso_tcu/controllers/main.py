# -*- coding: utf-8 -*-
import io
from odoo.tools.misc import xlsxwriter
import pytz
import json
from odoo import http
from odoo.http import content_disposition, request
from datetime import date, timedelta, datetime

class CobrosMain(http.Controller):
    
    @http.route(['/cobros/excel_asignacion_administrativo/<model("cobros.periodo.pago"):idCobros>', ], type='http',auth="user", csrf=False)
    def get_comparativo_pago(self, idCobros=None, **args):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Letras.xlsx'))
            ]
        )