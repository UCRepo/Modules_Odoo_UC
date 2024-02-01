odoo.define('uia_portal.users_portal', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
const Dialog = require('web.Dialog');
const {_t, qweb} = require('web.core');
const ajax = require('web.ajax');
var rpc = require('web.rpc');
var fechaMaximaJustificacion = new Date();
var rangoFechasJustificacion = "";
var pagoMarca = "";
var currency = 'CRC';
var cant_dias = 0;


publicWidget.registry.UIAPortalHome= publicWidget.Widget.extend({
    selector: '.uia_porta_administrativo',

    start: function () {
        this._updateMenu();
    },
    async _updateMenu(elem) {
        var contenedor = document.querySelector('#uia_portal_menu_administrativo');
        ajax.jsonRpc('/uia_menu_portal', 'call', {}).then(function (result){
            
            var button_gestion_vacaciones = document.createElement('button');
            button_gestion_vacaciones.appendChild(document.createTextNode("Gestionar Vacaciones"));
            button_gestion_vacaciones.type = "button";
            button_gestion_vacaciones.name = "btnGestionVacaciones";
            button_gestion_vacaciones.className = "btn btn-outline-primary";
            //button_gestion_vacaciones.style.borderRadius = "5px";
            button_gestion_vacaciones.id = "btnGestionVacaciones";
            button_gestion_vacaciones.onclick = btn_gestion_vacacioines;

            var button_gestion_vacaciones_colaboradores = document.createElement('button');
            button_gestion_vacaciones_colaboradores.appendChild(document.createTextNode("Gestionar Vacaciones de los Colaboradores"));
            button_gestion_vacaciones_colaboradores.type = "button";
            button_gestion_vacaciones_colaboradores.name = "btnCargarAjustesPago";
            button_gestion_vacaciones_colaboradores.className = "btn btn-outline-primary";
            //button_gestion_incapacidades.style.borderRadius = "5px";
            button_gestion_vacaciones_colaboradores.id = "btnCargarAdicionlaes";
            button_gestion_vacaciones_colaboradores.onclick = btn_gestion_vacaciones_colaboradores;

            var button_gestion_timepo_acomulado = document.createElement('button');
            button_gestion_timepo_acomulado.appendChild(document.createTextNode("Gestionar Tiempo Acumulado"));
            button_gestion_timepo_acomulado.type = "button";
            button_gestion_timepo_acomulado.name = "btnGestionTiempoAcomulado";
            button_gestion_timepo_acomulado.className = "btn btn-outline-primary";
            //button_gestion_timepo_acomulado.style.borderRadius = "5px";
            button_gestion_timepo_acomulado.id = "btnGestionTiempoAcomulado";
            button_gestion_timepo_acomulado.onclick = btn_gestion_tiempo_acumulado;

            var button_gestion_incapacidades = document.createElement('button');
            button_gestion_incapacidades.appendChild(document.createTextNode("Gestionar Incapacidades"));
            button_gestion_incapacidades.type = "button";
            button_gestion_incapacidades.name = "btnGestionIncapacidades";
            button_gestion_incapacidades.className = "btn btn-outline-primary";
            //button_gestion_incapacidades.style.borderRadius = "5px";
            button_gestion_incapacidades.id = "btnGestionIncapacidades";
            button_gestion_incapacidades.onclick = btn_gestion_incapacidades;

            var button_gestion_licencias = document.createElement('button');
            button_gestion_licencias.appendChild(document.createTextNode("Gestionar Licencias"));
            button_gestion_licencias.type = "button";
            button_gestion_licencias.name = "btnGestionLicencias";
            button_gestion_licencias.className = "btn btn-outline-primary";
            //button_gestion_timepo_acomulado.style.borderRadius = "5px";
            button_gestion_licencias.id = "btnGestionLicencias";
            button_gestion_licencias.onclick = btn_gestion_licencias;

            var button_gestion_justificaciones_marca = document.createElement('button');
            button_gestion_justificaciones_marca.appendChild(document.createTextNode("Gestionar Justificaciones de Marca"));
            button_gestion_justificaciones_marca.type = "button";
            button_gestion_justificaciones_marca.name = "btnGestionJustificacionesMarca";
            button_gestion_justificaciones_marca.className = "btn btn-outline-primary";
            //button_gestion_incapacidades.style.borderRadius = "5px";
            button_gestion_justificaciones_marca.id = "btnGestionJustificacionesMarca";
            button_gestion_justificaciones_marca.onclick = btn_gestion_justificaciones_marcas;

            var button_gestion_cargar_adicionales = document.createElement('button');
            button_gestion_cargar_adicionales.appendChild(document.createTextNode("Cargar Adicionales"));
            button_gestion_cargar_adicionales.type = "button";
            button_gestion_cargar_adicionales.name = "btnCargarAdicionlaes";
            button_gestion_cargar_adicionales.className = "btn btn-outline-primary";
            //button_gestion_incapacidades.style.borderRadius = "5px";
            button_gestion_cargar_adicionales.id = "btnCargarAdicionlaes";
            button_gestion_cargar_adicionales.onclick = btn_cargar_adicionales;

            var button_gestion_cargar_ajustes_pago = document.createElement('button');
            button_gestion_cargar_ajustes_pago.appendChild(document.createTextNode("Cargar Ajustes de Pago"));
            button_gestion_cargar_ajustes_pago.type = "button";
            button_gestion_cargar_ajustes_pago.name = "btnCargarAjustesPago";
            button_gestion_cargar_ajustes_pago.className = "btn btn-outline-primary";
            //button_gestion_incapacidades.style.borderRadius = "5px";
            button_gestion_cargar_ajustes_pago.id = "btnCargarAdicionlaes";
            button_gestion_cargar_ajustes_pago.onclick = btn_cargar_ajustes_pago;

            contenedor.appendChild(button_gestion_vacaciones);
            if(result['aceptaVacaciones']){
                contenedor.appendChild(button_gestion_vacaciones_colaboradores);
            }
            contenedor.appendChild(button_gestion_timepo_acomulado);
           // contenedor.appendChild(button_gestion_incapacidades);
           contenedor.appendChild(button_gestion_licencias);
            if(result['justifica']){
                contenedor.appendChild(button_gestion_justificaciones_marca);
            }
            if(result['adicionales']){
                contenedor.appendChild(button_gestion_cargar_adicionales);
            }
            if(result['ajustes']){
                contenedor.appendChild(button_gestion_cargar_ajustes_pago);
            }
        });
    },

});
function btn_gestion_vacacioines() {
    try {
        window.location.assign(window.location.href+'/uia_portal_gestion_vacaciones');
    } catch (err) {
        alert(err);
    }
}
function btn_gestion_vacaciones_colaboradores(){
    try {
        window.location.assign(window.location.href+'/uia_portal_gestion_vacacione_aprobar_jefatura');
    } catch (err) {
        alert(err);
    }
}
function btn_gestion_incapacidades() {
    try {
        window.location.assign(window.location.href+'/uia_portal_gestion_incapacidades');
    } catch (err) {
        alert(err);
    }
}

function btn_gestion_licencias() {
    try {
        window.location.assign(window.location.href+'/uia_portal_gestion_licencias');
    } catch (err) {
        alert(err);
    }
}

function btn_gestion_tiempo_acumulado() {
    try {
        window.location.assign(window.location.href+'/uia_portal_gestion_tiempo_acumulado');
    } catch (err) {
        alert(err);
    }
}
function btn_gestion_justificaciones_marcas() {
    try {
        window.location.assign(window.location.href+'/uia_portal_gestion_justificaciones_marca');
    } catch (err) {
        alert(err);
    }
}
function btn_cargar_adicionales() {
    try {
        window.location.assign(window.location.href+'/uia_portal_cargar_adicionales');
    } catch (err) {
        alert(err);
    }
}
function btn_cargar_ajustes_pago() {
    try {
        window.location.assign(window.location.href+'/uia_portal_cargar_ajustes_pago');
    } catch (err) {
        alert(err);
    }
}

publicWidget.registry.UIAPortalVacaciones = publicWidget.Widget.extend({
    selector: '.uia_portal_administrativo_gestion_vacaciones',
    events: {
        'click #uia_portal_administrativo_vacaciones_informacion': 'openvacacionesInfo',
        'click #uia_portal_administrativo_vacaciones_historial': 'openvacacionesHistorial',
        'click #uia_portal_administrativo_vacaciones_solicitud': 'openvacacionesSolicitud',
    },

    start: function () {
        this.openvacacionesInfo();
    },
    openvacacionesInfo: function() {
        try {
            ajax.jsonRpc('/get_vacaciones_info', 'call', {}).then(function (result){
                document.getElementById('uia_portal_menu_administrativo_vacaciones_container').innerHTML = "";
                document.getElementById('uia_portal_menu_administrativo_vacaciones_container').style.overflowY= "";
                document.getElementById('uia_portal_menu_administrativo_vacaciones_container').style.height= "";
                document.querySelector('#notificaciones_container').innerHTML = "";
                var contenedor = document.querySelector('#uia_portal_menu_administrativo_vacaciones_container');
    
                var table = document.createElement('table');
                table.className = 'table caption-top';
    
                var thead = document.createElement('thead');
    
                var tr = document.createElement('tr');
    
                var th1 = document.createElement('th');
                th1.appendChild(document.createTextNode('Total'))
                th1.scope = 'col'
    
                var th2 = document.createElement('th');
                th2.appendChild(document.createTextNode('Tomadas'))
                th2.scope = 'col'
    
                var th3 = document.createElement('th');
                th3.appendChild(document.createTextNode('Restantes'))
                th3.scope = 'col'
    
                tr.appendChild(th1);
                tr.appendChild(th2);
                tr.appendChild(th3);
                thead.appendChild(tr);
    
                var tbody = document.createElement('tbody');
    
                var td_total = document.createElement('td');
                td_total.appendChild(document.createTextNode(result['total']));
    
                var td_tomadas = document.createElement('td');
                td_tomadas.appendChild(document.createTextNode(result['tomadas']));
    
    
                var td_restantes = document.createElement('td');
                td_restantes.appendChild(document.createTextNode(result['restantes']));
                cant_dias = result['restantes'];
    
    
                tbody.appendChild(td_total);
    
                tbody.appendChild(td_tomadas);
    
                tbody.appendChild(td_restantes);
    
                table.appendChild(thead);
                table.appendChild(tbody);
                contenedor.appendChild(table);
    
            });

        } catch (err) {
        }
    },
    
    openvacacionesHistorial: function() {
        try {
            ajax.jsonRpc('/get_vacaciones_historial', 'call', {}).then(function (result){
                document.getElementById('uia_portal_menu_administrativo_vacaciones_container').innerHTML = "";
                document.querySelector('#notificaciones_container').innerHTML = "";
                var contenedor = document.querySelector('#uia_portal_menu_administrativo_vacaciones_container');          
                contenedor.style.overflowY = 'scroll';
                contenedor.style.height = '300px';
    
                var table = document.createElement('table');
                table.className = 'table';
    
                var thead = document.createElement('thead');
    
                var tr = document.createElement('tr');
    
                var th1 = document.createElement('th');
                th1.appendChild(document.createTextNode('Desde'))
                th1.scope = 'col'
    
                var th2 = document.createElement('th');
                th2.appendChild(document.createTextNode('Hasta'))
                th2.scope = 'col'
    
                var th3 = document.createElement('th');
                th3.appendChild(document.createTextNode('Dias'))
                th3.scope = 'col'
    
                var th4 = document.createElement('th');
                th4.appendChild(document.createTextNode('Estado Jefatura'))
                th4.scope = 'col'

                var th5 = document.createElement('th');
                th5.appendChild(document.createTextNode('Estado RH'))
                th5.scope = 'col'
    
                tr.appendChild(th1);
                tr.appendChild(th2);
                tr.appendChild(th3);
                tr.appendChild(th4);
                tr.appendChild(th5);
                thead.appendChild(tr);
    
                var tbody = document.createElement('tbody');
    
                for(let x in result){
                    var tr = document.createElement('tr');
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['fechaInicioVacaciones']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);
                    
    
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['fechaFinVacaciones']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);
    
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['diasVacaciones']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);
    
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['estadoJefatura']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);

                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['estadoRH']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);     
                }
    
                table.appendChild(thead);
                table.appendChild(tbody);
                contenedor.appendChild(table);
                
            });
        } catch (err) {
        }
    },
    
    openvacacionesSolicitud: function() {
        try {
            ajax.jsonRpc('/get_vacaciones_info', 'call', {}).then(function (result){

               if(result['restantes'] > 0 ){
                document.getElementById('uia_portal_menu_administrativo_vacaciones_container').innerHTML = "";
                document.getElementById('uia_portal_menu_administrativo_vacaciones_container').style.overflowY= "";
                document.getElementById('uia_portal_menu_administrativo_vacaciones_container').style.height= "";
                var contenedor = document.querySelector('#uia_portal_menu_administrativo_vacaciones_container');
    
                var form_row_g_3 = document.createElement('form');
                form_row_g_3.className = 'row g-3';
    
                var div_col_md_6_desde = document.createElement('div');
                div_col_md_6_desde.className = 'col-md-6';
    
                var div_col_md_6_hasta = document.createElement('div');
                div_col_md_6_hasta.className = 'col-md-6';

                var div_form_group = document.createElement('div');
                div_form_group.className = 'form-group';
                
                var div_form_check = document.createElement('div');
                div_form_check.className = 'form-check';
                div_form_check.id = 'contenedorDiaMedio'
    
                var label_form_label_desde = document.createElement('label');
                label_form_label_desde.className = 'form-label';
                label_form_label_desde.appendChild(document.createTextNode('Desde'));
    
                var input_date_desde = document.createElement('input');
                input_date_desde.className = 'form-control';
                input_date_desde.id = 'dt_desde';
                input_date_desde.type = 'date';
                input_date_desde.onchange = onChangeFechaDesdeVacaciones;
    
                var label_form_label_hasta = document.createElement('label');
                label_form_label_hasta.className = 'form-label';
                label_form_label_hasta.appendChild(document.createTextNode('Hasta'));

                var table_vacaciones = document.createElement('table');
                table_vacaciones.className = 'table'
                table_vacaciones.id = 'tbl_vacaciones'

                var table_thead_vacaciones = document.createElement('thead');

                var table_tbody_vacaciones = document.createElement('tbody');
                table_tbody_vacaciones.id ='tbl_vacaciones_data'

                var table_tr_vacaciones = document.createElement('tr');
                
                var tabla = ['Desde','Hasta','Medio día','Jornada']

                tabla.forEach((item,idex,arr)=>{

                    var th = document.createElement('th');
                    th.appendChild(document.createTextNode(item));
                    table_tr_vacaciones.appendChild(th);
                    
                });
                table_thead_vacaciones.appendChild(table_tr_vacaciones)
                table_vacaciones.appendChild(table_thead_vacaciones)
                table_vacaciones.appendChild(table_tbody_vacaciones)
                

                var input_checkbox_medio = document.createElement('input');
                input_checkbox_medio.type = 'checkbox';
                input_checkbox_medio.className = 'form-check-input';
                input_checkbox_medio.id = 'chkMedioDia';
                input_checkbox_medio.addEventListener('change', function() {
                    try {
                        if (this.checked) {
                            var desde = new Date(document.getElementById("dt_desde").value);
                            var hasta = new Date(document.getElementById("dt_hasta").value);
                            if(isNaN(desde)){
                                if(isNaN(hasta)){
                                    document.getElementById("dt_desde").style.borderColor = "red";
                                    document.getElementById("dt_hasta").style.borderColor = "red";
                                }else{
                                    document.getElementById("dt_desde").style.borderColor = "red";
                                }
                            }else if(isNaN(hasta)){
                                if(isNaN(desde)){
                                    document.getElementById("dt_desde").style.borderColor = "red";
                                    document.getElementById("dt_hasta").style.borderColor = "red";
                                }else{
                                    document.getElementById("dt_hasta").style.borderColor = "red";
                                }
                            }else{
                                document.getElementById("dt_desde").style.borderColor = "white";
                                document.getElementById("dt_hasta").style.borderColor = "white";
                                var select_form_jornada = document.createElement('select')
                                select_form_jornada.className = 'form-control';
                                select_form_jornada.id = 'selectJornada';
                
                                var listJornadaText = ['Inicio de Jornada','Fin de Jornada']
                                var listJornadaValues = ['Inicio de Jornada','Fin de Jornada']
                                for (var i = 0; i<=1; i++){
                                    var opt = document.createElement('option');
                                    opt.value = listJornadaValues[i];
                                    opt.innerHTML = listJornadaText[i];
                                    select_form_jornada.appendChild(opt);
                                }
                                var contenedor = document.querySelector('#contenedorDiaMedio');
                                var select_form_dia_medio = document.createElement('select')
                                select_form_dia_medio.className = 'form-control';
                                select_form_dia_medio.id = 'diaMedioSelect';
                                
                                for (var i = new Date(desde.setDate(desde.getDate())); i<= hasta;  i.setDate(i.getDate() + 1)){
                                    var dia = (i.getFullYear())+"-"+(i.getMonth()+1)+"-"+(i.getDate()+1)
                                    var opt = document.createElement('option');
                                    opt.value = dia;
                                    opt.innerHTML = dia;
                                    select_form_dia_medio.appendChild(opt);
                                }
                                contenedor.appendChild(select_form_dia_medio);
                                contenedor.appendChild(select_form_jornada);
                            }
                        } else {
                            var selecDiaMedio = document.getElementById("diaMedioSelect");
                            if(selecDiaMedio != null){
                                document.getElementById("dt_desde").style.borderColor = "#FFFFFF";
                                document.getElementById("dt_hasta").style.borderColor = "#FFFFFF";
                                document.getElementById("selectJornada").remove();
                                selecDiaMedio.remove();
                            }else{

                            }
                        }
                    } catch (error) {
                        alert(error);
                    }
                  });


                var label_form_label_medio_dia = document.createElement('label');
                label_form_label_medio_dia.appendChild(document.createTextNode('Medio día'));
                label_form_label_medio_dia.className = 'form-check-label';

    
                var input_date_hasta = document.createElement('input');
                input_date_hasta.className = 'form-control';
                input_date_hasta.id = 'dt_hasta';
                input_date_hasta.type = 'date';
    
                div_col_md_6_desde.appendChild(label_form_label_desde);
                div_col_md_6_desde.appendChild(input_date_desde);
    
                div_col_md_6_hasta.appendChild(label_form_label_hasta);
                div_col_md_6_hasta.appendChild(input_date_hasta);

                div_form_check.appendChild(input_checkbox_medio);
                div_form_check.appendChild(label_form_label_medio_dia);

                div_form_group.appendChild(div_form_check);
    
                form_row_g_3.appendChild(div_col_md_6_desde);
                form_row_g_3.appendChild(div_col_md_6_hasta);
       
                var div_input_group = document.createElement('div');
                div_input_group.className = 'inout-group';
    
                var label_form_label_razon = document.createElement('label');
                label_form_label_razon.className = 'form-label';
                label_form_label_razon.appendChild(document.createTextNode('Razón'));
    
                var textarea_form_control = document.createElement('textarea');
                textarea_form_control.id = 'txt_razon';
                textarea_form_control.className = 'form-control';
    
                div_input_group.appendChild(label_form_label_razon);
                div_input_group.appendChild(textarea_form_control);


                var btn_agregar = document.createElement('button');
                btn_agregar.className = 'btn btn-primary';
                btn_agregar.style.marginTop = '5px';
                btn_agregar.id = 'btn_agregar_vacaciones';
                btn_agregar.appendChild(document.createTextNode('Agregar'));
                btn_agregar.onclick = btnSetAgregarVacaciones;
    
                var btn_solicitar = document.createElement('button');
                btn_solicitar.className = 'btn btn-primary';
                btn_solicitar.style.marginTop = '5px';
                btn_solicitar.id = 'btn_solicitar_vacaciones';
                btn_solicitar.appendChild(document.createTextNode('Solicitar'));
                btn_solicitar.disabled = true; 
                btn_solicitar.onclick = btnSetSolicitarVacaciones;
    
                div_input_group.appendChild(btn_solicitar);
    
                contenedor.appendChild(form_row_g_3);
                contenedor.appendChild(div_form_group);
                contenedor.appendChild(btn_agregar);
                contenedor.appendChild(table_vacaciones);
                contenedor.appendChild(div_input_group);

            }else{
                var alertPlaceholder = document.querySelector('#uia_portal_menu_administrativo_vacaciones_container');
                alertPlaceholder.innerHTML = "";
                var div_alert = document.createElement('div');
                div_alert.className = "alert alert-danger";
                div_alert.style.borderRadius = "5px";
                div_alert.style.marginTop = "5px";
                div_alert.appendChild(document.createTextNode("Vacaciones insufucientes"));
                div_alert.style.fontSize = "15px";
                div_alert.style.fontWeight = "900";
                alertPlaceholder.appendChild(div_alert);
            }
            });
        } catch (err) {
            alert(err+"111");
        }
    },
});

