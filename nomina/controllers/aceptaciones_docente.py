# -*- coding: utf-8 -*-
import io
from odoo.tools.misc import xlsxwriter
import pytz
import json
from odoo import http
from odoo.http import content_disposition, request
from datetime import date, timedelta, datetime

class AceptacionesDocente(http.Controller):
    cuatriID = any
    docenteID = any
    pago = any

    @http.route('/marcaasistenciadocente', type='http', auth='public', methods=['GET', 'POST'],cors='*',csrf=False)
    def marcaAsistenciaDocente(self, **kw):
        cedulaDocente = request.params['cedula']
        data = {}
        anno = datetime.today()

        docentes = request.env['hr.employee'].sudo().search([('department_id.name', '=','Docentes')])
        docente = any
        for data in docentes:
            if data.identification_id != False:
                cedDocente = data.identification_id.replace("-","")
                if cedDocente == cedulaDocente:
                    docente = data

        marca = request.env['hr.attendance'].sudo().search(['&',('employee_id','=',docente.id),('check_in','<',anno),('check_out','=',False)])

        if marca:
            marca.check_out = anno
            result = anno - timedelta(hours=6)
            data = {
                "marcaAsistencia": str(result.time().replace(microsecond=0)),
            }
        else:
            vals = {
                'employee_id': docente.id,
                'check_in': anno,
            }
            res = request.env['hr.attendance'].sudo().create(vals)
            result = anno - timedelta(hours=6)
            data = {
                "marcaAsistencia": str(result.time().replace(microsecond=0)),
            }
        return request.make_response(data=json.dumps(data), headers=[('Content-Type', 'application/json')])

    @http.route('/verificarasistenciadocente', type='http', auth='public', methods=['GET', 'POST'],cors='*',csrf=False)
    def verificarasistenciadocente(self, **kw):
        cedulaDocente = request.params['cedula']
        data = {}
        anno = datetime.today() + timedelta(hours=6)

        docentes = request.env['hr.employee'].sudo().search([('department_id.name', '=','Docentes')])
        docente = any
        for data in docentes:
            if data.identification_id != False:
                cedDocente = data.identification_id.replace("-","")
                if cedDocente == cedulaDocente:
                    docente = data

        if docente:
            marca = request.env['hr.attendance'].sudo().search(['&',('employee_id','=',docente.id),('check_in','<',anno),('check_out','=',False)])

            if marca:
                data = {
                    "marcaAsistencia": "SI"
                }
            else:
                data = {
                    "marcaAsistencia": "NO"
                }
            return request.make_response(data=json.dumps(data), headers=[('Content-Type', 'application/json')])


    @http.route('/aceptacionesdocentes',type='http', auth='public', website=True)
    def contacto_render(self, **kw):
        self.cuatriID = request.params['cuatriID']
        self.docenteID = request.params['docenteID']
        self.pago = request.params['pago']
        return http.request.render('nomina.web_aceptacion_docente',{})

    @http.route('/get_pagos_docente',type='json',auth='public',website=True)
    def get_pagos_docente(self,**kw):
        if self.docenteID != any and self.cuatriID != any:
            datosPrePlanillaDocente = request.env['planilla.cuatrimestre.line'].sudo().search(['&',('docente_id.id', '=',self.docenteID),('cuatrimestre_id.id','=',self.cuatriID),('pago','=',self.pago)])
            datosCuatrimestre = request.env['planilla.cuatrimestre'].sudo().search(['&',('cuatrimestrePlanilla_id', '=', int(self.cuatriID)),('pago','=',self.pago)])
            ICPSudo = request.env['ir.config_parameter'].sudo()
            result = {
                'cuatriID': self.cuatriID,
                'docenteID': self.docenteID,
                'cuatriName': datosCuatrimestre.cuatrimestrePlanilla_id.name,
                'estadoPago': datosPrePlanillaDocente.prePlanillaAceptada,
                'pago': "{:,}".format(datosPrePlanillaDocente.totalDocente),
                'fechaInicioPago': datosCuatrimestre.fechaInicioPago,
                'fechaFinalPago' : datosCuatrimestre.fechaFinalPago,
                'correoConsulta': ICPSudo.get_param('nomina.correoContactoPlanilla')
            }
            return result

    @http.route('/set_aceptar_planilla', type='json', auth='public', website=True)
    def set_aceptar_planilla(self, **kw):
        try:
            datosPrePlanillaDocente = request.env['planilla.cuatrimestre.line'].sudo().search(['&', ('docente_id.id', '=', request.params['docenteID']), ('cuatrimestre_id.id', '=', request.params['cuatriID'])])
            datosPrePlanillaDocente.prePlanillaAceptada = True
            return True
        except:
            return False

    @http.route('/set_rechazar_planilla', type='json', auth='public', website=True)
    def set_rechazar_planilla(self, **kw):
        try:
            datosPrePlanillaDocente = request.env['planilla.cuatrimestre.line'].sudo().search(['&', ('docente_id.id', '=', request.params['docenteID']), ('cuatrimestre_id.id', '=', request.params['cuatriID'])])
            datosPrePlanillaDocente.prePlanillaAceptada = False
            return True
        except:
            return False

