import io
from odoo.tools.misc import xlsxwriter
import pytz
import json
import requests
from odoo import http
from odoo.http import content_disposition, request
from datetime import date, timedelta, datetime


class ExcelReportController(http.Controller):
    @http.route(['/poliza/excel_report/<model("poliza.generar.reporte.beneficiarios.wizard"):polizaId>',], type='http', auth="user", csrf=False)
    def get_poliza_excel_report(self, polizaId=None, **args):

        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Poliza UC Desde'+str(polizaId.polizaDesde)+' Hasta '+str(polizaId.polizaHasta)+ '.xlsx'))
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
        sheet.write(0, 0, 'Nombre')
        sheet.write(0, 1, 'Fecha de Nacimiento')
        sheet.write(0, 2, 'Genero')
        sheet.write(0, 3, 'Pais de Nacimiento')
        sheet.write(0, 4, 'Identificación')
        sheet.write(0, 5, 'Telefono')
        sheet.write(0, 6, 'Correo')
        sheet.write(0, 7, 'Dirección')
        sheet.write(0, 8, 'Beneficiario')
        sheet.write(0, 9, 'Nombre Beneficiario')
        sheet.write(0, 10, 'Parentesco de Beneficiario')
        sheet.write(0, 11, 'Telefono de Beneficiario')
        sheet.write(0, 12, 'Correo de Beneficiario')

        row = 1

        # search the sales order

        estudiantesPoliza =  request.env['poliza.informacion.line'].sudo().search(['&',('poliza_id', '=', polizaId.poliza.id),
                                                                                       ('datosActualizados','=',True),
                                                                                   ('fechaActualizacion','>=',polizaId.polizaDesde),
                                                                                   ('fechaActualizacion','<=',polizaId.polizaHasta)
                                                                                   ])
        for estudiante in estudiantesPoliza:
            # the report content
            sheet.write(row, 0, estudiante.nombre)
            sheet.write(row, 1, str(estudiante.fechaNacimiento))
            sheet.write(row, 2, estudiante.genero)
            sheet.write(row, 3, estudiante.paisNacimiento)
            sheet.write(row, 4, estudiante.identificacion)
            sheet.write(row, 5, estudiante.telefono)
            sheet.write(row, 6, estudiante.correo)
            sheet.write(row, 7, estudiante.direccion)
            sheet.write(row, 8, estudiante.beneficiarioIdentificacion)
            sheet.write(row, 9, estudiante.beneficiarioNombre)
            sheet.write(row, 10, estudiante.beneficiarioParentesco)
            sheet.write(row, 11, estudiante.beneficiarioTelefonoPrimario)
            sheet.write(row, 12, estudiante.beneficiarioEmail)
            row += 1

        # # create a formula to sum the total sales
        # sheet.merge_range('A' + str(row + 1) + ':D' + str(row + 1), 'Total', text_style)
        # sheet.write_formula(row, 4, '=SUM(E3:E' + str(row) + ')', number_style)

        # return the excel file as a response, so the browser can download it
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

        return response

    @http.route(['/poliza/excel_report_general/<model("poliza.generar.reporte.beneficiarios.wizard"):polizaId>',], type='http', auth="user", csrf=False)
    def get_poliza_excel_report_general(self, polizaId=None, **args):

        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Poliza UC General.xlsx'))
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
        sheet.write(0, 0, 'Nombre')
        sheet.write(0, 1, 'Fecha de Nacimiento')
        sheet.write(0, 2, 'Genero')
        sheet.write(0, 3, 'Pais de Nacimiento')
        sheet.write(0, 4, 'Identificación')
        sheet.write(0, 5, 'Telefono')
        sheet.write(0, 6, 'Correo')
        sheet.write(0, 7, 'Dirección')
        sheet.write(0, 8, 'Beneficiario')
        sheet.write(0, 9, 'Nombre Beneficiario')
        sheet.write(0, 10, 'Parentesco de Beneficiario')
        sheet.write(0, 11, 'Telefono de Beneficiario')
        sheet.write(0, 12, 'Correo de Beneficiario')

        row = 1

        # search the sales order

        estudiantesPoliza =  request.env['poliza.informacion.line'].sudo().search([('poliza_id', '=', polizaId.id)])

        for estudiante in estudiantesPoliza:
            # the report content
            sheet.write(row, 0, estudiante.nombre)
            sheet.write(row, 1, str(estudiante.fechaNacimiento))
            sheet.write(row, 2, estudiante.genero)
            sheet.write(row, 3, estudiante.paisNacimiento)
            sheet.write(row, 4, estudiante.identificacion)
            sheet.write(row, 5, estudiante.telefono)
            sheet.write(row, 6, estudiante.correo)
            sheet.write(row, 7, estudiante.direccion)
            sheet.write(row, 8, estudiante.beneficiarioIdentificacion)
            sheet.write(row, 9, estudiante.beneficiarioNombre)
            sheet.write(row, 10, estudiante.beneficiarioParentesco)
            sheet.write(row, 11, estudiante.beneficiarioTelefonoPrimario)
            sheet.write(row, 12, estudiante.beneficiarioEmail)
            row += 1

        # # create a formula to sum the total sales
        # sheet.merge_range('A' + str(row + 1) + ':D' + str(row + 1), 'Total', text_style)
        # sheet.write_formula(row, 4, '=SUM(E3:E' + str(row) + ')', number_style)

        # return the excel file as a response, so the browser can download it
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

        return response