function onChangeFechaDesdeVacaciones(result){
    var alertPlaceholder = document.querySelector('#notificaciones_container');
    alertPlaceholder.innerHTML = "";
    try{
        var dt_desde = document.getElementById('dt_desde'); 

        if(dt_desde != null){
            var fechaMinima = new Date();
            fechaMinima.setDate(fechaMinima.getDate());
            var fechaActual = new Date(dt_desde.value)

            if(fechaActual.getTime() > fechaMinima.getTime()){            

            }else{
                showNotificacionAlertVacaciones("La fecha inicial tiene que tener mínimo 2 días de antelación para poder hacer la solicitud.","alert alert-warning")
            }
        }
    

    }catch(err){
        alert(err)
    }
}
function btnSetSolicitarVacaciones() {

    try {
        
        document.getElementById('btn_solicitar_vacaciones').disabled = true; 

        var tbl = document.getElementById('tbl_vacaciones');
        var valsJS = []
        for (var i = 1; i < tbl.rows.length; i++){

            var celda = tbl.rows.item(i).cells;


            var valsDic = {
                'dt_desde': celda.item(0).innerHTML,
                'dt_hasta': celda.item(1).innerHTML,            
            }

            if(celda.item(2) != null){
                var valsDic = {
                    'dt_desde': celda.item(0).innerHTML,
                    'dt_hasta': celda.item(1).innerHTML,
                    'fechaMedioDia': celda.item(2).innerHTML ,
                    'tipoMedioDia': celda.item(3).innerHTML,
                }
            }
            
            valsJS.push(valsDic)
        }
        if(2>1){
            ajax.jsonRpc('/set_vacaciones_solicitud', 'call', {
                valsJS:  valsJS
            }).then(function (result){
                var alertPlaceholder = document.querySelector('#uia_portal_menu_administrativo_vacaciones_container');
                alertPlaceholder.innerHTML = "";
                var div_alert = document.createElement('div');
                div_alert.className = "alert alert-warning";
                div_alert.style.borderRadius = "5px";
                div_alert.style.marginTop = "5px";
                div_alert.appendChild(document.createTextNode(result));
                div_alert.style.fontSize = "15px";
                div_alert.style.fontWeight = "900";
                alertPlaceholder.appendChild(div_alert);
             });
        }else{
            document.getElementById('btn_solicitar_vacaciones').disabled = false; 
        }

    } catch (err) {
        alert(err);
    }
}
function btnSetAgregarVacaciones(){
    try {
        var valsJS = []
        var tbody = document.getElementById('tbl_vacaciones_data');
        var resultVerificacion = verificarSolicitudVacaciones();
        if(resultVerificacion.verificacion && verificarFechasVacaciones()){
            var tbl = document.getElementById('tbl_vacaciones');

            for (var i = 1; i < tbl.rows.length; i++){

                var celda = tbl.rows.item(i).cells;


                var valsDic = {
                    'dt_desde': celda.item(0).innerHTML,
                    'dt_hasta': celda.item(1).innerHTML,            
                }

                if(celda.item(2) != null){
                    var valsDic = {
                        'dt_desde': celda.item(0).innerHTML,
                        'dt_hasta': celda.item(1).innerHTML,
                        'fechaMedioDia': celda.item(2).innerHTML ,
                        'tipoMedioDia': celda.item(3).innerHTML,
                    }
                }
                
                valsJS.push(valsDic)
            }

            ajax.jsonRpc('/verificacion_vacaciones_solicitud', 'call', {
                valsJS:  valsJS
            }).then(function (result){

                if(result['result']){
                    showNotificacionAlertVacaciones(result['msg'],"alert alert-warning")
                }else{
                    document.getElementById('btn_solicitar_vacaciones').disabled = false; 
                    var newRow = tbl.insertRow(-1);

                    var dataCell = newRow.insertCell(0);
                    dataCell.textContent = resultVerificacion['dt_desde'];

                    dataCell = newRow.insertCell(1);
                    dataCell.textContent = resultVerificacion['dt_hasta'];

                    if(document.getElementById('chkMedioDia').checked){

                        dataCell = newRow.insertCell(2);
                        dataCell.textContent = resultVerificacion['fechaMedioDia'];

                        dataCell = newRow.insertCell(3);
                        dataCell.textContent = resultVerificacion['tipoMedioDia'];
                    } 

                    document.getElementById('dt_desde').value = ''; 
                    document.getElementById('dt_hasta').value = ''; 
                    if(document.getElementById('chkMedioDia').checked){
                        var selecDiaMedio = document.getElementById("diaMedioSelect");
                        if(selecDiaMedio != null){
                            document.getElementById("dt_desde").style.borderColor = "#FFFFFF";
                            document.getElementById("dt_hasta").style.borderColor = "#FFFFFF";
                            document.getElementById("selectJornada").remove();
                            selecDiaMedio.remove();
                            document.getElementById('chkMedioDia').checked = false
                        }else{

                        }
                    }
                }
                
             });

        }

        

    } catch (err) {
        alert(err);
    }
}
function verificarSolicitudVacaciones() {

    var alertPlaceholder = document.querySelector('#notificaciones_container');
    alertPlaceholder.innerHTML = "";

    var valsJS = {
        'verificacion': true
    };

    var dt_desde = document.getElementById('dt_desde'); 
    var dt_hasta = document.getElementById('dt_hasta'); 
    var chkMedioDia = document.getElementById('chkMedioDia');
    var diaMedioSelect = document.getElementById('diaMedioSelect'); 
    var selectJornada = document.getElementById('selectJornada'); 
    var txt_razon = document.getElementById('txt_razon');

    if(dt_desde != null){
        if(dt_desde != ""){
            valsJS["dt_desde"] = dt_desde.value;
        }else{
            showNotificacionAlertVacaciones("Tiene que elegir una fecha válida en el campo Desde","alert alert-warning")
            valsJS["verificacion"] = false;
        }
    }

    if(dt_hasta != null){
        if(dt_hasta != ""){
            valsJS["dt_hasta"] = dt_hasta.value;
        }else{
            showNotificacionAlertVacaciones("Tiene que elegir una fecha válida en el campo Hasta","alert alert-warning")
            valsJS["verificacion"] = false;
        }
    }

    if(dt_desde != null){
        var fechaMinima = new Date();
        fechaMinima.setDate(fechaMinima.getDate());
        var fechaActual = new Date(dt_desde.value)

        if(fechaActual.getTime() > fechaMinima.getTime()){            

        }else{
            showNotificacionAlertVacaciones("La fecha inicial tiene que tener mínimo 2 días de antelación para poder hacer la solicitud.","alert alert-warning")
            valsJS["verificacion"] = false;
        }
    }

    if(dt_desde != null && dt_hasta != null){

        if(dt_desde.value > dt_hasta.value){
            showNotificacionAlertVacaciones("El campo Desde no puede ser mayor la campo Hasta","alert alert-warning")
            valsJS["verificacion"] = false;
        }
    }

    if(txt_razon != null){
        if(txt_razon != ""){
            valsJS["txt_razon"] = txt_razon.value;
        }else{
            showNotificacionAlertVacaciones("Tiene que escribir algun txto en el campo Razón","alert alert-warning")
            valsJS["verificacion"] = false;
        }
    }

    if(chkMedioDia.checked){
        valsJS["fechaMedioDia"] = diaMedioSelect.value
        valsJS["tipoMedioDia"] = selectJornada.value
    }

    return valsJS
}
function verificarFechasVacaciones(){

    var tbl = document.getElementById('tbl_vacaciones');
    var valsJS = []
    for (var i = 1; i < tbl.rows.length; i++){
        var celda = tbl.rows.item(i).cells;


        var valsDic = {
            'dt_desde': celda.item(0).innerHTML,
            'dt_hasta': celda.item(1).innerHTML,            
        }

        if(celda.item(2) != null){
            var valsDic = {
                'dt_desde': celda.item(0).innerHTML,
                'dt_hasta': celda.item(1).innerHTML,
                'fechaMedioDia': celda.item(2).innerHTML ,
                'tipoMedioDia': celda.item(3).innerHTML,
            }
        }
        
        valsJS.push(valsDic)
    }

    var dt_desde = document.getElementById('dt_desde'); 
    var dt_hasta = document.getElementById('dt_hasta'); 
    var verificacion = true
    for (var i = 0; i < valsJS.length; i++){
        var desdeTabla = new Date(valsJS[i]['dt_desde']);
        var hastaTabla = new Date(valsJS[i]['dt_hasta']);
        var desdedt = new Date(dt_desde.value);
        var hastadt = new Date(dt_hasta.value);

        if(hastadt.getTime() > desdeTabla.getTime() && hastadt.getTime() < hastaTabla.getTime()){
            verificacion = false
        }
        if(desdedt.getTime() > desdeTabla.getTime() && desdedt.getTime() < hastaTabla.getTime()){
            verificacion = false
        }

        if(hastadt.getTime() == desdeTabla.getTime() || hastadt.getTime() == hastaTabla.getTime()){
            verificacion = false
        }
        if(desdedt.getTime() == desdeTabla.getTime() || desdedt.getTime() == hastaTabla.getTime()){
            verificacion = false
        }
                
    }
    if(verificacion == false){
        showNotificacionAlertVacaciones("La fecha de solicitud no pueden chocar.","alert alert-warning")
    }
    return verificacion;
}

function showNotificacionAlertVacaciones(notificacion,tipo){
    var alertPlaceholder = document.querySelector('#notificaciones_container');
    var div_alert = document.createElement('div');
    var p_text = document.createElement('p');
    p_text.innerHTML = notificacion;
    div_alert.className = tipo;
    div_alert.id = 'alert_docente_no_encontrado'
    div_alert.style.borderRadius = "5px";
    div_alert.style.marginTop = "5px";
    div_alert.appendChild(p_text);
    div_alert.style.fontSize = "15px";
    div_alert.style.fontWeight = "900";
    alertPlaceholder.appendChild(div_alert);
}

publicWidget.registry.UIAPortalVacacionesColaboradores = publicWidget.Widget.extend({
    selector: '.uia_portal_administrativo_gestion_vacaciones_aprobar_jefatura',
    events: {
        'click #aceptar_vacaciones': 'aceptarVacaciones',
        'click #rechazar_vacaciones': 'rechazarVacaciones',
    },

    start: function () {
    },

    aceptarVacaciones: function(objButton) {
        try {
           var vals ={
                'id_vacaciones': objButton.currentTarget.value,
                'accion': "Aceptado",
            };
            ajax.jsonRpc('/set_proceso_accion_vacaciones_jefatura_inmediata', 'call', {
                valsJS: vals,
            }).then(function (result){

                if(result['result']){
                    document.getElementById(objButton.currentTarget.value).parentNode.removeChild(document.getElementById(objButton.currentTarget.value));
                }
            });


        } catch (err) {
            alert(err);
        }
    },

    rechazarVacaciones: function(objButton) {
        try {
            var vals ={
                'id_vacaciones': objButton.currentTarget.value,
                'accion': "Rechazado",
            };
            ajax.jsonRpc('/set_proceso_accion_vacaciones_jefatura_inmediata', 'call', {
                valsJS: vals,
            }).then(function (result){

                if(result['result']){
                    document.getElementById(objButton.currentTarget.value).parentNode.removeChild(document.getElementById(objButton.currentTarget.value));
                }
            });
        } catch (err) {
        }
    },
});

publicWidget.registry.AceptacionVacacionesJefaturaInmediata = publicWidget.Widget.extend({
    selector: '.portal_administrativo_gestion_vacaciones_accion_jefatura_inmediata_form',
    events: {
        'click #btn_aceptar_vacaciones': 'btnAceptarVacaciones',
        'click #btn_rechazar_vacaciones': 'btnRechazarVacaciones',
    },

    start: function () {
    },

    btnAceptarVacaciones: function(){
        var vals ={
            'id_vacaciones': document.getElementById('id_vacaciones').innerHTML,
            'accion': "Aceptado",
        };
        ajax.jsonRpc('/set_proceso_accion_vacaciones_jefatura_inmediata', 'call', {
            valsJS: vals,
        }).then(function (result){

            if(result['result']){
                var contenedor = document.querySelector('#portal_administrativo_gestion_vacaciones_accion_jefatura_inmediata_container');

                var div_alert_alert_primary = document.createElement('div');
                div_alert_alert_primary.className = 'alert alert-primary';
                div_alert_alert_primary.appendChild(document.createTextNode('¡Información de solicitud enviada, muchas gracias!!!'));

                contenedor.innerHTML = '';
                document.querySelector('#portal_administrativo_gestion_vacaciones_accion_jefatura_inmediata_container').innerHTML = "";
                document.querySelector('#notificaciones_container').innerHTML = "";
                contenedor.appendChild(div_alert_alert_primary);
            }
        });
    },
    btnRechazarVacaciones: function(){
        var vals ={
            'id_vacaciones': document.getElementById('id_vacaciones').innerHTML,
            'accion': "Rechazado",
        };
        ajax.jsonRpc('/set_proceso_accion_vacaciones_jefatura_inmediata', 'call', {
            valsJS: vals,
        }).then(function (result){

            if(result['result']){
                var contenedor = document.querySelector('#portal_administrativo_gestion_vacaciones_accion_jefatura_inmediata_container');

                var div_alert_alert_primary = document.createElement('div');
                div_alert_alert_primary.className = 'alert alert-primary';
                div_alert_alert_primary.appendChild(document.createTextNode('¡Información de solicitud enviada, muchas gracias!!!'));

                contenedor.innerHTML = '';
                document.querySelector('#portal_administrativo_gestion_vacaciones_accion_jefatura_inmediata_container').innerHTML = "";
                document.querySelector('#notificaciones_container').innerHTML = "";
                contenedor.appendChild(div_alert_alert_primary);
            }
        });
    },

});

publicWidget.registry.AceptacionVacacionesJefaturaRH = publicWidget.Widget.extend({
    selector: '.portal_administrativo_gestion_vacaciones_accion_jefatura_RH_form',
    events: {
        'click #btn_aceptar_vacaciones': 'btnAceptarVacaciones',
        'click #btn_rechazar_vacaciones': 'btnRechazarVacaciones',
    },

    start: function () {
    },

    btnAceptarVacaciones: function(){
        var vals ={
            'id_vacaciones': document.getElementById('id_vacaciones').innerHTML,
            'accion': "Aceptado",
        };
        ajax.jsonRpc('/set_proceso_accion_vacaciones_jefatura_RH', 'call', {
            valsJS: vals,
        }).then(function (result){

            if(result['result']){
                var contenedor = document.querySelector('#portal_administrativo_gestion_vacaciones_accion_jefatura_RH_container');

                var div_alert_alert_primary = document.createElement('div');
                div_alert_alert_primary.className = 'alert alert-primary';
                div_alert_alert_primary.appendChild(document.createTextNode('¡Información de solicitud enviada, muchas gracias!!!'));
                contenedor.innerHTML = '';
                contenedor.appendChild(div_alert_alert_primary);

                if(result['reporte']){
                    var URLactual = window.location.hostname
                    window.open('/create_report_accion_vacaciones?vacacionesId='+result['vacacionesId'], "_blank");
                }

            }
        });
    },
    btnRechazarVacaciones: function(){
        var vals ={
            'id_vacaciones': document.getElementById('id_vacaciones').innerHTML,
            'accion': "Rechazado",
        };
        ajax.jsonRpc('/set_proceso_accion_licencia_jefatura_RH', 'call', {
            valsJS: vals,
        }).then(function (result){

            if(result['result']){
                var contenedor = document.querySelector('#portal_administrativo_gestion_licencias_accion_jefatura_RH_container');

                var div_alert_alert_primary = document.createElement('div');
                div_alert_alert_primary.className = 'alert alert-primary';
                div_alert_alert_primary.appendChild(document.createTextNode('¡Información de solicitud enviada, muchas gracias!!!'));
                contenedor.innerHTML = '';
                contenedor.appendChild(div_alert_alert_primary);
            }
        });
    },

});

