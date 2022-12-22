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


        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})


        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 14, 'bold': True, 'align': 'center'})
        header_style = workbook.add_format(
            {'font_name': 'Times', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center'})
        text_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'left'})
        number_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right'})

        sheet = workbook.add_worksheet('Asistencia')

        sheet.write(0, 0, 'Estudiante')
        sheet.write(0, 1, 'Carnet')
        sheet.write(0, 2, 'Letra')
        sheet.write(0, 3, 'Monto Letra')
        row = 1

        for data in idCobros.estudiantesCobro_ids:
            sheet.write(row, 0, data.nombreEstudiante)
            sheet.write(row, 1, data.carnetEstudiante)
            sheet.write(row, 2, data.numeroLetra)
            sheet.write(row, 3, data.totalLetra)

            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

        return response

    @http.route(['/cobros/excel_reporte_estado_pago/<model("cobros.reporte.estado.letras.wizard"):idCobros>', ], type='http',auth="user", csrf=False)
    def get_comparativo_pago(self, idCobros=None, **args):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Reporte de '+idCobros.tipoEstadoPago+'.xlsx'))
            ]
        )


        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})


        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 14, 'bold': True, 'align': 'center'})
        header_style = workbook.add_format(
            {'font_name': 'Times', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center'})
        text_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'left'})
        number_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right'})

        sheet = workbook.add_worksheet('Asistencia')

        sheet.write(0, 0, 'Estudiante')
        sheet.write(0, 1, 'Carnet')
        sheet.write(0, 2, 'Letra')
        sheet.write(0, 3, 'Monto Letra')
        sheet.write(0, 3, 'Estado')
        row = 1

        letras = list(filter(lambda x: (x.estadoPago == idCobros.tipoEstadoPago), idCobros.periodoPago_id.estudiantesCobro_ids ))

        for data in letras:
            sheet.write(row, 0, data.nombreEstudiante)
            sheet.write(row, 1, data.carnetEstudiante)
            sheet.write(row, 2, data.numeroLetra)
            sheet.write(row, 3, data.totalLetra)
            sheet.write(row, 3, data.estadoPago)

            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

        return response