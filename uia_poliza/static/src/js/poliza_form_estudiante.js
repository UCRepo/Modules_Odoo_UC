odoo.define('uia_poliza.poliza_form_estudiante', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    const Dialog = require('web.Dialog');
    const {_t, qweb} = require('web.core');
    const ajax = require('web.ajax');
    var rpc = require('web.rpc');

    publicWidget.registry.UIAPolizaFormEstudiante= publicWidget.Widget.extend({
        selector: '.uia_poliza_estudiante_form',
    
        start: function () {
            this._updateForm();
        },
        async _updateForm(elem) {
            var contenedor = document.querySelector('#uia_poliza_estudiante_form_div');

            if(document.getElementById('uia_poliza_datosActualizados').innerHTML == 'False'){       
                var form = document.createElement('form');

                //#region Informacion Estudiante
                var div_form_row_estudiante_info = document.createElement('div');
                div_form_row_estudiante_info.className = 'form-row';
                
                var div_form_group_col_md_6_estudiante_identificacion = document.createElement('div');
                div_form_group_col_md_6_estudiante_identificacion.className = 'form-group col-md-6';

                var label_estudiante_identificacion = document.createElement('label');
                label_estudiante_identificacion.appendChild(document.createTextNode('Identificación del Estudiante'));

                var input_estudiante_identificacion = document.createElement('input');
                input_estudiante_identificacion.type = 'text';
                input_estudiante_identificacion.className = 'form-control';
                input_estudiante_identificacion.id = 'id_Estudiante';
                input_estudiante_identificacion.value = document.getElementById('uia_poliza_identificaion_estudiante').innerHTML;
                input_estudiante_identificacion.readOnly = true;

                div_form_group_col_md_6_estudiante_identificacion.appendChild(label_estudiante_identificacion);
                div_form_group_col_md_6_estudiante_identificacion.appendChild(input_estudiante_identificacion);

                    

                var div_form_group_col_md_6_estudiante_nombre = document.createElement('div');
                div_form_group_col_md_6_estudiante_nombre.className = 'form-group col-md-6';
                
                var label_estudiante_nombre = document.createElement('label');   
                label_estudiante_nombre.appendChild(document.createTextNode('Nombre del Estudiante'));

                var input_estudiante_nombre = document.createElement('input');
                input_estudiante_nombre.type = 'text';
                input_estudiante_nombre.className = 'form-control';
                input_estudiante_nombre.id = 'nombre_Estudiante';
                input_estudiante_nombre.value = document.getElementById('uia_poliza_nombreEstudiante').innerHTML;
                input_estudiante_nombre.readOnly = true;

                div_form_group_col_md_6_estudiante_nombre.appendChild(label_estudiante_nombre);
                div_form_group_col_md_6_estudiante_nombre.appendChild(input_estudiante_nombre);

                div_form_row_estudiante_info.appendChild(div_form_group_col_md_6_estudiante_identificacion);
                div_form_row_estudiante_info.appendChild(div_form_group_col_md_6_estudiante_nombre);
                
                //#endregion

                //#region Informacion Beneficiario
                var div_form_group_tipo_identificacion = document.createElement('div');
                div_form_group_tipo_identificacion.className = 'form-group';

                var label_select_tipo_identificacion = document.createElement('label');
                label_select_tipo_identificacion.appendChild(document.createTextNode('*Tipo Identificación de Beneficiario'));

                var select_tipo_identificacion = document.createElement('select');
                select_tipo_identificacion.id = 'tipo_identificacion';
                select_tipo_identificacion.className = 'form-control';
                select_tipo_identificacion.onchange = onchangeTipoIdentificacion;
                var listTipoIdentificacion = ['Física','Jurídica','DIMEX','NITE','Otro']
                var listTipoIdentificacionValue = ['Cédula Física Nacional','Cédula Jurídica','Cédula Física Residente','Residente Rentistae','Identificación extranjero']
                for (var i = 0; i<=4; i++){
                    var opt = document.createElement('option');
                    opt.value = listTipoIdentificacionValue[i];
                    opt.innerHTML = listTipoIdentificacion[i];
                    select_tipo_identificacion.appendChild(opt);
                }

                div_form_group_tipo_identificacion.appendChild(label_select_tipo_identificacion);
                div_form_group_tipo_identificacion.appendChild(select_tipo_identificacion);

                var div_form_row_beneficiario_info = document.createElement('div');
                div_form_row_beneficiario_info.className = 'form-row';

                var div_form_group_col_md_6_beneficiario_identificacion = document.createElement('div');
                div_form_group_col_md_6_beneficiario_identificacion.className = 'form-group col-md-6';

                var label_beneficiario_identificacion = document.createElement('label');
                label_beneficiario_identificacion.appendChild(document.createTextNode('*Identificación de Beneficiario(Sin Guiones)'));

                var input_beneficiario_identificacion = document.createElement('input');
                input_beneficiario_identificacion.type = 'text';
                input_beneficiario_identificacion.className = 'form-control';
                input_beneficiario_identificacion.id = 'id_beneficiario';
                input_beneficiario_identificacion.onkeyup = onChangeIdentificaicon;

                div_form_group_col_md_6_beneficiario_identificacion.appendChild(label_beneficiario_identificacion);
                div_form_group_col_md_6_beneficiario_identificacion.appendChild(input_beneficiario_identificacion);

                var div_form_group_col_md_6_beneficiario_nombre = document.createElement('div');
                div_form_group_col_md_6_beneficiario_nombre.className = 'form-group col-md-6';
                
                var label_beneficiario_nombre = document.createElement('label');   
                label_beneficiario_nombre.appendChild(document.createTextNode('*Nombre de Beneficiario'));

                var input_beneficiario_nombre = document.createElement('input');
                input_beneficiario_nombre.type = 'text';
                input_beneficiario_nombre.className = 'form-control';
                input_beneficiario_nombre.id = 'nombre_beneficiario';
                input_beneficiario_nombre.readOnly = true;

                div_form_group_col_md_6_beneficiario_nombre.appendChild(label_beneficiario_nombre);
                div_form_group_col_md_6_beneficiario_nombre.appendChild(input_beneficiario_nombre);

                div_form_row_beneficiario_info.appendChild(div_form_group_col_md_6_beneficiario_identificacion);
                div_form_row_beneficiario_info.appendChild(div_form_group_col_md_6_beneficiario_nombre);

                var div_form_row_beneficiario_PTC = document.createElement('div');
                div_form_row_beneficiario_PTC.className = 'form-row';

                var div_form_group_col_md_4_Parentesco = document.createElement('div');
                div_form_group_col_md_4_Parentesco.className = 'form-group col-md-4';

                var label_beneficiario_Parentesco = document.createElement('label');
                label_beneficiario_Parentesco.appendChild(document.createTextNode('*Parentesco'));

                var select_beneficiario_Parentesco= document.createElement('select');
                select_beneficiario_Parentesco.className = 'form-control';
                select_beneficiario_Parentesco.id = 'parentesco_beneficiario';
                var parentesco_list = ['Cónyuge','Hijos','Madre','Padre','Hermanos','Patrono','Otro']
                var parentesco_codigo_list = ['Cónyuge','Hijos','Madre','Padre','Hermanos','Patrono','Otro']//['020','030','040','050','060','070','999']
                for (var i = 0; i<=(parentesco_list.length-1); i++){
                    var opt = document.createElement('option');
                    opt.value = parentesco_codigo_list[i];
                    opt.innerHTML = parentesco_list[i];
                    select_beneficiario_Parentesco.appendChild(opt);
                }

                div_form_group_col_md_4_Parentesco.appendChild(label_beneficiario_Parentesco);
                div_form_group_col_md_4_Parentesco.appendChild(select_beneficiario_Parentesco);

                var div_form_group_col_md_4_Telefono= document.createElement('div');
                div_form_group_col_md_4_Telefono.className = 'form-group col-md-4';
                
                var label_beneficiario_Telefono = document.createElement('label');
                label_beneficiario_Telefono.appendChild(document.createTextNode('Teléfono(Sin Guiones)'));

                var input_beneficiario_Telefono = document.createElement('input');
                input_beneficiario_Telefono.type = 'text';
                input_beneficiario_Telefono.className = 'form-control';
                input_beneficiario_Telefono.id = 'telefono_beneficiario';

                div_form_group_col_md_4_Telefono.appendChild(label_beneficiario_Telefono);
                div_form_group_col_md_4_Telefono.appendChild(input_beneficiario_Telefono);

                var div_form_group_col_md_4_Correo = document.createElement('div');
                div_form_group_col_md_4_Correo.className = 'form-group col-md-4';

                var label_beneficiario_Correo = document.createElement('label');
                label_beneficiario_Correo.appendChild(document.createTextNode('Correo'));

                var input_beneficiario_Correo = document.createElement('input');
                input_beneficiario_Correo.type = 'text';
                input_beneficiario_Correo.className = 'form-control';
                input_beneficiario_Correo.id = 'correo_beneficiario';

                div_form_group_col_md_4_Correo.appendChild(label_beneficiario_Correo);
                div_form_group_col_md_4_Correo.appendChild(input_beneficiario_Correo);

                div_form_row_beneficiario_PTC.appendChild(div_form_group_col_md_4_Parentesco);
                div_form_row_beneficiario_PTC.appendChild(div_form_group_col_md_4_Telefono);
                div_form_row_beneficiario_PTC.appendChild(div_form_group_col_md_4_Correo);

                //#endregion

                //#region 
                var btn_ingresar_datos_poliza = document.createElement('button');
                btn_ingresar_datos_poliza.className = 'btn btn-primary';
                btn_ingresar_datos_poliza.type = "button";
                btn_ingresar_datos_poliza.style.marginBottom = '2px';
                btn_ingresar_datos_poliza.appendChild(document.createTextNode('Aceptar'));
                btn_ingresar_datos_poliza.onclick = btnIngresarPoliza;
                //#endregion
                var div_mensages_error = document.createElement('div');
                div_mensages_error.className = 'form-group';
                div_mensages_error.id = 'div_mensages_error';
                form.appendChild(div_form_row_estudiante_info)
                form.appendChild(div_form_group_tipo_identificacion)
                form.appendChild(div_form_row_beneficiario_info)
                form.appendChild(div_form_row_beneficiario_PTC)
                form.appendChild(btn_ingresar_datos_poliza)
                form.appendChild(div_mensages_error)
                

                contenedor.appendChild(form);
            }
            else{

                var div_alert_alert_primary = document.createElement('div');
                div_alert_alert_primary.className = 'alert alert-primary';
                div_alert_alert_primary.appendChild(document.createTextNode('Información de Beneficiario Actualizada Muchas Gracias!!!'));

                contenedor.innerHTML = '';
                contenedor.appendChild(div_alert_alert_primary);
            }
        },
    
    });
    function onChangeIdentificaicon(result){
        var identificacion = document.getElementById('id_beneficiario').value;
        const sel = document.getElementById("tipo_identificacion");
        const tipoIdentificacion = sel.options[sel.selectedIndex].text;

        var xhr = new XMLHttpRequest();
        xhr.onload = success;
        xhr.onerror = error;

        if(tipoIdentificacion != 'Otro'){

            if(identificacion.length == 9 && tipoIdentificacion == 'Física'){
                xhr.open('GET', 'https://apis.gometa.org/cedulas/'+identificacion,true);
                xhr.send();
            }
            else if(identificacion.length == 10 && tipoIdentificacion == 'Jurídica' || tipoIdentificacion == 'NITE' ){
                xhr.open('GET', 'https://apis.gometa.org/cedulas/'+identificacion,true);
                xhr.send();
            }
            else if(identificacion.length >= 11 && tipoIdentificacion == 'DIMEX'){
                xhr.open('GET', 'https://apis.gometa.org/cedulas/'+identificacion,true);
                xhr.send();
            }

        }
        
    }

    function onchangeTipoIdentificacion(){
        document.getElementById('id_beneficiario').value = "";
        document.getElementById('nombre_beneficiario').value = "";
        const sel = document.getElementById("tipo_identificacion");
        const tipoIdentificacion = sel.options[sel.selectedIndex].text;
        if(tipoIdentificacion == 'Otro'){
            document.getElementById('nombre_beneficiario').readOnly = false
        }
        else
        {
            document.getElementById('nombre_beneficiario').readOnly = true
        }
    }

    function btnIngresarPoliza(){

        if (verificarInputs()){
            const sel = document.getElementById("tipo_identificacion");
            const tipoIdentificacion = sel.options[sel.selectedIndex].text;
            var vals = {
                'idPoliza': document.getElementById('uia_poliza_id').innerHTML,
                'idEstudiante': document.getElementById('uia_poliza_identificaion_estudiante').innerHTML,
                'nombreEstudiante': document.getElementById('uia_poliza_nombreEstudiante').innerHTML,
                'tipoIdentificacion': document.getElementById('tipo_identificacion').value,
                'identificacionBeneficiario': document.getElementById('id_beneficiario').value,
                'nombreBeneficiario': document.getElementById('nombre_beneficiario').value,
                'parentescoBeneficiario': document.getElementById('parentesco_beneficiario').value,
                'telefonoBeneficiario': document.getElementById('telefono_beneficiario').value,
                'correoBeneficiario': document.getElementById('correo_beneficiario').value,
            };
            ajax.jsonRpc('/set_informacion_beneficiario', 'call', {
                vals: vals,
            }).then(function (result){
    
                if(result['result'] == true){
                    var contenedor = document.querySelector('#uia_poliza_estudiante_form_div');
    
                    var div_alert_alert_primary = document.createElement('div');
                    div_alert_alert_primary.className = 'alert alert-primary';
                    div_alert_alert_primary.appendChild(document.createTextNode('Información de Beneficiario Actualizada Muchas Gracias!!!'));
    
                    contenedor.innerHTML = '';
                    contenedor.appendChild(div_alert_alert_primary);
                }
            });
        }
    }
    function verificarInputs(){
        var result = true;
        var contenedor = document.querySelector('#div_mensages_error');
        contenedor.innerHTML = "";
     if( document.getElementById('nombre_beneficiario').value.length <= 0){
        
        document.getElementById('nombre_beneficiario').style.border = "1px solid red";

        var div_error = document.createElement('div');
        div_error.className = 'alert alert-danger';
        div_error.appendChild(document.createTextNode('Falta el nombre del beneficiario'));
        contenedor.appendChild(div_error);

        result = false;
     }
     else
     {
        document.getElementById('nombre_beneficiario').style.border = "1px solid #CED4DA";
     }
     if( document.getElementById('id_beneficiario').value.length <= 0){

        document.getElementById('id_beneficiario').style.border = "1px solid red";

        var div_error = document.createElement('div');
        div_error.className = 'alert alert-danger';
        div_error.appendChild(document.createTextNode('Falta la identificación del beneficiario, recuerde que tiene que ingresar la identificación sin guiones\n'));
        contenedor.appendChild(div_error);
        result = false;
     }
     else
     {
        document.getElementById('id_beneficiario').style.border = "1px solid #CED4DA";
     }
     if( document.getElementById('parentesco_beneficiario').value.length <= 0){

        document.getElementById('parentesco_beneficiario').style.border = "1px solid red";

        var div_error = document.createElement('div');
        div_error.className = 'alert alert-danger';
        div_error.appendChild(document.createTextNode('Falta el parentesco del beneficiario\n'));
        contenedor.appendChild(div_error);
        result = false;
     }
     else
     {
        document.getElementById('parentesco_beneficiario').style.border = "1px solid #CED4DA";
     }
    /*if( document.getElementById('telefono_beneficiario').value.length < 8 || 
        isNaN(document.getElementById('telefono_beneficiario').value)){

        document.getElementById('telefono_beneficiario').style.border = "1px solid red";

        var div_error = document.createElement('div');
        div_error.className = 'alert alert-danger';
        div_error.appendChild(document.createTextNode('Falta el teléfono del beneficiario o está ingresando letras'));
        contenedor.appendChild(div_error);
        result = false;
     }
     else
     {
        document.getElementById('telefono_beneficiario').style.border = "1px solid #CED4DA";
     }
     if( document.getElementById('correo_beneficiario').value.length <= 0){

        document.getElementById('correo_beneficiario').style.border = "1px solid red";

        var div_error = document.createElement('div');
        div_error.className = 'alert alert-danger';
        div_error.appendChild(document.createTextNode('Falta el correo del beneficiarios\n'));
        contenedor.appendChild(div_error);
        result = false;
     }
     else
     {
        document.getElementById('correo_beneficiario').style.border = "1px solid #CED4DA";
     }*/

     return result;
    }

    function success() {
        var data = JSON.parse(this.responseText);
        if(data != undefined){
            document.getElementById('nombre_beneficiario').value = data['nombre']
        }
        else{

        }
        

    }

    function error() {
        var data = JSON.parse(this.responseText);
        document.getElementById('nombre_beneficiario').value = "";
    }

    $("input.id_beneficiario").bind('keypress', function(event) {
        var regex = new RegExp("^[a-zA-Z0-9 ]+$");
        var key = String.fromCharCode(!event.charCode ? event.which : event.charCode);
        if (!regex.test(key)) {
          event.preventDefault();
          return false;
       }
      });
});