publicWidget.registry.UIAPortalAprobacionVacciones = publicWidget.Widget.extend({
    selector: '.uia_porta_aprobacion_vacaciones',
   /* events: {
        'click #uia_portal_administrativo_vacaciones_informacion': 'openvacacionesInfo',
        'click #uia_portal_administrativo_vacaciones_historial': 'openvacacionesHistorial',
    },*/

    start: function () {
        this.createAprobacion();
    },
    createAprobacion: function() {
        try {
            var idVacaciones  =  document.getElementById("uia_portal_vacaciones_aprobacion_id").innerHTML;
            var contenedor = document.querySelector('#uia_portal_aprobacion_vacaciones');

            if(idVacaciones == 'SinAutorizacion'){
                contenedor.innerHTML = "";
                var div_alert = document.createElement('div');
                div_alert.className = "alert alert-danger";
                div_alert.style.borderRadius = "5px";
                div_alert.style.marginTop = "5px";
                div_alert.appendChild(document.createTextNode('Ustede no posee los privilegios nesearios para realizar esta accion'));
                div_alert.style.fontSize = "15px";
                div_alert.style.fontWeight = "900";
                contenedor.appendChild(div_alert);
            }else{
                ajax.jsonRpc('/get_vacaciones_aprobacion_info', 'call', {
                    idVacaciones: idVacaciones,
                }).then(function (result){

                    if(result['aplicado'] == false){
                        contenedor.innerHTML = "";

                        var table = document.createElement('table');
                        table.className = 'table caption-top';
            
                        var thead = document.createElement('thead');
            
                        var tr = document.createElement('tr');
            
                        var th1 = document.createElement('th');
                        th1.appendChild(document.createTextNode('Empleado'))
                        th1.scope = 'col'
            
                        var th2 = document.createElement('th');
                        th2.appendChild(document.createTextNode('Razon'))
                        th2.scope = 'col'
    
                        var th3 = document.createElement('th');
                        th3.appendChild(document.createTextNode('Fechas'))
                        th3.scope = 'col'
    
                        var th4 = document.createElement('th');
                        th4.appendChild(document.createTextNode('Dias'))
                        th4.scope = 'col'
    
                        var th5 = document.createElement('th');
                        th5.appendChild(document.createTextNode('Accion'))
                        th5.scope = 'col'
            
                        tr.appendChild(th1);
                        tr.appendChild(th2);
                        tr.appendChild(th3);
                        tr.appendChild(th4);
                        tr.appendChild(th5);
                        thead.appendChild(tr);
            
                        var tbody = document.createElement('tbody');
    
            
                        var td_empleado = document.createElement('td');
                        td_empleado.appendChild(document.createTextNode(result['empleado']));
    
            
                        var td_razon = document.createElement('td');
                        td_razon.appendChild(document.createTextNode(result['razon']));
    
                        var td_rango = document.createElement('td');
                        td_rango.appendChild(document.createTextNode(result['desde']+'  '+ result['hasta']));
            
            
                        var td_diasVacaciones = document.createElement('td');
                        td_diasVacaciones.appendChild(document.createTextNode(result['diasVacaciones']));
    
                        var td_accion = document.createElement('td');
                        
    
    
                        var button_aceptar_vacaciones = document.createElement('button');
                        button_aceptar_vacaciones.appendChild(document.createTextNode("Aceptar"));
                        button_aceptar_vacaciones.type = "button";
                        button_aceptar_vacaciones.name = "btnAceptarPago";
                        button_aceptar_vacaciones.className = "btn btn-success btn-sm";
                        button_aceptar_vacaciones.value = "aceptar";
                        button_aceptar_vacaciones.id = "btnAceptar";
                        button_aceptar_vacaciones.onclick = btn_aceptar_vacaciones;
    
                        var button_rechazar_vacaciones = document.createElement('button');
                        button_rechazar_vacaciones.appendChild(document.createTextNode("Rechazar"));
                        button_rechazar_vacaciones.type = "button";
                        button_rechazar_vacaciones.name = "btnRechazarPago";
                        button_rechazar_vacaciones.className = "btn btn-warning btn-sm";
                        button_rechazar_vacaciones.value = "rechazar";
                        button_rechazar_vacaciones.id = "btnRechazar";
                       // button_rechazar_vacaciones.onclick = btnRechazarPlanilla;
    
                        var div_btn_group = document.createElement('div');
                        div_btn_group.className = 'btn-group';
                        div_btn_group.ariaLabel = 'Basic mixed styles example';
    
                        div_btn_group.append(button_aceptar_vacaciones);
                        div_btn_group.append(button_rechazar_vacaciones);
    
                        td_accion.appendChild(div_btn_group);
            
            
                        tbody.appendChild(td_empleado);
            
                        tbody.appendChild(td_razon);
    
                        tbody.appendChild(td_rango);
            
                        tbody.appendChild(td_diasVacaciones);
    
                        tbody.appendChild(td_diasVacaciones);
    
                        tbody.appendChild(td_accion);
            
                        table.appendChild(thead);
                        table.appendChild(tbody);
                        contenedor.appendChild(table);
                    }else{
                        var alertPlaceholder = document.querySelector('#uia_portal_aprobacion_vacaciones');
                        alertPlaceholder.innerHTML = "";
                        var div_alert = document.createElement('div');
                        div_alert.className = "alert alert-success";
                        div_alert.style.borderRadius = "5px";
                        div_alert.style.marginTop = "5px";
                        div_alert.appendChild(document.createTextNode('Ya se realiso una accion sobre esta peticion de vacaciones'));
                        div_alert.style.fontSize = "15px";
                        div_alert.style.fontWeight = "900";
                        alertPlaceholder.appendChild(div_alert);
                    }
                });
            }

        } catch (err) {
        }
    },
});
function btn_aceptar_vacaciones(){
    try{
        var idVacaciones  =  document.getElementById("uia_portal_vacaciones_aprobacion_id").innerHTML;
        ajax.jsonRpc('/set_vacaciones_accion', 'call', {
            idVacaciones: idVacaciones,
            accion: true,
        }).then(function (result){
            
            var alertPlaceholder = document.querySelector('#uia_portal_aprobacion_vacaciones');
            alertPlaceholder.innerHTML = "";
            var div_alert = document.createElement('div');
            div_alert.className = "alert alert-success";
            div_alert.style.borderRadius = "5px";
            div_alert.style.marginTop = "5px";
            div_alert.appendChild(document.createTextNode('Accion realizada correctamente'));
            div_alert.style.fontSize = "15px";
            div_alert.style.fontWeight = "900";
            alertPlaceholder.appendChild(div_alert);

            if(result['pdfReport'] == true){
                var URLactual = window.location.hostname
                window.open('/create_report_accion_vacaciones?vacacionesId='+result['vacacionesId'], "_blank");
            }
        });
    }catch(err){
    }
}

publicWidget.registry.UIAPortalTiempoAcumulado= publicWidget.Widget.extend({
    selector: '.uia_portal_administrativo_gestion_tiempo_acumulado',
    events: {
        'click #uia_portal_administrativo_tiempo_acumulado_informacion':  'openTiempoAcumuladoInfo',
        'click #uia_portal_administrativo_tiempo_acumulado_historial':    'openTiempoAcumuladoHistorial',
        'click #uia_portal_administrativo_tiempo_acumulado_solicitud':    'openTiempoAcumuladoSolicitud',
    },

    start: function () {
        this.openTiempoAcumuladoInfo();
    },
    openTiempoAcumuladoInfo: function() {
        try {
            ajax.jsonRpc('/get_tiempo_acumulado_info', 'call', {}).then(function (result){
                document.getElementById('uia_portal_menu_administrativo_tiempo_acumulado_container').innerHTML = "";
                document.getElementById('uia_portal_menu_administrativo_tiempo_acumulado_container').style.overflowY= "";
                document.getElementById('uia_portal_menu_administrativo_tiempo_acumulado_container').style.height= "";
                var contenedor = document.querySelector('#uia_portal_menu_administrativo_tiempo_acumulado_container');
    
                var table = document.createElement('table');
                table.className = 'table caption-top';
    
                var thead = document.createElement('thead');
    
                var tr = document.createElement('tr');
    
                var th1 = document.createElement('th');
                th1.appendChild(document.createTextNode('Total'))
                th1.scope = 'col'
    
                var th2 = document.createElement('th');
                th2.appendChild(document.createTextNode('Tomadas'))
                th2.scope = 'col'
    
                var th3 = document.createElement('th');
                th3.appendChild(document.createTextNode('Restantes'))
                th3.scope = 'col'
    
                tr.appendChild(th1);
                tr.appendChild(th2);
                tr.appendChild(th3);
                thead.appendChild(tr);
    
                var tbody = document.createElement('tbody');
    
                var td_total = document.createElement('td');
                td_total.appendChild(document.createTextNode(result['total']/60));
    
                var td_tomadas = document.createElement('td');
                td_tomadas.appendChild(document.createTextNode(result['tomadas']/60));
    
    
                var td_restantes = document.createElement('td');
                td_restantes.appendChild(document.createTextNode(result['restantes']/60));
    
    
                tbody.appendChild(td_total);
    
                tbody.appendChild(td_tomadas);
    
                tbody.appendChild(td_restantes);
    
                table.appendChild(thead);
                table.appendChild(tbody);
                contenedor.appendChild(table);
    
            });

        } catch (err) {
        }
    },
    
    openTiempoAcumuladoHistorial: function() {
        try {
            ajax.jsonRpc('/get_tiempo_acumulado_historial', 'call', {}).then(function (result){
                document.getElementById('uia_portal_menu_administrativo_tiempo_acumulado_container').innerHTML = "";
                var contenedor = document.querySelector('#uia_portal_menu_administrativo_tiempo_acumulado_container');          
                contenedor.style.overflowY = 'scroll';
                contenedor.style.height = '300px';
    
                var table = document.createElement('table');
                table.className = 'table';
    
                var thead = document.createElement('thead');
    
                var tr = document.createElement('tr');
    
                var th1 = document.createElement('th');
                th1.appendChild(document.createTextNode('Fecha'))
                th1.scope = 'col'
    
                var th2 = document.createElement('th');
                th2.appendChild(document.createTextNode('Tiempo'))
                th2.scope = 'col'
    
                var th3 = document.createElement('th');
                th3.appendChild(document.createTextNode('Jornada'))
                th3.scope = 'col'
    
                var th4 = document.createElement('th');
                th4.appendChild(document.createTextNode('Estado'))
                th4.scope = 'col'
    
                tr.appendChild(th1);
                tr.appendChild(th2);
                tr.appendChild(th3);
                tr.appendChild(th4);
                thead.appendChild(tr);
    
                var tbody = document.createElement('tbody');
    
                for(let x in result){
                    var tr = document.createElement('tr');
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['fechaTiempoAcumulado']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);
                    
    
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['tiempoAcumuladoTomado']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);
    
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['inicioFinJornada']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);
    
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['estado']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);     
                }
    
                table.appendChild(thead);
                table.appendChild(tbody);
                contenedor.appendChild(table);
                
            });
        } catch (err) {
        }
    },
    
    openTiempoAcumuladoSolicitud: function() {
        try {
            ajax.jsonRpc('/get_vacaciones_info', 'call', {}).then(function (result){

               if(result['restantes'] > 0 ){
                document.getElementById('uia_portal_menu_administrativo_tiempo_acumulado_container').innerHTML = "";
                document.getElementById('uia_portal_menu_administrativo_tiempo_acumulado_container').style.overflowY= "";
                document.getElementById('uia_portal_menu_administrativo_tiempo_acumulado_container').style.height= "";
                var contenedor = document.querySelector('#uia_portal_menu_administrativo_tiempo_acumulado_container');


                var select_tipo_tiempo_acumulado = document.createElement('select');
                select_tipo_tiempo_acumulado.className = 'form-control';
                select_tipo_tiempo_acumulado.id = 'slt_tipo_tiempo_acumulado';
                select_tipo_tiempo_acumulado.style.marginTop = '10px';
                select_tipo_tiempo_acumulado.onchange = onchangeTipoTiempoCumulado;

                var tipoTiempoAcumulado = ['Tipos','Solo un dia','Rango de fechas']

                tipoTiempoAcumulado.forEach((item,idex,arr)=>{
                    var opt = document.createElement('option');
                    opt.value = item;
                    opt.innerHTML = item;
                    select_tipo_tiempo_acumulado.appendChild(opt);
                });
                
                contenedor.appendChild(select_tipo_tiempo_acumulado);
            }else{
                var alertPlaceholder = document.querySelector('#uia_portal_menu_administrativo_vacaciones_container');
                alertPlaceholder.innerHTML = "";
                var div_alert = document.createElement('div');
                div_alert.className = "alert alert-danger";
                div_alert.style.borderRadius = "5px";
                div_alert.style.marginTop = "5px";
                div_alert.appendChild(document.createTextNode("Vacaciones insufucientes"));
                div_alert.style.fontSize = "15px";
                div_alert.style.fontWeight = "900";
                alertPlaceholder.appendChild(div_alert);
            }

            });
        } catch (err) {
            alert(err);
        }
    },
});