class SaleExcelReportController(http.Controller):
    @http.route(['/sale/excel_report/<model("planilla.cuatrimestre"):idPlanilla>',], type='http', auth="user", csrf=False)
    def get_sale_excel_report(self, idPlanilla=None, **args):

        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Reporte de Pago Corte : ' + str(date.today()) +
                                                            " Del " + str(idPlanilla.fechaInicioPago) +
                                                            " Al " + str(idPlanilla.fechaFinalPago) + '.xlsx'))
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

        docentesAceptado =  request.env['planilla.cuatrimestre.line'].sudo().search(['&',('totalDocente', '>', 0),('pagoEfectuado','=',False),('prePlanillaAceptada','=',True),('docentesLinea_id','=',idPlanilla.id)])

        listDocentesCuentaBACActiva = list(filter(lambda x: x.cuentaBacActiva == True,docentesAceptado))
        listDocentesCuentaBACNoActiva = list(filter(lambda x: x.cuentaBacActiva == False,docentesAceptado))
        for aceptados in listDocentesCuentaBACActiva:
            aceptados.pagoEfectuado = True
            aceptados.fechaCorte = date.today()
            sheet.write(row, 0, aceptados.cuentaBac)
            sheet.write(row, 1, aceptados.nombreDocente)
            sheet.write(row, 2, aceptados.totalDocente)

            row += 1

        row += 5
        for aceptados in listDocentesCuentaBACNoActiva:
            aceptados.pagoEfectuado = True
            aceptados.fechaCorte = date.today()
            sheet.write(row, 0, aceptados.cuentaBac)
            sheet.write(row, 1, aceptados.nombreDocente)
            sheet.write(row, 2, aceptados.totalDocente)

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

    @http.route(['/nomina/excel_pago_docente_detallado_report/<model("planilla.cuatrimestre"):idPlanilla>', ], type='http', auth="user",csrf=False)
    def get_pago_docente_detallado_xls_report(self, idPlanilla=None, **args):

        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Reporte de Pago Detallado Corte : ' + str(date.today()) +
                                                            " Del " + str(idPlanilla.fechaInicioPago) +
                                                            " Al " + str(idPlanilla.fechaFinalPago) + '.xlsx'))
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
        sheet.write(0, 2, 'Bruto')
        sheet.write(0, 3, 'Total')
        sheet.write(0, 4, 'CCSS')
        sheet.write(0, 5, 'Renta')
        sheet.write(0, 6, 'Entrada Tardia')
        sheet.write(0, 7, 'Salida Temprana')
        sheet.write(0, 8, 'Omision Marca')
        sheet.write(0, 9, 'Embargo')
        sheet.write(0, 10, 'Total Deducciones')
        sheet.write(0, 11, 'Rebajos')
        sheet.write(0, 12, 'Total Adicionales')
        sheet.write(0, 13, 'Aguinaldo')
        sheet.write(0, 14, 'Cesantia')
        sheet.write(0, 15, 'Preaviso')
        sheet.write(0, 16, 'Vacaciones')

        row = 1

        # search the sales order

        docentesAceptado =  request.env['planilla.cuatrimestre.line'].sudo().search(['&',('totalDocente', '>', 0),('docentesLinea_id','=',idPlanilla.id)])

        for aceptados in docentesAceptado:
            aceptados.pagoEfectuado = True
            aceptados.fechaCorte = date.today()
            sheet.write(row, 0, aceptados.cedulaDocente)
            sheet.write(row, 1, aceptados.nombreDocente)
            sheet.write(row, 2, aceptados.brutoDocente)
            sheet.write(row, 3, aceptados.totalDocente)
            sheet.write(row, 4, aceptados.CCSSDocente)
            sheet.write(row, 5, aceptados.rentaDocente)
            sheet.write(row, 6, aceptados.deducionesEntradaTardia)
            sheet.write(row, 7, aceptados.deducionesSalidaTemprana)
            sheet.write(row, 8, aceptados.deducionesOmisionMarca)
            sheet.write(row, 9, aceptados.embargo)
            sheet.write(row, 10, aceptados.totalDeduccionDocente)
            sheet.write(row, 11, aceptados.rebajosNeto)
            sheet.write(row, 12, aceptados.adicionales)
            sheet.write(row, 13, aceptados.aguinaldoDocente)
            sheet.write(row, 16, aceptados.vacacionesDocente)

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

    @http.route(['/nomina/excel_prediccion_pago_docente_report/<model("planilla.cuatrimestre"):idPlanilla>', ], type='http', auth="user",csrf=False)
    def get_prediccion_pago_docente_xls_report(self, idPlanilla=None, **args):

        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Predicción.xlsx'))
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
        sheet.write(0, 2, 'Bruto')
        row = 1

        # search the sales order

        Docente =  request.env['cursos.docente'].sudo().search([('cuatrimestre_id','=',idPlanilla.cuatrimestrePlanilla_id.id)])

        for dataDocente in Docente:
            brutoDocente = 0
            tasa = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', dataDocente.docente_id.id)]).salario
            sheet.write(row, 0, dataDocente.docente_id.identification_id)
            sheet.write(row, 1, dataDocente.docente_id.name)
            for data in dataDocente.cursos_lines_ids:
                cursoMD = request.env['configuraciones.cursos.medicina'].search([('codigoCurso', '=', data.codigoCurso)])
                if cursoMD:
                    brutoDocente += cursoMD.tarifaCurso * (data.cantiadadHoras * 15)
                else:
                    brutoDocente += tasa * (data.cantiadadHoras * 15)

            sheet.write(row, 2, brutoDocente)

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

    @http.route(['/nomina/excel_reporte_marcas_justificadas/<model("planilla.cuatrimestre"):idPlanilla>', ], type='http', auth="user",csrf=False)
    def get_excel_reporte_marcas_justificadas(self, idPlanilla=None, **args):

        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Reporte de Justificaciones.xlsx'))
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

        sheet.write(0, 0, 'Docente')
        sheet.write(0, 1, 'Curso')
        sheet.write(0, 2, 'Horario')
        sheet.write(0, 3, 'Justifica Marca')
        row = 1



        asistencia =  request.env['asistencia.docente.line'].sudo().search(['&',('marcaJustificada','=',True),("fechaCurso",'>=',idPlanilla.fechaInicioPago),("fechaCurso",'<=',idPlanilla.fechaFinalPago)])

        for data in asistencia:
            sheet.write(row, 0, data.docente_id.name)
            sheet.write(row, 1, data.cursoMarca)
            sheet.write(row, 2, data.horarioCurso)
            sheet.write(row, 3, data.empleadoJustificacion.name)
            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

        return response

    @http.route(['/nomina/excel_comparativo_pago/<model("planilla.cuatrimestre"):idPlanilla>', ], type='http',auth="user", csrf=False)
    def get_comparativo_pago(self, idPlanilla=None, **args):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Comparativo Pago.xlsx'))
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

        sheet.write(0, 0, 'Docente')
        sheet.write(0, 1, 'Pago Perfecto')
        sheet.write(0, 2, 'Pago Actual')
        row = 1



        planilla =  request.env['planilla.cuatrimestre.line'].sudo().search([('docentesLinea_id','=',idPlanilla.id)])
        calculosPlanilla = request.env['configuraciones'].sudo().search([])

        for data in planilla:
            if data.totalDocente > 0:
                CCSS = 0
                renta = 0
                embargo = 0

                sheet.write(row, 0, data.docente_id.name)
                sheet.write(row, 2, data.totalDocente)
                contratoDocente = request.env['contrato.empleado'].sudo().search([('empleado_id', '=', data.docente_id.id)])
                calculo = data.horasContratoDocente * contratoDocente.salario

                calculo += data.adicionales

                if contratoDocente.pensionado == False:
                    CCSS = calculo * calculosPlanilla.CCSSNormal
                else:
                    CCSS = calculo * calculosPlanilla.CCSSPensionado

                if calculo > calculosPlanilla.desde0 and calculo < calculosPlanilla.hasta0:
                    renta += (calculo - calculosPlanilla.desde0) * calculosPlanilla.porciento0

                elif calculo > calculosPlanilla.desde1 and calculo < calculosPlanilla.hasta1:

                    renta += (calculosPlanilla.hasta0 - calculosPlanilla.desde0) * calculosPlanilla.porciento0
                    renta += (calculo - calculosPlanilla.desde1) * calculosPlanilla.porciento1

                elif calculo > calculosPlanilla.desde2 and calculo < calculosPlanilla.hasta2:

                    renta += (calculosPlanilla.hasta0 - calculosPlanilla.desde0) * calculosPlanilla.porciento0
                    renta += (calculosPlanilla.hasta1 - calculosPlanilla.desde1) * calculosPlanilla.porciento1
                    renta += (calculo - calculosPlanilla.desde2) * calculosPlanilla.porciento2

                elif calculo > calculosPlanilla.desde3:

                    renta += (calculosPlanilla.hasta0 - calculosPlanilla.desde0) * calculosPlanilla.porciento0
                    renta += (calculosPlanilla.hasta1 - calculosPlanilla.desde1) * calculosPlanilla.porciento1
                    renta += (calculosPlanilla.hasta2 - calculosPlanilla.desde2) * calculosPlanilla.porciento2
                    renta += (calculo - calculosPlanilla.desde3) * calculosPlanilla.porciento3

                if contratoDocente.embargo:
                    preCalculo  = calculo - (calculosPlanilla.salarioBase * 2 )
                    if preCalculo > 1000:
                        embargo = preCalculo * calculosPlanilla.porcientoRebajoEmbargo

                calculo -= embargo

                totalDeducciones = (CCSS + renta)
                aguinaldo = (calculo) * calculosPlanilla.aguinaldo
                vacaciones = (calculo) * calculosPlanilla.vacaciones
                calculo = (calculo + aguinaldo + vacaciones) - totalDeducciones

                sheet.write(row, 1, calculo)

                row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

        return response

