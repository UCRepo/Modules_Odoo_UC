# -*- coding: utf-8 -*-
import io
from odoo.tools.misc import xlsxwriter
import pytz
import json
import requests
from odoo import http
from odoo.http import content_disposition, request
from datetime import date, timedelta, datetime


class SaleExcelReportController(http.Controller):
    @http.route(['/planillaAdministrativa/excel_report/<model("planilla.administrativa.pre.planilla"):planillaAdministrativa>',], type='http', auth="user", csrf=False)
    def get_sale_excel_report(self, planillaAdministrativa=None, **args):

        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Reporte de Pago Corte : ' + str(date.today()) +
                                                            " Del " + str(planillaAdministrativa.desde) +
                                                            " Al " + str(planillaAdministrativa.hasta) + '.xlsx'))
            ]
        )

        # create workbook object from xlsxwriter library
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 14, 'bold': True, 'align': 'center'})
        header_style = workbook.add_format(
            {'font_name': 'Times', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center'})
        text_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'left'})
        number_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right'})

        sheet = workbook.add_worksheet('Planilla')
        # loop all selected user/salesperson
        # for user in wizard.user_id:
        #     # create worksheet/tab per salesperson
        #     sheet = workbook.add_worksheet(user.name)
        #     # set the orientation to landscape
        #     sheet.set_landscape()
        #     # set up the paper size, 9 means A4
        #     sheet.set_paper(9)
        #     # set up the margin in inch
        #     sheet.set_margins(0.5, 0.5, 0.5, 0.5)
        #
        #     # set up the column width
        #     sheet.set_column('A:A', 5)
        #     sheet.set_column('B:E', 15)
        #
        #     # the report title
        #     # merge the A1 to E1 cell and apply the style font size : 14, font weight : bold
        #     sheet.merge_range('A1:E1', 'Sales Report in Excel Format', title_style)

        # table title
        sheet.write(0, 0, 'No.')
        sheet.write(0, 1, 'Nombre')
        sheet.write(0, 2, 'Monto')

        row = 1

        # search the sales order
        for empleado in planillaAdministrativa.miembrosPlanilla_id:
            if empleado.pagoEfectuado == False:
                empleado.pagoEfectuado = True
                empleado.fechaCorte = date.today()
                cedula = empleado.cedulaEmpleado.replace("-", "")
                if len(cedula) == 9:
                    sheet.write(row, 0, '0' + cedula)
                else:
                    sheet.write(row, 0, cedula)
                sheet.write(row, 1, empleado.nombreEmpleado)
                sheet.write(row, 2, empleado.salarioNeto)
                row += 1
        # # create a formula to sum the total sales
        # sheet.merge_range('A' + str(row + 1) + ':D' + str(row + 1), 'Total', text_style)
        # sheet.write_formula(row, 4, '=SUM(E3:E' + str(row) + ')', number_style)

        # return the excel file as a response, so the browser can download it
        # sheet.protect('password')
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

        return response

class ReporteMarcasAdministrativos(http.Controller):
    @http.route(['/planillaAdministrativa/asistencia_general/excel_report',], type='http', auth="user", csrf=False)
    def get_sale_excel_report(self,**kw):

        ICPSudo = request.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('nomina.urlWSOdoo')+'/api/AsistenciaAdministrativaUIA/getAsistenciaEmpleado'

        responseXLS = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Reporte de Asistencia : ' + str(date.today()) +
                                                            " Del " + str(request.params['desde']) +
                                                            " Al " + str(request.params['hasta']) + '.xlsx'))
            ]
        )

        # create workbook object from xlsxwriter library
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 14, 'bold': True, 'align': 'center'})
        header_style = workbook.add_format(
            {'font_name': 'Times', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center'})
        text_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'left'})
        number_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right'})

        sheet = workbook.add_worksheet('Asistencia')

        # table title
        sheet.write(0, 0, 'Nombre')
        sheet.write(0, 1, 'Dia')
        sheet.write(0, 2, 'Marcas')

        row = 1

        desdeT = datetime.strptime(request.params['desde'],"%Y-%m-%d")
        desdeSet = datetime.strptime(request.params['desde'],"%Y-%m-%d")
        hastaT = datetime.strptime(request.params['hasta'],"%Y-%m-%d")

        for empelado in request.env['hr.employee'].sudo().search(['&', ('department_id.name', '!=', 'Inactivos'), ('department_id.name', '!=', 'Docentes')]):
            sheet.write(row, 0,empelado.name )
            desdeT = desdeSet
            while desdeT <= hastaT:
                sheet.write(row, 1, desdeT)
                dataJSon = {
                    'codigoMarca': request.env['contrato.empleado'].search([('empleado_id', '=', empelado.id)]).codigoMarca,
                    'fechaMarca': str(desdeT.date()),
                }
                header = {
                    'Content-Type': 'application/json',
                    'Accept': 'text/plain'
                }
                response = requests.post(url, headers=header, json=dataJSon, verify=False)

                if response.status_code == 200:
                    for data in response.json()['data']:
                        sheet.write(row, 2, data['datetime'])
                        row += 1
                desdeT += timedelta(days=1)

        workbook.close()
        output.seek(0)
        responseXLS.stream.write(output.read())
        output.close()

        return responseXLS