function onchangeTipoTiempoCumulado(result){
    var contenedor = document.querySelector('#uia_portal_menu_administrativo_tiempo_acumulado_container_tipos');

    var tipoLicencia = document.getElementById('slt_tipo_tiempo_acumulado').value

    switch (tipoLicencia) {
        case "Solo un dia":
            contenedor.innerHTML = "";
            tipoTiempoCumuladoDia();
          break;
        case "Rango de fechas":
            contenedor.innerHTML = "";
            tipoTiempoCumuladoRango();

          break;
        default:
            contenedor.innerHTML = "";
          break;
      }
}
function tipoTiempoCumuladoRango(){
    var contenedor = document.querySelector('#uia_portal_menu_administrativo_tiempo_acumulado_container_tipos');

    var form = document.createElement('form');
    //form_row_g_3.className = 'row g-3';

    //#region Fechas
    var div_form_row_licencias_fechas= document.createElement('div');
    div_form_row_licencias_fechas.className = 'form-row';

    //#region Fecha Desde
    var div_form_group_col_md_6_tipo_licencia_dt_desde = document.createElement('div');
    div_form_group_col_md_6_tipo_licencia_dt_desde.className = 'form-group col-md-6';

    var label_form_label_desde = document.createElement('label');
    label_form_label_desde.className = 'form-label';
    label_form_label_desde.appendChild(document.createTextNode('Desde'));

    var input_date_desde = document.createElement('input');
    input_date_desde.className = 'form-control';
    input_date_desde.id = 'dt_desde';
    input_date_desde.type = 'date';

    div_form_group_col_md_6_tipo_licencia_dt_desde.appendChild(label_form_label_desde);
    div_form_group_col_md_6_tipo_licencia_dt_desde.appendChild(input_date_desde);

    div_form_row_licencias_fechas.appendChild(div_form_group_col_md_6_tipo_licencia_dt_desde);
    //#endregion

    //#region Fecha Hasta
    var div_form_group_col_md_6_tipo_licencia_dt_hasta = document.createElement('div');
    div_form_group_col_md_6_tipo_licencia_dt_hasta.className = 'form-group col-md-6';
                            
    var label_form_label_hasta = document.createElement('label');
    label_form_label_hasta.className = 'form-label';
    label_form_label_hasta.appendChild(document.createTextNode('Hasta'));

    var input_date_hasta = document.createElement('input');
    input_date_hasta.className = 'form-control';
    input_date_hasta.id = 'dt_hasta';
    input_date_hasta.type = 'date';

    div_form_group_col_md_6_tipo_licencia_dt_hasta.appendChild(label_form_label_hasta);
    div_form_group_col_md_6_tipo_licencia_dt_hasta.appendChild(input_date_hasta);

    div_form_row_licencias_fechas.appendChild(div_form_group_col_md_6_tipo_licencia_dt_hasta);
    //#endregion

    form.appendChild(div_form_row_licencias_fechas);
    //#endregion

    //#region Razon
    var div_form_group = document.createElement('div');
    div_form_group.className = 'form-group';

    var label_form_label_razon = document.createElement('label');
    label_form_label_razon.className = 'form-label';
    label_form_label_razon.appendChild(document.createTextNode('Razón'));

    var textarea_form_control = document.createElement('textarea');
    textarea_form_control.id = 'txt_razon';
    textarea_form_control.className = 'form-control';

    div_form_group.appendChild(label_form_label_razon);
    div_form_group.appendChild(textarea_form_control);

    form.appendChild(div_form_group);
    //#endregion
    
    //#region Botron Solicitar
    var btn_solicitar = document.createElement('button');
    btn_solicitar.type = "button";
    btn_solicitar.className = 'btn btn-primary';
    btn_solicitar.id = 'btn_solicitar_tiempo_acumulado';
    btn_solicitar.style.marginTop = '15px';
    btn_solicitar.style.marginBottom = '15px';
    btn_solicitar.appendChild(document.createTextNode('Solicitar'));
    btn_solicitar.onclick = btnSetSolicitarTiempoAcumulado;     

    form.appendChild(btn_solicitar);
    //#endregion
    
    contenedor.appendChild(form);

}
function tipoTiempoCumuladoDia(){
    var contenedor = document.querySelector('#uia_portal_menu_administrativo_tiempo_acumulado_container_tipos');
    var form_row_g_3 = document.createElement('form');
    form_row_g_3.className = 'row g-3';

    var div_col_md_6_desde = document.createElement('div');
    div_col_md_6_desde.className = 'col-md-6';

    var div_col_md_4_tiempo_acumulado = document.createElement('div');
    div_col_md_4_tiempo_acumulado.className = 'col-md-4';

    var label_form_label_desde = document.createElement('label');
    label_form_label_desde.className = 'form-label';
    label_form_label_desde.appendChild(document.createTextNode('Fecha'));

    var input_date_desde = document.createElement('input');
    input_date_desde.className = 'form-control';
    input_date_desde.id = 'dt_desde';
    input_date_desde.type = 'date';

    var label_form_label_hasta_acumulado = document.createElement('label');
    label_form_label_hasta_acumulado.className = 'form-label';
    label_form_label_hasta_acumulado.appendChild(document.createTextNode('Tiempo en h'));

    var select_form_tiempo_acumulado = document.createElement('select')
    select_form_tiempo_acumulado.className = 'form-control';
    select_form_tiempo_acumulado.id = 'selectTiempo';

    var label_form_label_jornada = document.createElement('label');
    label_form_label_jornada.className = 'form-label';
    label_form_label_jornada.appendChild(document.createTextNode('Jornada'));

    var select_form_jornada = document.createElement('select')
    select_form_jornada.className = 'form-control';
    select_form_jornada.id = 'selectJornada';

    var listvalues = ['30','60','90','120','150','180','210','240','270','300','330','360','390','420','450','480','510','540','570','600']
    var listText = ['0,5','1','1,5','2','2,5','3','3,5','4','4,5','5','5,5','6','6,5','7','7,5','8','8,5','9','9,5','10']
    var listJornadaText = ['Inicio de Jornada','Fin de Jornada']
    var listJornadaValues = ['inicioJornada','finJornada']
    for (var i = 0; i<=19; i++){
        var opt = document.createElement('option');
        opt.value = listvalues[i];
        opt.innerHTML = listText[i];
        select_form_tiempo_acumulado.appendChild(opt);
    }

    for (var i = 0; i<=1; i++){
        var opt = document.createElement('option');
        opt.value = listJornadaValues[i];
        opt.innerHTML = listJornadaText[i];
        select_form_jornada.appendChild(opt);
    }

    div_col_md_6_desde.appendChild(label_form_label_desde);
    div_col_md_6_desde.appendChild(input_date_desde);

    div_col_md_4_tiempo_acumulado.appendChild(label_form_label_jornada);
    div_col_md_4_tiempo_acumulado.appendChild(select_form_jornada);

    div_col_md_4_tiempo_acumulado.appendChild(label_form_label_hasta_acumulado);
    div_col_md_4_tiempo_acumulado.appendChild(select_form_tiempo_acumulado);

    form_row_g_3.appendChild(div_col_md_6_desde);
    form_row_g_3.appendChild(div_col_md_4_tiempo_acumulado);


    var div_input_group = document.createElement('div');
    div_input_group.className = 'inout-group';

    var label_form_label_razon = document.createElement('label');
    label_form_label_razon.className = 'form-label';
    label_form_label_razon.appendChild(document.createTextNode('Razón'));

    var textarea_form_control = document.createElement('textarea');
    textarea_form_control.id = 'txt_razon';
    textarea_form_control.className = 'form-control';

    div_input_group.appendChild(label_form_label_razon);
    div_input_group.appendChild(textarea_form_control);

    var btn_solicitar = document.createElement('button');
    btn_solicitar.className = 'btn btn-primary';
    btn_solicitar.id = 'btn_solicitar_tiempo_acumulado';
    btn_solicitar.style.marginTop = '5px';
    btn_solicitar.appendChild(document.createTextNode('Solicitar'));
    btn_solicitar.onclick = btnSetSolicitarTiempoAcumulado;

    div_input_group.appendChild(btn_solicitar);


    contenedor.appendChild(form_row_g_3);
    contenedor.appendChild(div_input_group);
}
function validarSolicitudTiempoAcumulado(){
    try {
        var alertPlaceholder = document.querySelector('#notificaciones_container');
        alertPlaceholder.innerHTML = "";
        var valsJS = {
            'verificacion': true
        };
        var tipo_licencia = document.getElementById('slt_tipo_tiempo_acumulado').value; 
        var dt_desde = document.getElementById('dt_desde'); 
        var dt_hasta = document.getElementById('dt_hasta');
        var slt_jornada = document.getElementById('selectJornada');
        var slt_tiempo = document.getElementById('selectTiempo');
        var txt_razon = document.getElementById('txt_razon');
        

        valsJS['tipo_licencia'] = tipo_licencia;
        if(tipo_licencia == 'Tipos'){
            showNotificacionAlert("Tiene que elegir un tipo de solicitud de tiempo acumulado","alert alert-warning")
            valsJS["verificacion"] = false;
        }
        if(dt_desde != null){
            if(dt_desde != ""){
                valsJS["dt_desde"] = dt_desde.value;
            }else{
                showNotificacionAlert("Tiene que elegir una fecha válida en el campo Desde","alert alert-warning")
                valsJS["verificacion"] = false;
            }
        }

        if(dt_hasta != null){
            if(dt_hasta != ""){
                valsJS["dt_hasta"] = dt_hasta.value;
            }else{
                showNotificacionAlert("Tiene que elegir una fecha válida en el campo Hasta","alert alert-warning")
                valsJS["verificacion"] = false;
            }
        }else{
            if(dt_desde != null){
                valsJS["dt_hasta"] = dt_desde.value;
            }
        }

        if(dt_desde != null){
            var fechaMinima = new Date();
            fechaMinima.setDate(fechaMinima.getDate());
            var fechaActual = new Date(dt_desde.value)
    
            if(fechaActual.getTime() > fechaMinima.getTime()){            
    
            }else{
                showNotificacionAlertVacaciones("La fecha inicial tiene que tener mínimo 2 días de antelación para poder hacer la solicitud.","alert alert-warning")
                valsJS["verificacion"] = false;
            }
        }

        if(dt_desde != null && dt_hasta != null){

            if(dt_desde.value > dt_hasta.value){
                showNotificacionAlertVacaciones("El campo Desde no puede ser mayor la campo Hasta","alert alert-warning")
                valsJS["verificacion"] = false;
            }
        }

        if(txt_razon != null){
            if(txt_razon != ""){
                valsJS["txt_razon"] = txt_razon.value;
            }else{
                showNotificacionAlert("Tiene que escribir algun txto en el campo Razón","alert alert-warning")
                valsJS["verificacion"] = false;
            }
        }

        if(slt_jornada != null){
            valsJS["slt_jornada"] = slt_jornada.value;
        }
        if(slt_tiempo != null){
            valsJS["slt_tiempo"] = slt_tiempo.value;
        }
        return valsJS;

    } catch (err) {
        alert("vefi: "+err);
    }
}
function btnSetSolicitarTiempoAcumulado() {
    try {
        document.getElementById('btn_solicitar_tiempo_acumulado').disabled = true; 
        var valsJS = validarSolicitudTiempoAcumulado();
        if(valsJS.verificacion){
            document.getElementById('id_tiempo_acumulado')
            ajax.jsonRpc('/set_tiempo_acumulado_solicitud', 'call', {
                valsJS: valsJS
            }).then(function (result){
                var alertPlaceholder = document.querySelector('#uia_portal_menu_administrativo_tiempo_acumulado_container');
                document.querySelector('#uia_portal_menu_administrativo_tiempo_acumulado_container_tipos').innerHTML = "";
                alertPlaceholder.innerHTML = "";
                var div_alert = document.createElement('div');
                div_alert.className = "alert alert-warning";
                div_alert.style.borderRadius = "5px";
                div_alert.style.marginTop = "5px";
                div_alert.appendChild(document.createTextNode(result));
                div_alert.style.fontSize = "15px";
                div_alert.style.fontWeight = "900";
                alertPlaceholder.appendChild(div_alert);
             });
        }else{
            document.getElementById('btn_solicitar_tiempo_acumulado').disabled = true; 
        }

    } catch (err) {
    }
}

publicWidget.registry.AceptacionTiempoAcumuladoJefaturaInmediata = publicWidget.Widget.extend({
    selector: '.portal_administrativo_gestion_tiempo_acumulado_accion_jefatura_inmediata_form',
    events: {
        'click #btn_aceptar_tiempo_acumulado': 'btnAceptarTiempoAcumulado',
        'click #btn_rechazar_tiempo_acumulado': 'btnRechazarTiempoAcumulado',
    },

    start: function () {
    },

    btnAceptarTiempoAcumulado: function(){
        var vals ={
            'id_tiempo_acumulado': document.getElementById('id_tiempo_acumulado').innerHTML,
            'accion': "Aceptado",
        };
        ajax.jsonRpc('/set_proceso_accion_tiempo_acumulado_jefatura_inmediata', 'call', {
            valsJS: vals,
        }).then(function (result){

            if(result['result']){
                var contenedor = document.querySelector('#portal_administrativo_gestion_tiempo_acumulado_accion_jefatura_inmediata_container');

                var div_alert_alert_primary = document.createElement('div');
                div_alert_alert_primary.className = 'alert alert-primary';
                div_alert_alert_primary.appendChild(document.createTextNode('¡Información de solicitud enviada, muchas gracias!!!'));

                contenedor.innerHTML = '';
                document.querySelector('#portal_administrativo_gestion_tiempo_acumulado_accion_jefatura_inmediata_container').innerHTML = "";
                document.querySelector('#notificaciones_container').innerHTML = "";
                contenedor.appendChild(div_alert_alert_primary);
            }
        });
    },
    btnRechazarTiempoAcumulado: function(){
        var vals ={
            'id_tiempo_acumulado': document.getElementById('id_tiempo_acumulado').innerHTML,
            'accion': "Rechazado",
        };
        ajax.jsonRpc('/set_proceso_accion_tiempo_acumulado_jefatura_inmediata', 'call', {
            valsJS: vals,
        }).then(function (result){

            if(result['result']){
                var contenedor = document.querySelector('#portal_administrativo_gestion_tiempo_acumulado_accion_jefatura_inmediata_container');

                var div_alert_alert_primary = document.createElement('div');
                div_alert_alert_primary.className = 'alert alert-primary';
                div_alert_alert_primary.appendChild(document.createTextNode('¡Información de solicitud enviada, muchas gracias!!!'));

                contenedor.innerHTML = '';
                document.querySelector('#portal_administrativo_gestion_tiempo_acumulado_accion_jefatura_inmediata_container').innerHTML = "";
                document.querySelector('#notificaciones_container').innerHTML = "";
                contenedor.appendChild(div_alert_alert_primary);
            }
        });
    },

});

publicWidget.registry.AceptacionTiempoAcumuladoJefaturaRH = publicWidget.Widget.extend({
    selector: '.portal_administrativo_gestion_tiempo_acumulado_accion_jefatura_RH_form',
    events: {
        'click #btn_aceptar_tiempo_acumulado': 'btnAceptarTiempoAcumulado',
        'click #btn_rechazar_tiempo_acumulado': 'btnRechazarTiempoAcumulado',
    },

    start: function () {
    },

    btnAceptarTiempoAcumulado: function(){
        var vals ={
            'id_tiempo_acumulado': document.getElementById('id_tiempo_acumulado').innerHTML,
            'accion': "Aceptado",
        };
        ajax.jsonRpc('/set_proceso_accion_tiempo_acumulado_jefatura_RH', 'call', {
            valsJS: vals,
        }).then(function (result){

            if(result['result']){
                var contenedor = document.querySelector('#portal_administrativo_gestion_tiempo_acumulado_accion_jefatura_RH_container');

                var div_alert_alert_primary = document.createElement('div');
                div_alert_alert_primary.className = 'alert alert-primary';
                div_alert_alert_primary.appendChild(document.createTextNode('¡Información de solicitud enviada, muchas gracias!!!'));
                contenedor.innerHTML = '';
                contenedor.appendChild(div_alert_alert_primary);

                if(result['reporte']){
                    var URLactual = window.location.hostname
                    window.open('/create_report_tiempo_acumulado?idTiempoAcumulado='+result['idTiempoAcumulado'], "_blank");
                }

            }
        });
    },
    btnRechazarTiempoAcumulado: function(){
        var vals ={
            'id_tiempo_acumulado': document.getElementById('id_tiempo_acumulado').innerHTML,
            'accion': "Rechazado",
        };
        ajax.jsonRpc('/set_proceso_accion_tiempo_acumulado_jefatura_RH', 'call', {
            valsJS: vals,
        }).then(function (result){

            if(result['result']){
                var contenedor = document.querySelector('#portal_administrativo_gestion_tiempo_acumulado_accion_jefatura_RH_container');

                var div_alert_alert_primary = document.createElement('div');
                div_alert_alert_primary.className = 'alert alert-primary';
                div_alert_alert_primary.appendChild(document.createTextNode('¡Información de solicitud enviada, muchas gracias!!!'));
                contenedor.innerHTML = '';
                contenedor.appendChild(div_alert_alert_primary);
            }
        });
    },

});

publicWidget.registry.UIAPortalIncapacidadess = publicWidget.Widget.extend({
    selector: '.uia_portal_administrativo_gestion_incapacidades',
    events: {
        'click #uia_portal_administrativo_incapacidades_historial': 'openIcapacidadesHistorial',
        'click #uia_portal_administrativo_incapacidades_solicitud': 'openIcapacidadesSolicitud',
    },

    start: function () {
        this.openIcapacidadesHistorial();
    },
    
    openIcapacidadesHistorial: function() {
        try {
            ajax.jsonRpc('/get_incapacidades_historial', 'call', {}).then(function (result){
                document.getElementById('uia_portal_menu_administrativo_incapacidades_container').innerHTML = "";
                var contenedor = document.querySelector('#uia_portal_menu_administrativo_incapacidades_container');          
                contenedor.style.overflowY = 'scroll';
                contenedor.style.height = '300px';
    
                var table = document.createElement('table');
                table.className = 'table';
    
                var thead = document.createElement('thead');
    
                var tr = document.createElement('tr');
    
                var th1 = document.createElement('th');
                th1.appendChild(document.createTextNode('Desde'))
                th1.scope = 'col'
    
                var th2 = document.createElement('th');
                th2.appendChild(document.createTextNode('Hasta'))
                th2.scope = 'col'
    
                var th3 = document.createElement('th');
                th3.appendChild(document.createTextNode('Dias'))
                th3.scope = 'col'
    
                var th4 = document.createElement('th');
                th4.appendChild(document.createTextNode('Tipo'))
                th4.scope = 'col'
    
                tr.appendChild(th1);
                tr.appendChild(th2);
                tr.appendChild(th3);
                tr.appendChild(th4);
                thead.appendChild(tr);
    
                var tbody = document.createElement('tbody');
    
                for(let x in result){
                    var tr = document.createElement('tr');
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['fechaInicioIncapacidad']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);
                    
    
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['fechaFinIncapacidad']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);
    
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['totalDiasIncapacidad']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);
    
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['tipoIncapacidad']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);     
                }
    
                table.appendChild(thead);
                table.appendChild(tbody);
                contenedor.appendChild(table);
                
            });
        } catch (err) {
        }
    },
    
    openIcapacidadesSolicitud: function() {
        try {
                document.getElementById('uia_portal_menu_administrativo_incapacidades_container').innerHTML = "";
                document.getElementById('uia_portal_menu_administrativo_incapacidades_container').style.overflowY= "";
                document.getElementById('uia_portal_menu_administrativo_incapacidades_container').style.height= "";
                var contenedor = document.querySelector('#uia_portal_menu_administrativo_incapacidades_container');
    
                var form_row_g_3 = document.createElement('form');
                form_row_g_3.className = 'row g-3';
    
                var div_col_md_6_desde = document.createElement('div');
                div_col_md_6_desde.className = 'col-md-6';
    
                var div_col_md_6_hasta = document.createElement('div');
                div_col_md_6_hasta.className = 'col-md-6';

                var div_col_md_4_tipo = document.createElement('div');
                div_col_md_4_tipo.className = 'col-md-4';

                var div_col_md_6_boleta = document.createElement('div');
                div_col_md_6_boleta.className = 'col-md-6';


    
                var label_form_label_desde = document.createElement('label');
                label_form_label_desde.className = 'form-label';
                label_form_label_desde.appendChild(document.createTextNode('Desde'));
    
                var input_date_desde = document.createElement('input');
                input_date_desde.className = 'form-control';
                input_date_desde.id = 'dt_desde';
                input_date_desde.type = 'date';
    
                var label_form_label_hasta = document.createElement('label');
                label_form_label_hasta.className = 'form-label';
                label_form_label_hasta.appendChild(document.createTextNode('Hasta'));
    
                var input_date_hasta = document.createElement('input');
                input_date_hasta.className = 'form-control';
                input_date_hasta.id = 'dt_hasta';
                input_date_hasta.type = 'date';

                var label_form_label_tipo = document.createElement('label');
                label_form_label_tipo.className = 'form-label';
                label_form_label_tipo.appendChild(document.createTextNode('Tipo de incapacidad'));

                var select_form_tipo = document.createElement('select')
                select_form_tipo.className = 'form-control'
                select_form_tipo.id = 'selectTipo'

                var list = ['INS','SEM','MAT']

                for (var i = 0; i<=2; i++){
                    var opt = document.createElement('option');
                    opt.value = list[i];
                    opt.innerHTML = list[i];
                    select_form_tipo.appendChild(opt);
                }

                var label_form_label_boleta = document.createElement('label');
                label_form_label_boleta.className = 'form-label';
                label_form_label_boleta.appendChild(document.createTextNode('Numero de boleta'));
    
                var input_date_boleta = document.createElement('input');
                input_date_boleta.className = 'form-control';
                input_date_boleta.id = 'txt_boleta';
                input_date_boleta.type = 'text';

                div_col_md_6_desde.appendChild(label_form_label_desde);
                div_col_md_6_desde.appendChild(input_date_desde);
    
                div_col_md_6_hasta.appendChild(label_form_label_hasta);
                div_col_md_6_hasta.appendChild(input_date_hasta);

                div_col_md_6_boleta.appendChild(label_form_label_boleta);
                div_col_md_6_boleta.appendChild(input_date_boleta);

                div_col_md_4_tipo.appendChild(label_form_label_tipo)
                div_col_md_4_tipo.appendChild(select_form_tipo)
    
                form_row_g_3.appendChild(div_col_md_6_desde);
                form_row_g_3.appendChild(div_col_md_6_hasta);
                form_row_g_3.appendChild(div_col_md_6_boleta)
                form_row_g_3.appendChild(div_col_md_4_tipo);
    
    
                var div_input_group = document.createElement('div');
                div_input_group.className = 'inout-group';
    
                var btn_solicitar = document.createElement('button');
                btn_solicitar.className = 'btn btn-primary';
                btn_solicitar.style.marginTop = '5px';
                btn_solicitar.appendChild(document.createTextNode('Solicitar'));
                btn_solicitar.onclick = btnSetSolicitarIncapacidad;
    
                div_input_group.appendChild(btn_solicitar);
    
    
                contenedor.appendChild(form_row_g_3);
                contenedor.appendChild(div_input_group);
        } catch (err) {
            alert(err);
        }
    },
});
function btnSetSolicitarIncapacidad() {
    try {
        ajax.jsonRpc('/set_incapacidad_solicitud', 'call', {
            desde: new Date(document.getElementById("dt_desde").value),
            hasta: new Date(document.getElementById("dt_hasta").value),
            boleta: document.getElementById("txt_boleta").value,
            tipo: document.getElementById("selectTipo").options[document.getElementById("selectTipo").selectedIndex].text,
        }).then(function (result){
            var alertPlaceholder = document.querySelector('#uia_portal_menu_administrativo_incapacidades_container');
            alertPlaceholder.innerHTML = "";
            var div_alert = document.createElement('div');
            div_alert.className = "alert alert-warning";
            div_alert.style.borderRadius = "5px";
            div_alert.style.marginTop = "5px";
            div_alert.appendChild(document.createTextNode(result));
            div_alert.style.fontSize = "15px";
            div_alert.style.fontWeight = "900";
            alertPlaceholder.appendChild(div_alert);
         });
    } catch (err) {
        alert(err);
    }
}

