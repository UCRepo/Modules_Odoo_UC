# -*- coding: utf-8 -*-
import io
from odoo.tools.misc import xlsxwriter

from odoo import http
from odoo.http import content_disposition, request
from datetime import date, timedelta, datetime
class DocenteHome(http.Controller):
    @http.route('/my',type='http', auth='user', website=True)
    def contacto(self):
        return http.request.render('nomina.web_aceptacion_docente',{})

    @http.route('/my/home',type='http', auth='user', website=True)
    def contactos(self):
        return http.request.render('nomina.web_aceptacion_docente',{})



    @http.route('/get_docente_home',type='json',auth='public',website=True)
    def get_pagos_docente(self,**kw):
        id = request.env.user.name
        print(id)