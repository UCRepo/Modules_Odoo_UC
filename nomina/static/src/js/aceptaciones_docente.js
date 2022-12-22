odoo.define('nomina.aceptaciones_docente', function (require) {
    "use strict";

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var core = require('web.core');

    var _t = core._t;
    var cuatriID;
    var docenteID;
    var cuatriName;
    var fechaInicioPago;
    var fechaFinalPago;
    var correoConsulta;
    if (location.pathname.includes('/aceptacionesdocentes')) {
        load();
    }
    function load(e) {

        try {

            var contenedor = document.querySelector('#web_nomina_planilla_cuatrimestre_container_pagos');
            ajax.jsonRpc('/get_pagos_docente', 'call', {}).then(function (result) {

                cuatriID = result['cuatriID'];
                docenteID = result['docenteID'];
                cuatriName = result['cuatriName'];
                fechaInicioPago = result['fechaInicioPago'];
                fechaFinalPago = result['fechaFinalPago'];
                correoConsulta = result['correoConsulta'];

                if (result['estadoPago']) {
                    btnAceptarPlanilla()
                } else {
                    if (result != null) {
                        var div_row_principal = document.createElement('div');
                        div_row_principal.className = "row";
                        div_row_principal.style.marginTop = "5px";

                        var div_row_secundario = document.createElement('div');
                        div_row_secundario.className = "row";

                        var div_col_primario = document.createElement('div');
                        div_col_primario.className = "col";

                        var button_aceptar_planilla = document.createElement('button');
                        button_aceptar_planilla.appendChild(document.createTextNode("Aceptar"));
                        button_aceptar_planilla.type = "button";
                        button_aceptar_planilla.name = "btnAceptarPago";
                        button_aceptar_planilla.className = "btn btn-success";
                        button_aceptar_planilla.value = "aceptar";
                        button_aceptar_planilla.style.borderRadius = "5px";
                        button_aceptar_planilla.id = "btnAceptar";
                        button_aceptar_planilla.onclick = btnAceptarPlanilla;


                        var div_col_secundario = document.createElement('div');
                        div_col_secundario.className = "col";

                        var button_rechazar_planilla = document.createElement('button');
                        button_rechazar_planilla.appendChild(document.createTextNode("Rechazar"));
                        button_rechazar_planilla.type = "button";
                        button_rechazar_planilla.name = "btnRechazarPago";
                        button_rechazar_planilla.className = "btn btn-warning";
                        button_rechazar_planilla.value = "rechazar";
                        button_rechazar_planilla.style.borderRadius = "5px";
                        button_rechazar_planilla.id = "btnRechazar";
                        button_rechazar_planilla.onclick = btnRechazarPlanilla;

                        var div_col_sm_9 = document.createElement('div');
                        div_col_sm_9.className = "col-sm-9";

                        var div_col_sm_9_row = document.createElement('div');
                        div_col_sm_9_row.className = "row";

                        var div_col_8_6 = document.createElement('div');
                        div_col_8_6.className = "col-8 col-sm-6";

                        var div_col_4_6 = document.createElement('div');
                        div_col_4_6.className = "col-4 col-sm-6";

                        var p_col_8_6 = document.createElement('p');
                        p_col_8_6.appendChild(document.createTextNode(result['cuatriName'] + " Del " + result['fechaInicioPago'] + " al " + result['fechaFinalPago']));
                        p_col_8_6.className = "text-center";
                        p_col_8_6.style.fontSize = "15px";
                        p_col_8_6.style.fontWeight = "900";
                        p_col_8_6.style.marginLeft = "100px"

                        var p__col_4_6 = document.createElement('p');
                        p__col_4_6.appendChild(document.createTextNode("₡ " + result['pago']));
                        p__col_4_6.className = "text-center";
                        p__col_4_6.style.fontSize = "15px";
                        p__col_4_6.style.fontWeight = "900";

                        div_col_8_6.appendChild(p_col_8_6);
                        div_col_4_6.appendChild(p__col_4_6);

                        div_col_sm_9_row.appendChild(div_col_8_6);
                        div_col_sm_9_row.appendChild(div_col_4_6);

                        div_col_sm_9.appendChild(div_col_sm_9_row);

                        div_col_primario.appendChild(button_aceptar_planilla);
                        div_col_secundario.appendChild(button_rechazar_planilla);

                        div_row_secundario.appendChild(div_col_primario);
                        div_row_secundario.appendChild(div_col_secundario);

                        div_row_principal.appendChild(div_row_secundario);
                        div_row_principal.appendChild(div_col_sm_9);

                        contenedor.appendChild(div_row_principal);

                    }
                }
            })

        } catch (err) {

        }
    }

    function btnAceptarPlanilla() {
        try {
            ajax.jsonRpc('/set_aceptar_planilla', 'call', {
                'docenteID': docenteID,
                'cuatriID': cuatriID
            }).then(function (result) {
                if (result) {
                    var alertPlaceholder = document.getElementById('web_nomina_planilla_cuatrimestre_container_pagos')
                    alertPlaceholder.innerHTML = "";
                    var div_alert = document.createElement('div');
                    div_alert.className = "alert alert-success";
                    div_alert.style.borderRadius = "5px";
                    div_alert.style.marginTop = "5px";
                    div_alert.appendChild(document.createTextNode("Pago " + cuatriName + " Del " + fechaInicioPago + " al " + fechaFinalPago + " Fue Aceptado"));
                    div_alert.style.fontSize = "15px";
                    div_alert.style.fontWeight = "900";
                    alertPlaceholder.appendChild(div_alert);
                } else {
                }
            })
        } catch (err) {

        }
    }

    function btnRechazarPlanilla() {
        try {
            ajax.jsonRpc('/set_rechazar_planilla', 'call', {
                'docenteID': docenteID,
                'cuatriID': cuatriID
            }).then(function (result) {
                if (result) {
                    var alertPlaceholder = document.getElementById('web_nomina_planilla_cuatrimestre_container_pagos')
                    alertPlaceholder.innerHTML = "";
                    var div_alert = document.createElement('div');
                    div_alert.className = "alert alert-success";
                    div_alert.appendChild(document.createTextNode("En caso de duda o reclamo nos puede contactar al correo " + correoConsulta));
                    alertPlaceholder.appendChild(div_alert);
                } else {
                }
            })
        } catch (err) {

        }
    }


});