publicWidget.registry.UIAPortalLicencias= publicWidget.Widget.extend({
    selector: '.uia_portal_administrativo_gestion_licencias',
    events: {
        'click #uia_portal_administrativo_licencias_historial': 'openLicenciasHistorial',
        'click #uia_portal_administrativo_licencias_solicitud': 'openLicenciaSolicitud',
    },

    start: function () {
        this.openLicenciasHistorial();
    },
    
    openLicenciasHistorial: function() {
        try {
            ajax.jsonRpc('/get_licencias_historial', 'call', {}).then(function (result){
                document.getElementById('uia_portal_menu_administrativo_licencias_container').innerHTML = "";
                document.getElementById('notificaciones_licencias_container').innerHTML = "";
                var contenedor = document.querySelector('#uia_portal_menu_administrativo_licencias_container');          
                contenedor.style.overflowY = 'scroll';
                contenedor.style.height = '300px';
    
                var table = document.createElement('table');
                table.className = 'table';
    
                var thead = document.createElement('thead');
    
                var tr = document.createElement('tr');
    
                var th1 = document.createElement('th');
                th1.appendChild(document.createTextNode('Tipo Licencia'))
                th1.scope = 'col'

                var th2 = document.createElement('th');
                th2.appendChild(document.createTextNode('Desde'))
                th2.scope = 'col'
    
                var th3 = document.createElement('th');
                th3.appendChild(document.createTextNode('Hasta'))
                th3.scope = 'col'
    
                var th4 = document.createElement('th');
                th4.appendChild(document.createTextNode('Tipo Pago'))
                th4.scope = 'col'
    
                var th5 = document.createElement('th');
                th5.appendChild(document.createTextNode('Estado Jefatura'))
                th5.scope = 'col'

                var th6 = document.createElement('th');
                th6.appendChild(document.createTextNode('Estado RH'))
                th6.scope = 'col'
    
                tr.appendChild(th1);
                tr.appendChild(th2);
                tr.appendChild(th3);
                tr.appendChild(th4);
                tr.appendChild(th5);
                tr.appendChild(th6);
                thead.appendChild(tr);
    
                var tbody = document.createElement('tbody');
    
                for(let x in result){
                    var tr = document.createElement('tr');

                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['tipoLicencia']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);

                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['fechaInicioLicencia']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);
                    
    
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['fechaFinLicencia']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);
    
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['tipoPago']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);
    
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['estadoJefatura']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);

                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(result[x]['estadoRH']));
                    tr.appendChild(td);
                    tbody.appendChild(tr);    
                }
    
                table.appendChild(thead);
                table.appendChild(tbody);
                contenedor.appendChild(table);
                
            });
        } catch (err) {
        }
    },
    
    openLicenciaSolicitud: function() {
        try {
                document.getElementById('uia_portal_menu_administrativo_licencias_container').innerHTML = "";
                document.getElementById('uia_portal_menu_administrativo_licencias_container').style.overflowY= "";
                document.getElementById('uia_portal_menu_administrativo_licencias_container').style.height= "";
                document.getElementById('notificaciones_licencias_container').innerHTML = "";

                ajax.jsonRpc('/get_tipo_licencias', 'call', {}).then(function (result){
                    document.getElementById('uia_portal_menu_administrativo_licencias_container').innerHTML = "";
                    var contenedor = document.querySelector('#uia_portal_menu_administrativo_licencias_container');

                    var select_tipo_licencia = document.createElement('select');
                    select_tipo_licencia.className = 'form-control';
                    select_tipo_licencia.id = 'slt_tipo_licencia';
                    select_tipo_licencia.style.marginTop = '10px';
                    select_tipo_licencia.onchange = onchangeTipoLicencia;

                    result['tipoTicencias'].forEach((item,idex,arr)=>{
                        var opt = document.createElement('option');
                        opt.value = item;
                        opt.innerHTML = item;
                        select_tipo_licencia.appendChild(opt);
                    });
                    
                    contenedor.appendChild(select_tipo_licencia);
                });

        } catch (err) {
            alert(err);
        }
    },
});

function onchangeTipoLicencia(result){
    var contenedor = document.querySelector('#uia_portal_menu_administrativo_tipos_licencias_container');

    var tipoLicencia = document.getElementById('slt_tipo_licencia').value

    switch (tipoLicencia) {
        case "Sin goce salarial":
            contenedor.innerHTML = "";
            tipoLicenciaSinGoce();
          break;
        case "Matrimonio":
            contenedor.innerHTML = "";
            tipoLicenciaMatrimonio();

          break;
        case "Muerte de un familiar":
            contenedor.innerHTML = "";
            tipoLicenciaMuerte();
          break;
        case "Paternidad":
            contenedor.innerHTML = "";
            tipoLicenciaPaternidad();
          break;
        case "Maternidad":
            contenedor.innerHTML = "";
            tipoLicenciaMaternidad()
          break;
        default:
            contenedor.innerHTML = "";
          break;
      }
}

function tipoLicenciaSinGoce(){
    var contenedor = document.querySelector('#uia_portal_menu_administrativo_tipos_licencias_container');

    var form = document.createElement('form');
    //form_row_g_3.className = 'row g-3';

    //#region Fechas
    var div_form_row_licencias_fechas= document.createElement('div');
    div_form_row_licencias_fechas.className = 'form-row';

    //#region Fecha Desde
    var div_form_group_col_md_6_tipo_licencia_dt_desde = document.createElement('div');
    div_form_group_col_md_6_tipo_licencia_dt_desde.className = 'form-group col-md-6';

    var label_form_label_desde = document.createElement('label');
    label_form_label_desde.className = 'form-label';
    label_form_label_desde.appendChild(document.createTextNode('Desde'));

    var input_date_desde = document.createElement('input');
    input_date_desde.className = 'form-control';
    input_date_desde.id = 'dt_desde';
    input_date_desde.type = 'date';

    div_form_group_col_md_6_tipo_licencia_dt_desde.appendChild(label_form_label_desde);
    div_form_group_col_md_6_tipo_licencia_dt_desde.appendChild(input_date_desde);

    div_form_row_licencias_fechas.appendChild(div_form_group_col_md_6_tipo_licencia_dt_desde);
    //#endregion

    //#region Fecha Hasta
    var div_form_group_col_md_6_tipo_licencia_dt_hasta = document.createElement('div');
    div_form_group_col_md_6_tipo_licencia_dt_hasta.className = 'form-group col-md-6';
                            
    var label_form_label_hasta = document.createElement('label');
    label_form_label_hasta.className = 'form-label';
    label_form_label_hasta.appendChild(document.createTextNode('Hasta'));

    var input_date_hasta = document.createElement('input');
    input_date_hasta.className = 'form-control';
    input_date_hasta.id = 'dt_hasta';
    input_date_hasta.type = 'date';

    div_form_group_col_md_6_tipo_licencia_dt_hasta.appendChild(label_form_label_hasta);
    div_form_group_col_md_6_tipo_licencia_dt_hasta.appendChild(input_date_hasta);

    div_form_row_licencias_fechas.appendChild(div_form_group_col_md_6_tipo_licencia_dt_hasta);
    //#endregion

    form.appendChild(div_form_row_licencias_fechas);
    //#endregion

    //#region Razon
    var div_form_group = document.createElement('div');
    div_form_group.className = 'form-group';

    var label_form_label_razon = document.createElement('label');
    label_form_label_razon.className = 'form-label';
    label_form_label_razon.appendChild(document.createTextNode('Razón'));

    var textarea_form_control = document.createElement('textarea');
    textarea_form_control.id = 'txt_razon';
    textarea_form_control.className = 'form-control';

    div_form_group.appendChild(label_form_label_razon);
    div_form_group.appendChild(textarea_form_control);

    form.appendChild(div_form_group);
    //#endregion
    
    //#region Botron Solicitar
    var btn_solicitar = document.createElement('button');
    btn_solicitar.type = "button";
    btn_solicitar.className = 'btn btn-primary';
    btn_solicitar.id = 'btn_solicitar_licencia';
    btn_solicitar.style.marginTop = '15px';
    btn_solicitar.style.marginBottom = '15px';
    btn_solicitar.appendChild(document.createTextNode('Solicitar'));
    btn_solicitar.onclick = btnSetSolicitarLicencia;     

    form.appendChild(btn_solicitar);
    //#endregion
    
    contenedor.appendChild(form);

}

function tipoLicenciaMatrimonio(){
    var contenedor = document.querySelector('#uia_portal_menu_administrativo_tipos_licencias_container');

    var form = document.createElement('form');
    //form_row_g_3.className = 'row g-3';

    //#region Fechas
    var div_form_row_licencias_fechas= document.createElement('div');
    div_form_row_licencias_fechas.className = 'form-row';

    //#region Fecha Desde
    var div_form_group_col_md_6_tipo_licencia_dt_desde = document.createElement('div');
    div_form_group_col_md_6_tipo_licencia_dt_desde.className = 'form-group col-md-6';

    var label_form_label_desde = document.createElement('label');
    label_form_label_desde.className = 'form-label';
    label_form_label_desde.appendChild(document.createTextNode('Día'));

    var input_date_desde = document.createElement('input');
    input_date_desde.className = 'form-control';
    input_date_desde.id = 'dt_desde';
    input_date_desde.type = 'date';

    div_form_group_col_md_6_tipo_licencia_dt_desde.appendChild(label_form_label_desde);
    div_form_group_col_md_6_tipo_licencia_dt_desde.appendChild(input_date_desde);

    div_form_row_licencias_fechas.appendChild(div_form_group_col_md_6_tipo_licencia_dt_desde);
    //#endregion

    form.appendChild(div_form_row_licencias_fechas);
    //#endregion

    //#region Razon
    var div_form_group = document.createElement('div');
    div_form_group.className = 'form-group';

    var label_form_label_razon = document.createElement('label');
    label_form_label_razon.className = 'form-label';
    label_form_label_razon.appendChild(document.createTextNode('Razón'));

    var textarea_form_control = document.createElement('textarea');
    textarea_form_control.id = 'txt_razon';
    textarea_form_control.className = 'form-control';

    div_form_group.appendChild(label_form_label_razon);
    div_form_group.appendChild(textarea_form_control);

    form.appendChild(div_form_group);
    //#endregion
    
    //#region Botron Solicitar
    var btn_solicitar = document.createElement('button');
    btn_solicitar.type = "button";
    btn_solicitar.className = 'btn btn-primary';
    btn_solicitar.id = 'btn_solicitar_licencia';
    btn_solicitar.style.marginTop = '15px';
    btn_solicitar.style.marginBottom = '15px';
    btn_solicitar.appendChild(document.createTextNode('Solicitar'));
    btn_solicitar.onclick = btnSetSolicitarLicencia;     

    form.appendChild(btn_solicitar);
    //#endregion
    
    contenedor.appendChild(form);

}

function tipoLicenciaMuerte(){
    var contenedor = document.querySelector('#uia_portal_menu_administrativo_tipos_licencias_container');

    var form = document.createElement('form');
    //form_row_g_3.className = 'row g-3';

    //#region Fechas
    var div_form_row_licencias_fechas= document.createElement('div');
    div_form_row_licencias_fechas.className = 'form-row';

    //#region Fecha Desde
    var div_form_group_col_md_6_tipo_licencia_dt_desde = document.createElement('div');
    div_form_group_col_md_6_tipo_licencia_dt_desde.className = 'form-group col-md-6';

    var label_form_label_desde = document.createElement('label');
    label_form_label_desde.className = 'form-label';
    label_form_label_desde.appendChild(document.createTextNode('Día'));

    var input_date_desde = document.createElement('input');
    input_date_desde.className = 'form-control';
    input_date_desde.id = 'dt_desde';
    input_date_desde.type = 'date';

    div_form_group_col_md_6_tipo_licencia_dt_desde.appendChild(label_form_label_desde);
    div_form_group_col_md_6_tipo_licencia_dt_desde.appendChild(input_date_desde);

    div_form_row_licencias_fechas.appendChild(div_form_group_col_md_6_tipo_licencia_dt_desde);
    //#endregion

    form.appendChild(div_form_row_licencias_fechas);
    //#endregion

    //#region Razon
    var div_form_group = document.createElement('div');
    div_form_group.className = 'form-group';

    var label_form_label_razon = document.createElement('label');
    label_form_label_razon.className = 'form-label';
    label_form_label_razon.appendChild(document.createTextNode('Razón'));

    var textarea_form_control = document.createElement('textarea');
    textarea_form_control.id = 'txt_razon';
    textarea_form_control.className = 'form-control';

    div_form_group.appendChild(label_form_label_razon);
    div_form_group.appendChild(textarea_form_control);

    form.appendChild(div_form_group);
    //#endregion
    
    //#region Botron Solicitar
    var btn_solicitar = document.createElement('button');
    btn_solicitar.type = "button";
    btn_solicitar.className = 'btn btn-primary';
    btn_solicitar.id = 'btn_solicitar_licencia';
    btn_solicitar.style.marginTop = '15px';
    btn_solicitar.style.marginBottom = '15px';
    btn_solicitar.appendChild(document.createTextNode('Solicitar'));
    btn_solicitar.onclick = btnSetSolicitarLicencia;     

    form.appendChild(btn_solicitar);
    //#endregion
    
    contenedor.appendChild(form);

}

function tipoLicenciaPaternidad(){
    var contenedor = document.querySelector('#uia_portal_menu_administrativo_tipos_licencias_container');

    var form = document.createElement('form');
    //form_row_g_3.className = 'row g-3';

    //#region Anno Mes
    var div_form_row_licencias_fechas= document.createElement('div');
    div_form_row_licencias_fechas.className = 'form-row';

    //#region Annos
    var div_form_group_col_md_6_tipo_licencia_anno = document.createElement('div');
    div_form_group_col_md_6_tipo_licencia_anno.className = 'form-group col-md-6';

    var label_select_anno= document.createElement('label');
    label_select_anno.appendChild(document.createTextNode('Seleccione el año'));

    var select_anno= document.createElement('select');
    select_anno.id = 'slt_anno';
    select_anno.className = 'form-control';

    var annoActual =  new Date().getFullYear();
    for (var i = 0; i<=2; i++){
        var opt = document.createElement('option');
        opt.value = annoActual;
        opt.innerHTML = annoActual
        select_anno.appendChild(opt);
        annoActual ++;
    }

    div_form_group_col_md_6_tipo_licencia_anno.appendChild(label_select_anno);
    div_form_group_col_md_6_tipo_licencia_anno.appendChild(select_anno);

    div_form_row_licencias_fechas.appendChild(div_form_group_col_md_6_tipo_licencia_anno);
    //#endregion

    //#region Mes
    var div_form_group_col_md_6_tipo_licencia_mes = document.createElement('div');
    div_form_group_col_md_6_tipo_licencia_mes.className = 'form-group col-md-6';

    var label_select_mes= document.createElement('label');
    label_select_mes.appendChild(document.createTextNode('Seleccione el mes'));

    var select_mes= document.createElement('select');
    select_mes.id = 'slt_mes';
    select_mes.className = 'form-control';


    var mesActual  = new Date("2022/1/01");
    for (var i = 0; i<=11; i++){
        var opt = document.createElement('option');
        opt.value = mesActual.getMonth()+1;
        opt.innerHTML = mesActual.toLocaleString("es-CR", {month: "long"});
        select_mes.appendChild(opt);
        mesActual.setMonth(i+1);
    }

    div_form_group_col_md_6_tipo_licencia_mes.appendChild(label_select_mes);
    div_form_group_col_md_6_tipo_licencia_mes.appendChild(select_mes);

    div_form_row_licencias_fechas.appendChild(div_form_group_col_md_6_tipo_licencia_mes);
    //#endregion

    form.appendChild(div_form_row_licencias_fechas);
    //#endregion

    //#region Dias
    var div_form_row_licencias_dias= document.createElement('div');
    div_form_row_licencias_dias.className = 'form-row';

    //#region Dia 1
    var div_form_group_col_md_6_tipo_licencia_dia_1 = document.createElement('div');
    div_form_group_col_md_6_tipo_licencia_dia_1.className = 'form-group col-md-6';

    var label_select_dia_1= document.createElement('label');
    label_select_dia_1.appendChild(document.createTextNode('Seleccione el Día 1'));

    var select_dia_1= document.createElement('select');
    select_dia_1.id = 'slt_dia_1';
    select_dia_1.className = 'form-control';

    var dias = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
    var diasID = [0,1,2,3,4,5,6]

    for (var i = 0; i<=6; i++){
        var opt = document.createElement('option');
        opt.value = diasID[i],
        opt.innerHTML = dias[i];
        select_dia_1.appendChild(opt);
    }

    div_form_group_col_md_6_tipo_licencia_dia_1.appendChild(label_select_dia_1);
    div_form_group_col_md_6_tipo_licencia_dia_1.appendChild(select_dia_1);

    div_form_row_licencias_dias.appendChild(div_form_group_col_md_6_tipo_licencia_dia_1);
    //#endregion

    //#region Annos
    var div_form_group_col_md_6_tipo_licencia_dia_2 = document.createElement('div');
    div_form_group_col_md_6_tipo_licencia_dia_2.className = 'form-group col-md-6';

    var label_select_dia_2= document.createElement('label');
    label_select_dia_2.appendChild(document.createTextNode('Seleccione el Día 2'));

    var select_dia_2= document.createElement('select');
    select_dia_2.id = 'slt_dia_2';
    select_dia_2.className = 'form-control';

    var dias = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
    var diasID = [0,1,2,3,4,5,6]

    for (var i = 0; i<=6; i++){
        var opt = document.createElement('option');
        opt.value = diasID[i],
        opt.innerHTML = dias[i];
        select_dia_2.appendChild(opt);
    }

    div_form_group_col_md_6_tipo_licencia_dia_2.appendChild(label_select_dia_2);
    div_form_group_col_md_6_tipo_licencia_dia_2.appendChild(select_dia_2);

    div_form_row_licencias_dias.appendChild(div_form_group_col_md_6_tipo_licencia_dia_2);
    //#endregion

    form.appendChild(div_form_row_licencias_dias);
    //#endregion

    //#region Razon
    var div_form_group = document.createElement('div');
    div_form_group.className = 'form-group';

    var label_form_label_razon = document.createElement('label');
    label_form_label_razon.className = 'form-label';
    label_form_label_razon.appendChild(document.createTextNode('Razón'));

    var textarea_form_control = document.createElement('textarea');
    textarea_form_control.id = 'txt_razon';
    textarea_form_control.className = 'form-control';

    div_form_group.appendChild(label_form_label_razon);
    div_form_group.appendChild(textarea_form_control);

    form.appendChild(div_form_group);
    //#endregion
    
    //#region Botron Solicitar
    var btn_solicitar = document.createElement('button');
    btn_solicitar.type = "button";
    btn_solicitar.className = 'btn btn-primary';
    btn_solicitar.id = 'btn_solicitar_licencia';
    btn_solicitar.style.marginTop = '15px';
    btn_solicitar.style.marginBottom = '15px';
    btn_solicitar.appendChild(document.createTextNode('Solicitar'));
    btn_solicitar.onclick = btnSetSolicitarLicencia;     

    form.appendChild(btn_solicitar);
    //#endregion
    
    contenedor.appendChild(form);

}