class ExcelReportPlanillaTesis(http.Controller):
    @http.route(['/planilla/report_excel_planilla_tesis/<model("planilla.tesis"):planillaTesis>', ], type='http', auth="user",csrf=False)
    def report_excel_planilla_tesis(self, planillaTesis=None, **args):

        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Reporte de Pago Tesis Corte : ' + str(date.today()) + '.xlsx'))
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

        for aceptados in list(filter(lambda x: x.cuentaBacActiva == True, planillaTesis.miembrosPlanilla_id)):
            aceptados.pagoEfectuado = True
            sheet.write(row, 0, aceptados.cuentaBac)
            sheet.write(row, 1, aceptados.nombreDocente)
            sheet.write(row, 2, aceptados.totalDocente)

            row += 1

        row += 5
        for aceptados in list(filter(lambda x: x.cuentaBacActiva == False, planillaTesis.miembrosPlanilla_id)):
            aceptados.pagoEfectuado = True
            sheet.write(row, 0, aceptados.cuentaBac)
            sheet.write(row, 1, aceptados.nombreDocente)
            sheet.write(row, 2, aceptados.totalDocente)

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

class ExcelReportPlanillaCursosLibres(http.Controller):
    @http.route(['/planilla/report_excel_planilla_cursos_libres/<model("planilla.tesis"):planillaCursosLibres>', ], type='http', auth="user",csrf=False)
    def report_excel_planilla_cursos_libres(self, planillaCursosLibres=None, **args):

        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Reporte de Pago Cursos Libre Corte : ' + str(date.today()) + '.xlsx'))
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

        for aceptados in list(filter(lambda x: (x.cuentaBacActiva == True) and  (x.pagoEfectuado == False), planillaCursosLibres.miembrosPlanilla_id)):
            aceptados.pagoEfectuado = True
            sheet.write(row, 0, aceptados.cuentaBac)
            sheet.write(row, 1, aceptados.nombreDocente)
            sheet.write(row, 2, aceptados.totalDocente)

            row += 1

        row += 5
        for aceptados in list(filter(lambda x: (x.cuentaBacActiva == False) and  (x.pagoEfectuado == False), planillaCursosLibres.miembrosPlanilla_id)):
            aceptados.pagoEfectuado = True
            sheet.write(row, 0, aceptados.cuentaBac)
            sheet.write(row, 1, aceptados.nombreDocente)
            sheet.write(row, 2, aceptados.totalDocente)

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