class Poliza(http.Controller):
    @http.route('/formBeneficiarioPoliza', type='http', auth='public', website=True)
    def verificarasistenciadocente(self, **kw):
        idPoliza = request.params['idPoliza']
        idEstudiante = request.params['idEstudiante']
        polizaLine = request.env['poliza.informacion.line'].sudo().search(['&',('identificacion','=',idEstudiante),('poliza_id.id','=',idPoliza)])
        vals = {
            'identificacionEstudiante': idEstudiante,
            'idpoliza': idPoliza,
            'nombreEstudiante': polizaLine.nombre,
            'datosActualizados': str(False),
        }
        return request.render('uia_poliza.poliza_estudiante_form', vals)

    @http.route('/set_informacion_beneficiario', type='json', auth="public", website=True)
    def set_informacion_beneficiario(self,vals=None, **kw):
        ICPSudo = request.env['ir.config_parameter'].sudo()
        url = ICPSudo.get_param('uia_poliza.UrlAPI')+'/api/PolizaUC/setbeneficiarioInfo'
        poliza  = request.env['poliza.informacion.line'].sudo().search(['&',('identificacion','=',vals['idEstudiante']),('poliza_id.id','=',vals['idPoliza'])])
        user_tz = pytz.timezone(request.env.user.tz)

        poliza.beneficiarioIdentificacion = vals['identificacionBeneficiario']
        poliza.beneficiarioNombre = vals['nombreBeneficiario']
        poliza.beneficiarioParentesco = vals['parentescoBeneficiario']
        poliza.beneficiarioTelefonoPrimario = vals['telefonoBeneficiario']
        poliza.beneficiarioEmail = vals['correoBeneficiario']
        poliza.datosActualizados = True
        poliza.fechaActualizacion = pytz.utc.localize(datetime.today()).astimezone(user_tz).date()

        dataJSon = {
            "year": int(poliza.poliza_id.anno),
            "periodo": int(poliza.poliza_id.periodo),
            "cedulaEstudiante": vals['idEstudiante'],
            "cedulaBeneficiario": vals['identificacionBeneficiario'],
            "nombreBeneficiario": vals['nombreBeneficiario'],
            "parentescoBeneficiario": vals['parentescoBeneficiario'],
            "numeroTelefonoBeneficiario": vals['telefonoBeneficiario'] if vals['telefonoBeneficiario'] != '' else '88888888',
            "correoBeneficiario": vals['correoBeneficiario'] if vals['correoBeneficiario'] != '' else 'none@email.com',
            "tipoIdentificacionBeneficiario": vals['tipoIdentificacion']
        }
        header = {
            'Content-Type': 'application/json',
            'Accept': 'text/plain'
        }
        response = requests.post(url, headers=header, json=dataJSon, verify=False)

        return {
            'result':True
        }