function tipoLicenciaMaternidad(){
    var contenedor = document.querySelector('#uia_portal_menu_administrativo_tipos_licencias_container');

    var form = document.createElement('form');
    //form_row_g_3.className = 'row g-3';

    //#region Anno Mes
    var div_form_row_licencias_fechas= document.createElement('div');
    div_form_row_licencias_fechas.className = 'form-row';

    //#region Annos
    var div_form_group_col_md_6_tipo_licencia_anno = document.createElement('div');
    div_form_group_col_md_6_tipo_licencia_anno.className = 'form-group col-md-6';

    var label_select_anno= document.createElement('label');
    label_select_anno.appendChild(document.createTextNode('Seleccione el año'));

    var select_anno= document.createElement('select');
    select_anno.id = 'slt_anno';
    select_anno.className = 'form-control';

    var annoActual =  new Date().getFullYear();
    for (var i = 0; i<=2; i++){
        var opt = document.createElement('option');
        opt.value = annoActual;
        opt.innerHTML = annoActual
        select_anno.appendChild(opt);
        annoActual ++;
    }

    div_form_group_col_md_6_tipo_licencia_anno.appendChild(label_select_anno);
    div_form_group_col_md_6_tipo_licencia_anno.appendChild(select_anno);

    div_form_row_licencias_fechas.appendChild(div_form_group_col_md_6_tipo_licencia_anno);
    //#endregion

    //#region Mes
    var div_form_group_col_md_6_tipo_licencia_mes = document.createElement('div');
    div_form_group_col_md_6_tipo_licencia_mes.className = 'form-group col-md-6';

    var label_select_mes= document.createElement('label');
    label_select_mes.appendChild(document.createTextNode('Seleccione el mes'));

    var select_mes= document.createElement('select');
    select_mes.id = 'slt_mes';
    select_mes.className = 'form-control';


    var mesActual  = new Date("2022/1/01");
    for (var i = 0; i<=11; i++){
        var opt = document.createElement('option');
        opt.value = mesActual.getMonth()+1;
        opt.innerHTML = mesActual.toLocaleString("es-CR", {month: "long"});
        select_mes.appendChild(opt);
        mesActual.setMonth(i+1);
    }

    div_form_group_col_md_6_tipo_licencia_mes.appendChild(label_select_mes);
    div_form_group_col_md_6_tipo_licencia_mes.appendChild(select_mes);

    div_form_row_licencias_fechas.appendChild(div_form_group_col_md_6_tipo_licencia_mes);
    //#endregion

    form.appendChild(div_form_row_licencias_fechas);
    //#endregion

    //#region Razon
    var div_form_group = document.createElement('div');
    div_form_group.className = 'form-group';

    var label_form_label_razon = document.createElement('label');
    label_form_label_razon.className = 'form-label';
    label_form_label_razon.appendChild(document.createTextNode('Razón'));

    var textarea_form_control = document.createElement('textarea');
    textarea_form_control.id = 'txt_razon';
    textarea_form_control.className = 'form-control';

    div_form_group.appendChild(label_form_label_razon);
    div_form_group.appendChild(textarea_form_control);

    form.appendChild(div_form_group);
    //#endregion
    
    //#region Botron Solicitar
    var btn_solicitar = document.createElement('button');
    btn_solicitar.type = "button";
    btn_solicitar.className = 'btn btn-primary';
    btn_solicitar.id = 'btn_solicitar_licencia';
    btn_solicitar.style.marginTop = '15px';
    btn_solicitar.style.marginBottom = '15px';
    btn_solicitar.appendChild(document.createTextNode('Solicitar'));
    btn_solicitar.onclick = btnSetSolicitarLicencia;     

    form.appendChild(btn_solicitar);
    //#endregion
    
    contenedor.appendChild(form);

}

function btnSetSolicitarLicencia() {
    try {

        document.getElementById('btn_solicitar_licencia').disabled = true; 
        var valsJS = validarSolicitudLicencia();
        if(valsJS.verificacion){
            ajax.jsonRpc('/set_licencia_solicitud', 'call', {
                valsJS: valsJS
            }).then(function (result){
                document.querySelector('#uia_portal_menu_administrativo_tipos_licencias_container').innerHTML = "";
                
                showNotificacionAlert("Gracias por su solicitud, en la pestaña de historial puede ver el seguimiento de la licencia.","alert alert-success");
             });
        }else{
            document.getElementById('btn_solicitar_licencia').disabled = false; 
        }
    } catch (err) {
        alert(err);
    }
}

function validarSolicitudLicencia(){
    try {
        var alertPlaceholder = document.querySelector('#notificaciones_licencias_container');
        alertPlaceholder.innerHTML = "";
        var valsJS = {
            'verificacion': true
        };

        var tipo_licencia = document.getElementById('slt_tipo_licencia').value; 
        var dt_desde = document.getElementById('dt_desde'); 
        var dt_hasta = document.getElementById('dt_hasta'); 
        var txt_razon = document.getElementById('txt_razon');
        var slt_anno = document.getElementById('slt_anno'); 
        var slt_mes = document.getElementById('slt_mes'); 
        var slt_dia_1 = document.getElementById('slt_dia_1'); 
        var slt_dia_2 = document.getElementById('slt_dia_2'); 
        

        valsJS['tipo_licencia'] = tipo_licencia;

        if(dt_desde != null){
            if(dt_desde != ""){
                valsJS["dt_desde"] = dt_desde.value;
            }else{
                showNotificacionAlert("Tiene que elegir una fecha válida en el campo Desde","alert alert-warning")
                valsJS["verificacion"] = false;
            }
        }

        if(dt_hasta != null){
            if(dt_hasta != ""){
                valsJS["dt_hasta"] = dt_hasta.value;
            }else{
                showNotificacionAlert("Tiene que elegir una fecha válida en el campo Hasta","alert alert-warning")
                valsJS["verificacion"] = false;
            }
        }else{
            if(dt_desde != null){
                valsJS["dt_hasta"] = dt_desde.value;
            }
        }

        if(dt_desde != null){
            var fechaMinima = new Date();
            fechaMinima.setDate(fechaMinima.getDate());
            var fechaActual = new Date(dt_desde.value)
    
            if(fechaActual.getTime() > fechaMinima.getTime()){            
    
            }else{
                showNotificacionAlertVacaciones("La fecha inicial tiene que tener mínimo 2 días de antelación para poder hacer la solicitud.","alert alert-warning")
                valsJS["verificacion"] = false;
            }
        }

        if(dt_desde != null && dt_hasta != null){

            if(dt_desde.value > dt_hasta.value){
                showNotificacionAlertVacaciones("El campo Desde no puede ser mayor la campo Hasta","alert alert-warning")
                valsJS["verificacion"] = false;
            }
        }

        if(txt_razon != null){
            if(txt_razon != ""){
                valsJS["txt_razon"] = txt_razon.value;
            }else{
                showNotificacionAlert("Tiene que escribir algun txto en el campo Razón","alert alert-warning")
                valsJS["verificacion"] = false;
            }
        }

        if(slt_anno != null){
            if(slt_anno != ""){
                valsJS["slt_anno"] = slt_anno.value;
            }else{
                showNotificacionAlert("Tiene que seleccionar algun año ","alert alert-warning")
                valsJS["verificacion"] = false;
            }
        }

        if(slt_mes != null){
            if(slt_mes != ""){
                valsJS["slt_mes"] = slt_mes.value;
            }else{
                showNotificacionAlert("Tiene que seleccionar algun año ","alert alert-warning")
                valsJS["verificacion"] = false;
            }
        }

        if(slt_dia_1 != null){
            if(slt_dia_1 != ""){
                valsJS["slt_dia_1"] = slt_dia_1.value;
            }else{
                showNotificacionAlert("Tiene que seleccionar algun año ","alert alert-warning")
                valsJS["verificacion"] = false;
            }
        }

        if(slt_dia_2 != null){
            if(slt_dia_2 != ""){
                valsJS["slt_dia_2"] = slt_dia_2.value;
            }else{
                showNotificacionAlert("Tiene que seleccionar algun año ","alert alert-warning")
                valsJS["verificacion"] = false;
            }
        }

        return valsJS;

    } catch (err) {
        alert("vefi: "+err);
    }
}

function showNotificacionAlert(notificacion,tipo){
    var alertPlaceholder = document.querySelector('#notificaciones_licencias_container');
    var div_alert = document.createElement('div');
    var p_text = document.createElement('p');
    p_text.innerHTML = notificacion;
    div_alert.className = tipo;
    div_alert.id = 'alert_docente_no_encontrado'
    div_alert.style.borderRadius = "5px";
    div_alert.style.marginTop = "5px";
    div_alert.appendChild(p_text);
    div_alert.style.fontSize = "15px";
    div_alert.style.fontWeight = "900";
    alertPlaceholder.appendChild(div_alert);
}

publicWidget.registry.AceptacionLicenciaJefaturaInmediata = publicWidget.Widget.extend({
    selector: '.portal_administrativo_gestion_licencias_accion_jefatura_inmediata_form',
    events: {
        'click #btn_aceptar_licencia': 'btnAceptarLicencia',
        'click #btn_rechazar_licencia': 'btnRechazarLicencia',
    },

    start: function () {
    },

    btnAceptarLicencia: function(){
        var vals ={
            'id_licencia': document.getElementById('id_licencia').innerHTML,
            'accion': "Aceptado",
        };
        ajax.jsonRpc('/set_proceso_accion_licencia_jefatura_inmediata', 'call', {
            valsJS: vals,
        }).then(function (result){

            if(result['result']){
                var contenedor = document.querySelector('#portal_administrativo_gestion_licencias_accion_jefatura_inmediata_container');

                var div_alert_alert_primary = document.createElement('div');
                div_alert_alert_primary.className = 'alert alert-primary';
                div_alert_alert_primary.appendChild(document.createTextNode('¡Información de solicitud enviada, muchas gracias!!!'));

                contenedor.innerHTML = '';
                document.querySelector('#portal_administrativo_gestion_licencias_accion_jefatura_inmediata_container').innerHTML = "";
                document.querySelector('#notificaciones_container').innerHTML = "";
                contenedor.appendChild(div_alert_alert_primary);
            }
        });
    },
    btnRechazarLicencia: function(){
        var vals ={
            'id_licencia': document.getElementById('id_licencia').innerHTML,
            'accion': "Rechazado",
        };
        ajax.jsonRpc('/set_proceso_accion_licencia_jefatura_inmediata', 'call', {
            valsJS: vals,
        }).then(function (result){

            if(result['result']){
                var contenedor = document.querySelector('#portal_administrativo_gestion_licencias_accion_jefatura_inmediata_container');

                var div_alert_alert_primary = document.createElement('div');
                div_alert_alert_primary.className = 'alert alert-primary';
                div_alert_alert_primary.appendChild(document.createTextNode('¡Información de solicitud enviada, muchas gracias!!!'));

                contenedor.innerHTML = '';
                document.querySelector('#portal_administrativo_gestion_licencias_accion_jefatura_inmediata_container').innerHTML = "";
                document.querySelector('#notificaciones_container').innerHTML = "";
                contenedor.appendChild(div_alert_alert_primary);
            }
        });
    },

});

publicWidget.registry.AceptacionLicenciaJefaturaRH = publicWidget.Widget.extend({
    selector: '.portal_administrativo_gestion_licencias_accion_jefatura_RH_form',
    events: {
        'click #btn_aceptar_licencia': 'btnAceptarLicencia',
        'click #btn_rechazar_licencia': 'btnRechazarLicencia',
    },

    start: function () {
    },

    btnAceptarLicencia: function(){
        var vals ={
            'id_licencia': document.getElementById('id_licencia').innerHTML,
            'accion': "Aceptado",
        };
        ajax.jsonRpc('/set_proceso_accion_licencia_jefatura_RH', 'call', {
            valsJS: vals,
        }).then(function (result){

            if(result['result']){
                var contenedor = document.querySelector('#portal_administrativo_gestion_licencias_accion_jefatura_RH_container');

                var div_alert_alert_primary = document.createElement('div');
                div_alert_alert_primary.className = 'alert alert-primary';
                div_alert_alert_primary.appendChild(document.createTextNode('¡Información de solicitud enviada, muchas gracias!!!'));
                contenedor.innerHTML = '';
                contenedor.appendChild(div_alert_alert_primary);

                if(result['reporte']){
                    var URLactual = window.location.hostname
                    window.open('/create_report_accion_licencia?id_licencia='+result['id_licencia'], "_blank");
                }

            }
        });
    },
    btnRechazarLicencia: function(){
        var vals ={
            'id_licencia': document.getElementById('id_licencia').innerHTML,
            'accion': "Rechazado",
        };
        ajax.jsonRpc('/set_proceso_accion_licencia_jefatura_RH', 'call', {
            valsJS: vals,
        }).then(function (result){

            if(result['result']){
                var contenedor = document.querySelector('#portal_administrativo_gestion_licencias_accion_jefatura_RH_container');

                var div_alert_alert_primary = document.createElement('div');
                div_alert_alert_primary.className = 'alert alert-primary';
                div_alert_alert_primary.appendChild(document.createTextNode('¡Información de solicitud enviada, muchas gracias!!!'));
                contenedor.innerHTML = '';
                contenedor.appendChild(div_alert_alert_primary);
            }
        });
    },

});

publicWidget.registry.UIAPortalJustificacion = publicWidget.Widget.extend({
    selector: '.uia_porta_justificaciones_marca',
    events: {
        'click #btn_buscar_docente': 'btnBuscarDocente',
    },
    start: function () {
    },

    btnBuscarDocente: function() {
        try {
            ajax.jsonRpc('/get_docente_justificaciones_marca', 'call', {
                cedulaDocente: document.getElementById("cedulaDocente").value,
            }).then(function (result){
                
                var div_remove = document.getElementById('alert_docente_no_encontrado');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('alert_docente_no_encontrado');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('form_justificacion');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('form_cursos_justificacion');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('cursos_menu');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('cursos_list');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('alert_justificacion_aplicada');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                if(result['encontrado']){
                    var container = document.querySelector('#uia_porta_justificaciones_marca_container');

                    var form = document.createElement('form');
                    form.id = 'form_justificacion';

                    //#region Informacion Docente
                    var div_form_row_docente_info = document.createElement('div');
                    div_form_row_docente_info.className = 'form-row';

                    var div_form_group_col_md_6_docente_nombre = document.createElement('div');
                    div_form_group_col_md_6_docente_nombre.className = 'form-group col-md-6';
                    
                    var label_docente_nombre = document.createElement('label');   
                    label_docente_nombre.appendChild(document.createTextNode('Nombre del Docente'));

                    var input_docente_nombre = document.createElement('input');
                    input_docente_nombre.type = 'text';
                    input_docente_nombre.className = 'form-control';
                    input_docente_nombre.id = 'nombre_Docente';
                    input_docente_nombre.value = result['docenteNombre'];
                    input_docente_nombre.readOnly = true;

                    div_form_group_col_md_6_docente_nombre.appendChild(label_docente_nombre);
                    div_form_group_col_md_6_docente_nombre.appendChild(input_docente_nombre);

                    div_form_row_docente_info.appendChild(div_form_group_col_md_6_docente_nombre);
                    //#endregion

                    //#region Anno Curso Docente
                    var div_col_md_6_justificacion_marca_anoo = document.createElement('div');
                    div_col_md_6_justificacion_marca_anoo.className = 'col-md-6';

                    var label_form_label_justificacion_marca_anoo = document.createElement('label');
                    label_form_label_justificacion_marca_anoo.className = 'form-label';
                    label_form_label_justificacion_marca_anoo.appendChild(document.createTextNode('Año de curso'));

                    var input_date_justificacion_marca_anoo = document.createElement('input');
                    input_date_justificacion_marca_anoo.className = 'form-control';
                    input_date_justificacion_marca_anoo.id = 'dt_justificacion_marca_anno';
                    input_date_justificacion_marca_anoo.type = 'text';
                    input_date_justificacion_marca_anoo.value = new Date().getFullYear().toString();
                    input_date_justificacion_marca_anoo.readOnly = true;

                    div_col_md_6_justificacion_marca_anoo.appendChild(label_form_label_justificacion_marca_anoo);
                    div_col_md_6_justificacion_marca_anoo.appendChild(input_date_justificacion_marca_anoo);

                    div_form_row_docente_info.appendChild(div_col_md_6_justificacion_marca_anoo);
                    //#endregion
                    
                    //#region Cuatrimestre Curso Docente
                    var div_col_md_6_justificacion_marca_cuatrimestre = document.createElement('div');
                    div_col_md_6_justificacion_marca_cuatrimestre.className = 'col-md-6';

                    var label_form_label_justificacion_marca_cuatrimestre = document.createElement('label');
                    label_form_label_justificacion_marca_cuatrimestre.appendChild(document.createTextNode('Cuatrimestre'));
    
                    var select_beneficiario_justificacion_marca_cuatrimestre = document.createElement('select');
                    select_beneficiario_justificacion_marca_cuatrimestre.className = 'form-control';
                    select_beneficiario_justificacion_marca_cuatrimestre.id = 'slt_justificacion_marca_cuatrimestre';
                    var parentesco_list = ['1Q','2Q','3Q']
                    var parentesco_codigo_list = ['1Q','2Q','3Q']
                    for (var i = 0; i<=(parentesco_list.length-1); i++){
                        var opt = document.createElement('option');
                        opt.value = parentesco_codigo_list[i];
                        opt.innerHTML = parentesco_list[i];
                        select_beneficiario_justificacion_marca_cuatrimestre.appendChild(opt);
                    }

                    div_col_md_6_justificacion_marca_cuatrimestre.appendChild(label_form_label_justificacion_marca_cuatrimestre);
                    div_col_md_6_justificacion_marca_cuatrimestre.appendChild(select_beneficiario_justificacion_marca_cuatrimestre);

                    div_form_row_docente_info.appendChild(div_col_md_6_justificacion_marca_cuatrimestre);
                    //#endregion                    

                    //#region Fecha Curso Docente
                    var div_col_md_6_justificacion_marca = document.createElement('div');
                    div_col_md_6_justificacion_marca.className = 'col-md-6';

                    var label_form_label_justificacion_marca = document.createElement('label');
                    label_form_label_justificacion_marca.className = 'form-label';
                    label_form_label_justificacion_marca.appendChild(document.createTextNode('Fecha de curso'));

                    var input_date_justificacion_marca = document.createElement('input');
                    input_date_justificacion_marca.className = 'form-control';
                    input_date_justificacion_marca.id = 'dt_justificacion_marca';
                    input_date_justificacion_marca.type = 'date';
                    input_date_justificacion_marca.onchange = onChangeFechaJustificacionCurso;

                    div_col_md_6_justificacion_marca.appendChild(label_form_label_justificacion_marca);
                    div_col_md_6_justificacion_marca.appendChild(input_date_justificacion_marca);

                    div_form_row_docente_info.appendChild(div_col_md_6_justificacion_marca);
                    //#endregion

                    form.appendChild(div_form_row_docente_info)

                    container.appendChild(form);


                }else{
                    var alertPlaceholder = document.querySelector('#uia_porta_justificaciones_marca_container');
                    var div_alert = document.createElement('div');
                    div_alert.className = "alert alert-warning";
                    div_alert.id = 'alert_docente_no_encontrado'
                    div_alert.style.borderRadius = "5px";
                    div_alert.style.marginTop = "5px";
                    div_alert.appendChild(document.createTextNode('Docente no encontrado, por favor verifique el número de cédula'));
                    div_alert.style.fontSize = "15px";
                    div_alert.style.fontWeight = "900";
                    alertPlaceholder.appendChild(div_alert);
                }
            });
        } catch (err) {
        }
    },
});

function onChangeFechaJustificacionCurso(result){

    ajax.jsonRpc('/get_cursos_docente_justificaciones_marca', 'call', {
        fechaCurso : new Date(document.getElementById("dt_justificacion_marca").value),
        cedulaDocente : document.getElementById("cedulaDocente").value,
        anno : document.getElementById("dt_justificacion_marca_anno").value,
        periodo : document.getElementById("slt_justificacion_marca_cuatrimestre").value,
    }).then(function (result){
        pagoMarca = result['pagoMarca'];  
        var div_remove = document.getElementById('alert_curso_no_encontrado');
        if(div_remove != null){
            div_remove.parentElement.removeChild(div_remove);
        }
        var div_remove = document.getElementById('form_cursos_justificacion');
        if(div_remove != null){
            div_remove.parentElement.removeChild(div_remove);
        }
        var div_remove = document.getElementById('alert_justificacion_aplicada');
        if(div_remove != null){
            div_remove.parentElement.removeChild(div_remove);
        }
        if(result['encontrado'] && result['estadoFecha'] == "OK"){
            var container = document.querySelector('#uia_porta_justificaciones_marca_container');

            var form = document.createElement('form');
            form.id = 'form_cursos_justificacion';

            var fieldset_form_group = document.createElement('div');
            fieldset_form_group.className = 'form-group row';

            var div_col_sm_2_justificacion_marca_cursos = document.createElement('div');
            div_col_sm_2_justificacion_marca_cursos.className = 'col-sm-2';
            div_col_sm_2_justificacion_marca_cursos.id = 'cursos_menu';
            div_col_sm_2_justificacion_marca_cursos.appendChild(document.createTextNode('Cursos'));

            var div_col_sm_10_justificacion_marca_cursos = document.createElement('div');
            div_col_sm_10_justificacion_marca_cursos.className = 'col-sm-10';
            div_col_sm_10_justificacion_marca_cursos.id = 'cursos_list';

            result['listCursos'].forEach((item,idex,arr)=>{
                var div_form_checkustificacion_marca_cursos = document.createElement('div');
                div_form_checkustificacion_marca_cursos.className = 'form-check';

                var input_checkbox_curso = document.createElement('input');
                input_checkbox_curso.className = 'form-check-input';
                input_checkbox_curso.type = 'checkbox';
                input_checkbox_curso.id = 'chk'+ item['id'];
                input_checkbox_curso.name = 'chk';

                var label_checkbox_curso  = document.createElement('label');
                label_checkbox_curso.className = 'form-check-label';
                label_checkbox_curso.setAttribute('for','chk'+ item['id']);
                label_checkbox_curso.appendChild(document.createTextNode(item['codigoCurso']+' - '+item['horarioCurso']));

                div_form_checkustificacion_marca_cursos.appendChild(input_checkbox_curso);
                div_form_checkustificacion_marca_cursos.appendChild(label_checkbox_curso);

                div_col_sm_10_justificacion_marca_cursos.appendChild(div_form_checkustificacion_marca_cursos);
                
            });

            var btn_enviar_justificacion = document.createElement('button');
            btn_enviar_justificacion.type = "button";
            btn_enviar_justificacion.className = 'btn btn-primary';
            btn_enviar_justificacion.style.marginTop = '5px';
            btn_enviar_justificacion.appendChild(document.createTextNode('Enviar Justificación'));
            btn_enviar_justificacion.onclick = btnEnviarJustificacion;      


            form.appendChild(div_col_sm_2_justificacion_marca_cursos);
            form.appendChild(div_col_sm_10_justificacion_marca_cursos);
            form.appendChild(btn_enviar_justificacion);
            
            container.appendChild(form);

        

        }
        else if(result['encontrado'] && result['estadoFecha'] == "NOT"){

            var alertPlaceholder = document.querySelector('#uia_porta_justificaciones_marca_container');
            var div_alert = document.createElement('div');
            div_alert.className = "alert alert-warning";
            div_alert.id = 'alert_curso_no_encontrado'
            div_alert.style.borderRadius = "5px";
            div_alert.style.marginTop = "5px";
            div_alert.appendChild(document.createTextNode('La fecha indicada está fuera del rango de fechas para justificar este pago, el rango es' + result['rangoJustificacion']));
            div_alert.style.fontSize = "15px";
            div_alert.style.fontWeight = "900";
            alertPlaceholder.appendChild(div_alert);
        }
        else{
            var alertPlaceholder = document.querySelector('#uia_porta_justificaciones_marca_container');
            var div_alert = document.createElement('div');
            div_alert.className = "alert alert-warning";
            div_alert.id = 'alert_curso_no_encontrado'
            div_alert.style.borderRadius = "5px";
            div_alert.style.marginTop = "5px";
            div_alert.appendChild(document.createTextNode('No se encontraron cursos para la fecha especificada'));
            div_alert.style.fontSize = "15px";
            div_alert.style.fontWeight = "900";
            alertPlaceholder.appendChild(div_alert);
        }
    });

    
}
function btnEnviarJustificacion() {
    try {
        var chklist = document.getElementsByName("chk");
        let array = []
        chklist.forEach((item,idex,arr)=>{
            if(item.checked){
                array.push(parseInt(item.id.substring(3)));
            }
        });

        ajax.jsonRpc('/set_cursos_docente_justificaciones_marca', 'call', {
            cursosJustificacion : array,
            fechaCurso : new Date(document.getElementById("dt_justificacion_marca").value),
            pagoMarca: pagoMarca
        }).then(function (result){
            var div_remove = document.getElementById('alert_justificacion_aplicada');
            if(div_remove != null){
                div_remove.parentElement.removeChild(div_remove);
            }
            var alertPlaceholder = document.querySelector('#uia_porta_justificaciones_marca_container');
            var div_alert = document.createElement('div');
            div_alert.className = 'alert alert-success';
            div_alert.style.borderRadius = "5px";
            div_alert.style.marginTop = "5px";
            div_alert.id = 'alert_justificacion_aplicada'
            div_alert.appendChild(document.createTextNode(result['estado']));
            div_alert.style.fontSize = "15px";
            div_alert.style.fontWeight = "900";
            alertPlaceholder.appendChild(div_alert);
         });
    } catch (err) {
        alert(err);
    }
}

publicWidget.registry.UIAPortalAdicionales = publicWidget.Widget.extend({
    selector: '.uia_porta_cargar_adicionales',
    events: {
        'click #btn_buscar_docente': 'btnBuscarDocente',
    },
    start: function () {
    },

    btnBuscarDocente: function() {
        try {
            ajax.jsonRpc('/get_docente_carga_adicionales', 'call', {
                cedulaDocente: document.getElementById("cedulaDocente").value,
            }).then(function (result){
                
                var div_remove = document.getElementById('alert_docente_no_encontrado');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('alert_docente_no_encontrado');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('form_justificacion');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('form_cursos_justificacion');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('cursos_menu');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('cursos_list');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('alert_justificacion_aplicada');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                if(result['encontrado']){
                    var container = document.querySelector('#uia_porta_cargar_adicionales_container');

                    var form = document.createElement('form');
                    form.id = 'form_justificacion';

                    //#region Informacion Docente
                    var div_form_row_docente_info = document.createElement('div');
                    div_form_row_docente_info.className = 'form-row';

                    var div_form_group_col_md_6_docente_nombre = document.createElement('div');
                    div_form_group_col_md_6_docente_nombre.className = 'form-group col-md-6';
                    
                    var label_docente_nombre = document.createElement('label');   
                    label_docente_nombre.appendChild(document.createTextNode('Nombre del Docente'));

                    var input_docente_nombre = document.createElement('input');
                    input_docente_nombre.type = 'text';
                    input_docente_nombre.className = 'form-control';
                    input_docente_nombre.id = 'nombre_Docente';
                    input_docente_nombre.value = result['docenteNombre'];
                    input_docente_nombre.readOnly = true;

                    div_form_group_col_md_6_docente_nombre.appendChild(label_docente_nombre);
                    div_form_group_col_md_6_docente_nombre.appendChild(input_docente_nombre);

                    div_form_row_docente_info.appendChild(div_form_group_col_md_6_docente_nombre);
                    //#endregion

                    //#region Anno Adicional Docente
                    var div_col_md_6_carga_adicional_anoo = document.createElement('div');
                    div_col_md_6_carga_adicional_anoo.className = 'col-md-6';

                    var label_form_label_carga_adicional_anoo = document.createElement('label');
                    label_form_label_carga_adicional_anoo.className = 'form-label';
                    label_form_label_carga_adicional_anoo.appendChild(document.createTextNode('Año'));

                    var input_date_carga_adicional_anoo = document.createElement('input');
                    input_date_carga_adicional_anoo.className = 'form-control';
                    input_date_carga_adicional_anoo.id = 'dt_justificacion_marca_anno';
                    input_date_carga_adicional_anoo.type = 'text';
                    input_date_carga_adicional_anoo.value = new Date().getFullYear().toString();
                    input_date_carga_adicional_anoo.readOnly = true;

                    div_col_md_6_carga_adicional_anoo.appendChild(label_form_label_carga_adicional_anoo);
                    div_col_md_6_carga_adicional_anoo.appendChild(input_date_carga_adicional_anoo);

                    div_form_row_docente_info.appendChild(div_col_md_6_carga_adicional_anoo);
                    //#endregion
                    
                    //#region Cuatrimestre Curso Docente
                    var div_col_md_6_carga_adicional_periodo = document.createElement('div');
                    div_col_md_6_carga_adicional_periodo.className = 'col-md-6';

                    var label_form_label_carga_adicional_periodo = document.createElement('label');
                    label_form_label_carga_adicional_periodo.appendChild(document.createTextNode('Cuatrimestre'));
    
                    var select_carga_adicional_periodo= document.createElement('select');
                    select_carga_adicional_periodo.className = 'form-control';
                    select_carga_adicional_periodo.id = 'slt_carga_adicional_periodo';

                    var periodo_Value = ['1Q','2Q','3Q']
                    for (var i = 0; i<=(periodo_Value.length-1); i++){
                        var opt = document.createElement('option');
                        opt.value = periodo_Value[i];
                        opt.innerHTML = periodo_Value[i];
                        select_carga_adicional_periodo.appendChild(opt);
                    }

                    div_col_md_6_carga_adicional_periodo.appendChild(label_form_label_carga_adicional_periodo);
                    div_col_md_6_carga_adicional_periodo.appendChild(select_carga_adicional_periodo);

                    div_form_row_docente_info.appendChild(div_col_md_6_carga_adicional_periodo);
                    //#endregion  
                    
                    //#region Tipo Adicional Docente
                    var div_col_md_6_cargar_adicional_tipo = document.createElement('div');
                    div_col_md_6_cargar_adicional_tipo.className = 'col-md-6';

                    var label_form_label_cargar_adicional_tipo = document.createElement('label');
                    label_form_label_cargar_adicional_tipo.appendChild(document.createTextNode('Tipo Adicional'));
    
                    var select_beneficiario_cargar_adicional_tipo = document.createElement('select');
                    select_beneficiario_cargar_adicional_tipo.className = 'form-control';
                    select_beneficiario_cargar_adicional_tipo.id = 'slt_justificacion_marca_cuatrimestre';
                    
                    result['adicionalesList'].forEach((item,idex,arr)=>{
                        var opt = document.createElement('option');
                        opt.value = item['id'];
                        opt.innerHTML = item['nombre'];
                        select_beneficiario_cargar_adicional_tipo.appendChild(opt);
                    });
                    div_col_md_6_cargar_adicional_tipo.appendChild(label_form_label_cargar_adicional_tipo);
                    div_col_md_6_cargar_adicional_tipo.appendChild(select_beneficiario_cargar_adicional_tipo);

                    div_form_row_docente_info.appendChild(div_col_md_6_cargar_adicional_tipo);
                    //#endregion                    

                    //#region Fecha Curso Docente
                    var div_col_md_6_justificacion_marca = document.createElement('div');
                    div_col_md_6_justificacion_marca.className = 'col-md-6';

                    var label_form_label_justificacion_marca = document.createElement('label');
                    label_form_label_justificacion_marca.className = 'form-label';
                    label_form_label_justificacion_marca.appendChild(document.createTextNode('Fecha(Preguntar a Adrian)'));

                    var input_date_justificacion_marca = document.createElement('input');
                    input_date_justificacion_marca.className = 'form-control';
                    input_date_justificacion_marca.id = 'dt_cargar_adicional';
                    input_date_justificacion_marca.type = 'date';

                    div_col_md_6_justificacion_marca.appendChild(label_form_label_justificacion_marca);
                    div_col_md_6_justificacion_marca.appendChild(input_date_justificacion_marca);

                    div_form_row_docente_info.appendChild(div_col_md_6_justificacion_marca);
                    //#endregion
                    
                    //#region Cantidad Adicionales
                    var div_col_md_6_carga_adicional_cantidad = document.createElement('div');
                    div_col_md_6_carga_adicional_cantidad.className = 'col-md-6';

                    var label_form_label_carga_adicional_cantidad= document.createElement('label');
                    label_form_label_carga_adicional_cantidad.className = 'form-label';
                    label_form_label_carga_adicional_cantidad.appendChild(document.createTextNode('Cantidad'));

                    var input_date_carga_adicional_cantidad = document.createElement('input');
                    input_date_carga_adicional_cantidad.className = 'form-control';
                    input_date_carga_adicional_cantidad.id = 'cant_adicionales';
                    input_date_carga_adicional_cantidad.type = 'number';

                    div_col_md_6_carga_adicional_cantidad.appendChild(label_form_label_carga_adicional_cantidad);
                    div_col_md_6_carga_adicional_cantidad.appendChild(input_date_carga_adicional_cantidad);

                    div_form_row_docente_info.appendChild(div_col_md_6_carga_adicional_cantidad);
                    //#endregion

                    var btn_enviar_justificacion = document.createElement('button');
                    btn_enviar_justificacion.type = "button";
                    btn_enviar_justificacion.className = 'btn btn-primary';
                    btn_enviar_justificacion.style.marginTop = '5px';
                    btn_enviar_justificacion.appendChild(document.createTextNode('Cargar Adicional'));
                    btn_enviar_justificacion.onclick = btnCargarAdicionales;          
                    
                    form.appendChild(div_form_row_docente_info)
                    form.appendChild(btn_enviar_justificacion);
                    container.appendChild(form);

                }else{
                    var alertPlaceholder = document.querySelector('#uia_porta_justificaciones_marca_container');
                    var div_alert = document.createElement('div');
                    div_alert.className = "alert alert-warning";
                    div_alert.id = 'alert_docente_no_encontrado'
                    div_alert.style.borderRadius = "5px";
                    div_alert.style.marginTop = "5px";
                    div_alert.appendChild(document.createTextNode('Docente no encontrado, por favor verifique el número de cédula'));
                    div_alert.style.fontSize = "15px";
                    div_alert.style.fontWeight = "900";
                    alertPlaceholder.appendChild(div_alert);
                }
            });
        } catch (err) {
        }
    },
});
function onChangeFechaJustificacionCurso(result){

    ajax.jsonRpc('/get_cursos_docente_justificaciones_marca', 'call', {
        fechaCurso : new Date(document.getElementById("dt_justificacion_marca").value),
        cedulaDocente : document.getElementById("cedulaDocente").value,
        anno : document.getElementById("dt_justificacion_marca_anno").value,
        periodo : document.getElementById("slt_justificacion_marca_cuatrimestre").value,
    }).then(function (result){
        pagoMarca = result['pagoMarca'];  
        var div_remove = document.getElementById('alert_curso_no_encontrado');
        if(div_remove != null){
            div_remove.parentElement.removeChild(div_remove);
        }
        var div_remove = document.getElementById('form_cursos_justificacion');
        if(div_remove != null){
            div_remove.parentElement.removeChild(div_remove);
        }
        var div_remove = document.getElementById('alert_justificacion_aplicada');
        if(div_remove != null){
            div_remove.parentElement.removeChild(div_remove);
        }
        if(result['encontrado'] && result['estadoFecha'] == "OK"){
            var container = document.querySelector('#uia_porta_justificaciones_marca_container');

            var form = document.createElement('form');
            form.id = 'form_cursos_justificacion';

            var fieldset_form_group = document.createElement('div');
            fieldset_form_group.className = 'form-group row';

            var div_col_sm_2_justificacion_marca_cursos = document.createElement('div');
            div_col_sm_2_justificacion_marca_cursos.className = 'col-sm-2';
            div_col_sm_2_justificacion_marca_cursos.id = 'cursos_menu';
            div_col_sm_2_justificacion_marca_cursos.appendChild(document.createTextNode('Cursos'));

            var div_col_sm_10_justificacion_marca_cursos = document.createElement('div');
            div_col_sm_10_justificacion_marca_cursos.className = 'col-sm-10';
            div_col_sm_10_justificacion_marca_cursos.id = 'cursos_list';

            result['listCursos'].forEach((item,idex,arr)=>{
                var div_form_checkustificacion_marca_cursos = document.createElement('div');
                div_form_checkustificacion_marca_cursos.className = 'form-check';

                var input_checkbox_curso = document.createElement('input');
                input_checkbox_curso.className = 'form-check-input';
                input_checkbox_curso.type = 'checkbox';
                input_checkbox_curso.id = 'chk'+ item['id'];
                input_checkbox_curso.name = 'chk';

                var label_checkbox_curso  = document.createElement('label');
                label_checkbox_curso.className = 'form-check-label';
                label_checkbox_curso.setAttribute('for','chk'+ item['id']);
                label_checkbox_curso.appendChild(document.createTextNode(item['codigoCurso']+' - '+item['horarioCurso']));

                div_form_checkustificacion_marca_cursos.appendChild(input_checkbox_curso);
                div_form_checkustificacion_marca_cursos.appendChild(label_checkbox_curso);

                div_col_sm_10_justificacion_marca_cursos.appendChild(div_form_checkustificacion_marca_cursos);
                
            });

            var btn_enviar_justificacion = document.createElement('button');
            btn_enviar_justificacion.type = "button";
            btn_enviar_justificacion.className = 'btn btn-primary';
            btn_enviar_justificacion.style.marginTop = '5px';
            btn_enviar_justificacion.appendChild(document.createTextNode('Enviar Justificación'));
            btn_enviar_justificacion.onclick = btnEnviarJustificacion;      


            form.appendChild(div_col_sm_2_justificacion_marca_cursos);
            form.appendChild(div_col_sm_10_justificacion_marca_cursos);
            form.appendChild(btn_enviar_justificacion);
            
            container.appendChild(form);


        }
        else if(result['encontrado'] && result['estadoFecha'] == "NOT"){

            var alertPlaceholder = document.querySelector('#uia_porta_justificaciones_marca_container');
            var div_alert = document.createElement('div');
            div_alert.className = "alert alert-warning";
            div_alert.id = 'alert_curso_no_encontrado'
            div_alert.style.borderRadius = "5px";
            div_alert.style.marginTop = "5px";
            div_alert.appendChild(document.createTextNode('La fecha indicada está fuera del rango de fechas para justificar este pago, el rango es' + result['rangoJustificacion']));
            div_alert.style.fontSize = "15px";
            div_alert.style.fontWeight = "900";
            alertPlaceholder.appendChild(div_alert);
        }
        else{
            var alertPlaceholder = document.querySelector('#uia_porta_justificaciones_marca_container');
            var div_alert = document.createElement('div');
            div_alert.className = "alert alert-warning";
            div_alert.id = 'alert_curso_no_encontrado'
            div_alert.style.borderRadius = "5px";
            div_alert.style.marginTop = "5px";
            div_alert.appendChild(document.createTextNode('No se encontraron cursos para la fecha especificada'));
            div_alert.style.fontSize = "15px";
            div_alert.style.fontWeight = "900";
            alertPlaceholder.appendChild(div_alert);
        }
    });

    
}
function btnCargarAdicionales() {
    try {
        if(verificacionAdicionales()){        
            ajax.jsonRpc('/set_cargar_adicional', 'call', {
                fechaAdicional : new Date(document.getElementById("dt_cargar_adicional").value),
                identificacionDocente: document.getElementById('cedulaDocente').value,
                tipoAdicional: document.getElementById('slt_justificacion_marca_cuatrimestre').value,
                cantidad: document.getElementById('cant_adicionales').value,
                periodo: document.getElementById('slt_carga_adicional_periodo').value,
                anno: document.getElementById('dt_justificacion_marca_anno').value,
            }).then(function (result){
                var div_remove = document.getElementById('alert_cargar_adicional');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                showMensajeAdicionales(result['estado'],"alert alert-success")
             });
        }
        
    } catch (err) {
        alert(err);
    }
}
function showMensajeAdicionales(Text,typeAlert){
    var div_remove = document.getElementById('alert_cargar_adicional');
    if(div_remove != null){
        div_remove.parentElement.removeChild(div_remove);
    }
    var alertPlaceholder = document.querySelector('#uia_porta_cargar_adicionales_container');
    var div_alert = document.createElement('div');
    div_alert.className = typeAlert;
    div_alert.style.borderRadius = "5px";
    div_alert.style.marginTop = "5px";
    div_alert.id = 'alert_cargar_adicional'
    div_alert.appendChild(document.createTextNode(Text));
    div_alert.style.fontSize = "15px";
    div_alert.style.fontWeight = "900";
    alertPlaceholder.appendChild(div_alert);
}
function verificacionAdicionales(){

    var verificacion = true;

    if(!document.getElementById('cant_adicionales').value || parseInt(document.getElementById('cant_adicionales').value) <= 0){

        verificacion = false
        verificacionAdicionales('Casilla Cantidad en blanco o Cantidad igual o meno a 0 ',"alert alert-warning")
        document.getElementById("cant_adicionales").style.borderColor = "red";

    }else{

        document.getElementById("cant_adicionales").style.borderColor = "white";

    }
    if(!document.getElementById("dt_cargar_adicional").value){

        verificacion = false
        verificacionAdicionales('Fecha Invalida',"alert alert-warning")
        document.getElementById("dt_cargar_adicional").style.borderColor = "red";

    }else{

        document.getElementById("dt_cargar_adicional").style.borderColor = "white";

    }
    return verificacion;
}

publicWidget.registry.UIAPortalAjustesPago= publicWidget.Widget.extend({
    selector: '.uia_porta_cargar_ajustes_pago',
    events: {
        'click #btn_buscar_docente': 'btnBuscarDocente',
    },
    start: function () {
    },

    btnBuscarDocente: function() {
        try {
            ajax.jsonRpc('/get_docente_carga_ajustes_pago', 'call', {
                cedulaDocente: document.getElementById("cedulaDocente").value,
            }).then(function (result){
                
                var div_remove = document.getElementById('alert_docente_no_encontrado');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('alert_docente_no_encontrado');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('form_justificacion');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('form_cursos_justificacion');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('cursos_menu');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('cursos_list');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                var div_remove = document.getElementById('alert_justificacion_aplicada');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                if(result['encontrado']){
                    var container = document.querySelector('#uia_porta_cargar_ajustes_pago_container');

                    var form = document.createElement('form');
                    form.id = 'form_justificacion';

                    //#region Informacion Docente
                    var div_form_row_docente_info = document.createElement('div');
                    div_form_row_docente_info.className = 'form-row';

                    var div_form_group_col_md_6_docente_nombre = document.createElement('div');
                    div_form_group_col_md_6_docente_nombre.className = 'form-group col-md-6';
                    
                    var label_docente_nombre = document.createElement('label');   
                    label_docente_nombre.appendChild(document.createTextNode('Nombre del Docente'));

                    var input_docente_nombre = document.createElement('input');
                    input_docente_nombre.type = 'text';
                    input_docente_nombre.className = 'form-control';
                    input_docente_nombre.id = 'nombre_Docente';
                    input_docente_nombre.value = result['docenteNombre'];
                    input_docente_nombre.readOnly = true;

                    div_form_group_col_md_6_docente_nombre.appendChild(label_docente_nombre);
                    div_form_group_col_md_6_docente_nombre.appendChild(input_docente_nombre);

                    div_form_row_docente_info.appendChild(div_form_group_col_md_6_docente_nombre);
                    //#endregion

                    //#region Anno Adicional Docente
                    var div_col_md_6_carga_adicional_anoo = document.createElement('div');
                    div_col_md_6_carga_adicional_anoo.className = 'col-md-6';

                    var label_form_label_carga_adicional_anoo = document.createElement('label');
                    label_form_label_carga_adicional_anoo.className = 'form-label';
                    label_form_label_carga_adicional_anoo.appendChild(document.createTextNode('Año'));

                    var input_date_carga_adicional_anoo = document.createElement('input');
                    input_date_carga_adicional_anoo.className = 'form-control';
                    input_date_carga_adicional_anoo.id = 'dt_justificacion_marca_anno';
                    input_date_carga_adicional_anoo.type = 'text';
                    input_date_carga_adicional_anoo.value = new Date().getFullYear().toString();
                    input_date_carga_adicional_anoo.readOnly = true;

                    div_col_md_6_carga_adicional_anoo.appendChild(label_form_label_carga_adicional_anoo);
                    div_col_md_6_carga_adicional_anoo.appendChild(input_date_carga_adicional_anoo);

                    div_form_row_docente_info.appendChild(div_col_md_6_carga_adicional_anoo);
                    //#endregion
                    
                    //#region Cuatrimestre Curso Docente
                    var div_col_md_6_carga_adicional_periodo = document.createElement('div');
                    div_col_md_6_carga_adicional_periodo.className = 'col-md-6';

                    var label_form_label_carga_adicional_periodo = document.createElement('label');
                    label_form_label_carga_adicional_periodo.appendChild(document.createTextNode('Cuatrimestre'));
    
                    var select_carga_adicional_periodo= document.createElement('select');
                    select_carga_adicional_periodo.className = 'form-control';
                    select_carga_adicional_periodo.id = 'slt_carga_adicional_periodo';

                    var periodo_Value = ['1Q','2Q','3Q']
                    for (var i = 0; i<=(periodo_Value.length-1); i++){
                        var opt = document.createElement('option');
                        opt.value = periodo_Value[i];
                        opt.innerHTML = periodo_Value[i];
                        select_carga_adicional_periodo.appendChild(opt);
                    }

                    div_col_md_6_carga_adicional_periodo.appendChild(label_form_label_carga_adicional_periodo);
                    div_col_md_6_carga_adicional_periodo.appendChild(select_carga_adicional_periodo);

                    div_form_row_docente_info.appendChild(div_col_md_6_carga_adicional_periodo);
                    //#endregion  
                    
                    //#region Tipo Adicional Docente
                    var div_col_md_6_cargar_adicional_tipo = document.createElement('div');
                    div_col_md_6_cargar_adicional_tipo.className = 'col-md-6';

                    var label_form_label_cargar_adicional_tipo = document.createElement('label');
                    label_form_label_cargar_adicional_tipo.appendChild(document.createTextNode('Tipo de Ajuste'));
    
                    var select_beneficiario_cargar_adicional_tipo = document.createElement('select');
                    select_beneficiario_cargar_adicional_tipo.className = 'form-control';
                    select_beneficiario_cargar_adicional_tipo.id = 'slt_justificacion_marca_cuatrimestre';
                    
                    result['adicionalesList'].forEach((item,idex,arr)=>{
                        var opt = document.createElement('option');
                        opt.value = item['id'];
                        opt.innerHTML = item['nombre'];
                        select_beneficiario_cargar_adicional_tipo.appendChild(opt);
                    });
                    div_col_md_6_cargar_adicional_tipo.appendChild(label_form_label_cargar_adicional_tipo);
                    div_col_md_6_cargar_adicional_tipo.appendChild(select_beneficiario_cargar_adicional_tipo);

                    div_form_row_docente_info.appendChild(div_col_md_6_cargar_adicional_tipo);
                    //#endregion                    

                    //#region Fecha Curso Docente
                    var div_col_md_6_justificacion_marca = document.createElement('div');
                    div_col_md_6_justificacion_marca.className = 'col-md-6';

                    var label_form_label_justificacion_marca = document.createElement('label');
                    label_form_label_justificacion_marca.className = 'form-label';
                    label_form_label_justificacion_marca.appendChild(document.createTextNode('Fecha(Preguntar a Adrian)'));

                    var input_date_justificacion_marca = document.createElement('input');
                    input_date_justificacion_marca.className = 'form-control';
                    input_date_justificacion_marca.id = 'dt_cargar_adicional';
                    input_date_justificacion_marca.type = 'date';

                    div_col_md_6_justificacion_marca.appendChild(label_form_label_justificacion_marca);
                    div_col_md_6_justificacion_marca.appendChild(input_date_justificacion_marca);

                    div_form_row_docente_info.appendChild(div_col_md_6_justificacion_marca);
                    //#endregion

                    //#region Cantidad Adicionales
                    var div_col_md_6_carga_adicional_cantidad = document.createElement('div');
                    div_col_md_6_carga_adicional_cantidad.className = 'col-md-6';

                    var label_form_label_carga_adicional_cantidad= document.createElement('label');
                    label_form_label_carga_adicional_cantidad.className = 'form-label';
                    label_form_label_carga_adicional_cantidad.appendChild(document.createTextNode('Monto'));

                    var input_date_carga_adicional_cantidad = document.createElement('input');
                    input_date_carga_adicional_cantidad.className = 'form-control';
                    input_date_carga_adicional_cantidad.id = 'cant_adicionales';
                    input_date_carga_adicional_cantidad.type = 'number';

                    div_col_md_6_carga_adicional_cantidad.appendChild(label_form_label_carga_adicional_cantidad);
                    div_col_md_6_carga_adicional_cantidad.appendChild(input_date_carga_adicional_cantidad);

                    div_form_row_docente_info.appendChild(div_col_md_6_carga_adicional_cantidad);
                    //#endregion

                    //#region Descripción  Adicionales
                    var form_group_carga_adicional_descripción = document.createElement('div');
                    form_group_carga_adicional_descripción.className = 'form-group';

                    var label_form_label_carga_adicional_descripcion= document.createElement('label');
                    label_form_label_carga_adicional_descripcion.className = 'form-label';
                    label_form_label_carga_adicional_descripcion.appendChild(document.createTextNode('Descripción'));

                    var textarea_form_control_descripcion = document.createElement('textarea');
                    textarea_form_control_descripcion.id = 'txt_descripcion';
                    textarea_form_control_descripcion.className = 'form-control';
                    textarea_form_control_descripcion.rows = 2;

                    form_group_carga_adicional_descripción.appendChild(label_form_label_carga_adicional_descripcion);
                    form_group_carga_adicional_descripción.appendChild(textarea_form_control_descripcion);

                    //#endregion

                    var btn_enviar_justificacion = document.createElement('button');
                    btn_enviar_justificacion.type = "button";
                    btn_enviar_justificacion.className = 'btn btn-primary';
                    btn_enviar_justificacion.style.marginTop = '5px';
                    btn_enviar_justificacion.appendChild(document.createTextNode('Cargar Ajuste'));
                    btn_enviar_justificacion.onclick = btnCargarAjustes;          
                    
                    form.appendChild(div_form_row_docente_info)
                    form.appendChild(form_group_carga_adicional_descripción)
                    form.appendChild(btn_enviar_justificacion);
                    container.appendChild(form);

                }else{
                    var alertPlaceholder = document.querySelector('#uia_porta_cargar_ajustes_pago_container');
                    var div_alert = document.createElement('div');
                    div_alert.className = "alert alert-warning";
                    div_alert.id = 'alert_docente_no_encontrado'
                    div_alert.style.borderRadius = "5px";
                    div_alert.style.marginTop = "5px";
                    div_alert.appendChild(document.createTextNode('Docente no encontrado, por favor verifique el número de cédula'));
                    div_alert.style.fontSize = "15px";
                    div_alert.style.fontWeight = "900";
                    alertPlaceholder.appendChild(div_alert);
                }
            });
        } catch (err) {
        }
    },
});
function btnCargarAjustes() {
    try {
        if(verificacionAjustes()){
            ajax.jsonRpc('/set_cargar_ajustes_pago', 'call', {
                fechaAdicional : new Date(document.getElementById("dt_cargar_adicional").value),
                identificacionDocente: document.getElementById('cedulaDocente').value,
                tipoAdicional: document.getElementById('slt_justificacion_marca_cuatrimestre').value,
                monto: document.getElementById('cant_adicionales').value,
                periodo: document.getElementById('slt_carga_adicional_periodo').value,
                anno: document.getElementById('dt_justificacion_marca_anno').value,
                descripcion: document.getElementById('txt_descripcion').value,
            }).then(function (result){
                var div_remove = document.getElementById('alert_cargar_adicional');
                if(div_remove != null){
                    div_remove.parentElement.removeChild(div_remove);
                }
                showMensajeAjustes(result['estado'],"alert alert-success")
             });
        }
        
    } catch (err) {
        alert(err);
    }
}
function showMensajeAjustes(Text,typeAlert){
    var div_remove = document.getElementById('alert_cargar_adicional');
    if(div_remove != null){
        div_remove.parentElement.removeChild(div_remove);
    }
    var alertPlaceholder = document.querySelector('#uia_porta_cargar_ajustes_pago_container');
    var div_alert = document.createElement('div');
    div_alert.className = typeAlert;
    div_alert.style.borderRadius = "5px";
    div_alert.style.marginTop = "5px";
    div_alert.id = 'alert_cargar_adicional'
    div_alert.appendChild(document.createTextNode(Text));
    div_alert.style.fontSize = "15px";
    div_alert.style.fontWeight = "900";
    alertPlaceholder.appendChild(div_alert);
}
function verificacionAjustes(){

    var verificacion = true;

    if(!document.getElementById('cant_adicionales').value || parseInt(document.getElementById('cant_adicionales').value) <= 0){

        verificacion = false
        showMensajeAjustes('Casilla monto en blanco o Cantidad igual o meno a 0 ',"alert alert-warning")
        document.getElementById("cant_adicionales").style.borderColor = "red";

    }else{

        document.getElementById("cant_adicionales").style.borderColor = "white";

    }
    if(!document.getElementById("dt_cargar_adicional").value){

        verificacion = false
        showMensajeAjustes('Fecha Invalida',"alert alert-warning")
        document.getElementById("dt_cargar_adicional").style.borderColor = "red";

    }else{

        document.getElementById("dt_cargar_adicional").style.borderColor = "white";

    }
    return verificacion;
}

});