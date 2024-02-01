odoo.define('sa_graduacion.preceso_graduacion', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    const Dialog = require('web.Dialog');
    const { _t, qweb } = require('web.core');
    const ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var identificacion = "";
    var titulo_Media = "";
    var titulo_Diploma = "";
    var titulo_Apostille = "";
    var titulo_Equiparacion = "";
    var titulo_Bachillerato = "";
    var titulo_Bachillerato_Licenciatura = "";
    var TCU = "";
    var comprobante = "";
    var boleta = "";
    var grado = "";
    var estado_Migratorio = "";
    var send = false;

    publicWidget.registry.UIAProcesoGraduacion = publicWidget.Widget.extend({
        selector: '.proceso_graduacion_form',
        events: {
            'click #btn_buscar_estudiante': 'btnBuscarEstudiante',
            'click #btn_Enviar_Solicitud': 'btnEnviarSolicitud',
            'click #btn_Enviar_PG': 'btnEnviarPG',
        },

        start: function () {
        },

        btnBuscarEstudiante: function () {
            try {
                hideAll();
                setcargarDocs();
                var container = document.querySelector('#proceso_graduacion_carreras_container');
                document.querySelector('#notificaciones_container').innerHTML = "";

                ajax.jsonRpc('/get_estado_graduacion', 'call', {
                    cedulaEstudiante: document.getElementById("cedulaEstudiante").value,
                }).then(function (result) {
                    if (result['tiene'] == false || result['estado'] == "Rechazado") {
                        if(result['estado'] == "Rechazado"){
                            var btn = document.getElementById("btn_Enviar_Solicitud");

                            btn.onclick = btnActualizarSolicitud;
                        }
                        ajax.jsonRpc('/get_estudiante_carreras', 'call', {
                            cedulaEstudiante: document.getElementById("cedulaEstudiante").value,
                        }).then(function (result) {
                            if (result['tiene']) {
                                var select_carrera = document.getElementById("carrera");
                                removeOptions(document.getElementById('carrera'));
                                select_carrera.onchange = onchangeCarrea;

                                result['carreras'].forEach((item, idex, arr) => {
                                    var opt = document.createElement('option');
                                    opt.value = item;
                                    opt.innerHTML = item;
                                    select_carrera.appendChild(opt);
                                });


                                container.style.display = "block";
                                container.appendChild(select_carrera);



                            } else {
                                showNotificacionAlert("")
                            }
                        });


                    } else {
                        if (result['pago'] == false && result['estado'] == "Aprobado") {
                            showDocumentosPago();
                        } else {
                            showNotificacionAlert("Estado: " + result['estado'])
                        }

                    }
                });

            } catch (err) {
            }
        },
        btnEnviarSolicitud: function () {

            var identificacion_ = document.getElementById('cedulaEstudiante').value
            var correo = document.getElementById('correo').value
            var telefono = document.getElementById('telefono').value
            var carrera = document.getElementById('carrera').value

            if (correo == "") {
                showNotificacionAlert("Falta rellenar el campo de correo")
            }

            if (telefono == "") {
                showNotificacionAlert("Falta rellenar el campo de telefono")
            }
            var send = verificarData();
            if(verificarData()){
                var vals = {
                    "identificacion": identificacion_,
                    "correo": correo,
                    "telefono": telefono,
                    "carrera": carrera,
                    "grado": grado,
                    "estado_Migratorio": (estado_Migratorio != "" ? estado_Migratorio : false),
                    "copia_Identificacion": (identificacion != "" ? identificacion : false),
                    "copia_Titulo_Educacion": (titulo_Media != "" ? titulo_Media : false),
                    "copia_Diploma": (titulo_Diploma != "" ? titulo_Diploma : false),
                    "copia_Apostille": (titulo_Apostille != "" ? titulo_Apostille : false),
                    "copia_Equiparacion_MEP": (titulo_Equiparacion != "" ? titulo_Equiparacion : false),
                    "copia_Titulo_Bachillerato": (titulo_Bachillerato != "" ? titulo_Bachillerato : false),
                    "copia_Titulo_Bachillerato_Licenciatura": (titulo_Bachillerato_Licenciatura != "" ? titulo_Bachillerato_Licenciatura : false),
                    "copia_TCU_Certificacion": (TCU != "" ? identificacion : false),
                }
                ajax.jsonRpc('/proceso_graduacion_crear', 'call', {
                    valsJS: vals,
                }).then(function (result) {
                    hideAll();
                    showNotificacionAlert(result['result'])
                });
            }else{
                showNotificacionAlert("Faltan Documentos por cagar");
            }



        },

        btnEnviarPG: function () {
            var vals = {
                "comprobante": comprobante,
                "boleta": boleta,
                "identificacion": document.getElementById('cedulaEstudiante').value,
            }
            ajax.jsonRpc('/set_pago_graduacion', 'call', {
                valsJS: vals,
            }).then(function (result) {
                hideAll();
                showNotificacionAlert(result['result'])
            });

        }

    });

    function btnActualizarSolicitud() {

        var identificacion_ = document.getElementById('cedulaEstudiante').value
        var correo = document.getElementById('correo').value
        var telefono = document.getElementById('telefono').value
        var carrera = document.getElementById('carrera').value

        if (correo == "") {
            showNotificacionAlert("Falta rellenar el campo de correo")
        }

        if (telefono == "") {
            showNotificacionAlert("Falta rellenar el campo de telefono")
        }
        var send = verificarData();
        if(verificarData()){
            var vals = {
                "identificacion": identificacion_,
                "correo": correo,
                "telefono": telefono,
                "carrera": carrera,
                "grado": grado,
                "estado_Migratorio": (estado_Migratorio != "" ? estado_Migratorio : false),
                "copia_Identificacion": (identificacion != "" ? identificacion : false),
                "copia_Titulo_Educacion": (titulo_Media != "" ? titulo_Media : false),
                "copia_Diploma": (titulo_Diploma != "" ? titulo_Diploma : false),
                "copia_Apostille": (titulo_Apostille != "" ? titulo_Apostille : false),
                "copia_Equiparacion_MEP": (titulo_Equiparacion != "" ? titulo_Equiparacion : false),
                "copia_Titulo_Bachillerato": (titulo_Bachillerato != "" ? titulo_Bachillerato : false),
                "copia_Titulo_Bachillerato_Licenciatura": (titulo_Bachillerato_Licenciatura != "" ? titulo_Bachillerato_Licenciatura : false),
                "copia_TCU_Certificacion": (TCU != "" ? identificacion : false),
            }
            ajax.jsonRpc('/proceso_graduacion_actualizar', 'call', {
                valsJS: vals,
            }).then(function (result) {
                hideAll();
                showNotificacionAlert(result['result'])
            });
        }else{
            showNotificacionAlert("Faltan Documentos por cagar");
        }



    }

    function onchangeCarrea() {
        var carrera = document.getElementById('carrera').value
        hideAll();

        switch (true) {

            case carrera.includes("BACHILLERATO") &&
                document.getElementById('nacional').checked:
                showDocumentosBachillerNacional();
                grado = "BACHILLERATO";
                estado_Migratorio = "Nacional";
                break;

            case carrera.includes("BACHILLERATO") &&
                document.getElementById('extranjero').checked:
                showDocumentosBachillerExtranjero();
                grado = "BACHILLERATO";
                estado_Migratorio = "Extranjero";
                break;

            case carrera.includes("LICENCIATURA") &&
                document.getElementById('nacional').checked: showDocumentosLicenNacional(); grado = "LICENCIATURA"; estado_Migratorio = "Nacional";
                break;

            case carrera.includes("LICENCIATURA") &&
                document.getElementById('extranjero').checked: showDocumentosLicenxtranjero(); grado = "LICENCIATURA"; estado_Migratorio = "Extranjero";
                break;

            case carrera.includes("MAESTRIA") || carrera.includes("MAESTRÍA") &&
                document.getElementById('nacional').checked: showDocumentosMaestriaNacional(); grado = "MAESTRIA"; estado_Migratorio = "Nacional";
                break;

            case carrera.includes("MAESTRIA") || carrera.includes("MAESTRÍA") &&
                document.getElementById('extranjero').checked: 
                showDocumentosMaestriaExtranjero(); grado = "MAESTRIA"; estado_Migratorio = "Extranjero";
                break;

            case carrera.includes("ESPECIALIDAD") &&
                document.getElementById('nacional').checked: showDocumentosMaestriaNacional(); grado = "MAESTRIA"; estado_Migratorio = "Nacional";
                break;

            case carrera.includes("ESPECIALIDAD") &&
                document.getElementById('extranjero').checked: showDocumentosMaestriaExtranjero(); grado = "MAESTRIA"; estado_Migratorio = "Extranjero";
                break;

        }

    }

    function showDocumentosBachillerNacional() {
        var container = document.getElementById("proceso_graduacion_informacion_BN");
        container.style.display = "block";
    }

    function showDocumentosBachillerExtranjero() {
        var container = document.getElementById("proceso_graduacion_informacion_BE");
        container.style.display = "block";
    }

    function showDocumentosLicenNacional() {
        var container = document.getElementById("proceso_graduacion_informacion_LN");
        container.style.display = "block";
    }

    function showDocumentosLicenxtranjero() {
        var container = document.getElementById("proceso_graduacion_informacion_LE");
        container.style.display = "block";
    }

    function showDocumentosMaestriaNacional() {
        var container = document.getElementById("proceso_graduacion_informacion_MN");
        container.style.display = "block";
    }

    function showDocumentosMaestriaExtranjero() {
        var container = document.getElementById("proceso_graduacion_informacion_ME");
        container.style.display = "block";
    }
    function showDocumentosPago() {
        var container = document.getElementById("proceso_graduacion_informacion_PG");
        container.style.display = "block";
    }

    function removeOptions(selectElement) {
        var i, L = selectElement.options.length - 1;
        for (i = L; i >= 0; i--) {
            selectElement.remove(i);
        }
    }

    function cargarDocs() {
        var alertPlaceholder = document.querySelector('#notificaciones_container');
        alertPlaceholder.innerHTML = "";
        var contenedores = document.querySelectorAll(`[id^="proceso_graduacion_informacion_"]`);
        contenedores.forEach((item, idex, arr) => {
            var style = window.getComputedStyle(item);
            var display = style.getPropertyValue('display');
            if (display == "block") {
                var inputs = item.querySelectorAll(`[type^="file"]`);

                inputs.forEach((item, idex, arr) => {
                    var file = item.files[0];

                    if (typeof file !== 'undefined') {
                        var reader = new FileReader();
                        reader.readAsDataURL(file);
                        reader.onload = function () {
                            switch (item.id) {
                                case "identificacion": identificacion = reader.result.replace(/^data:.+;base64,/, ''); break;

                                case "titulo_Media": titulo_Media = reader.result.replace(/^data:.+;base64,/, ''); break;

                                case "titulo_Diploma": titulo_Diploma = reader.result.replace(/^data:.+;base64,/, ''); break;

                                case "titulo_Apostille": titulo_Apostille = reader.result.replace(/^data:.+;base64,/, ''); break;

                                case "titulo_Equiparacion": titulo_Equiparacion = reader.result.replace(/^data:.+;base64,/, ''); break;

                                case "titulo_Bachillerato": titulo_Bachillerato = reader.result.replace(/^data:.+;base64,/, ''); break;

                                case "titulo_Bachillerato_Licenciatura": titulo_Bachillerato_Licenciatura = reader.result.replace(/^data:.+;base64,/, ''); break;

                                case "TCU": TCU = reader.result.replace(/^data:.+;base64,/, ''); break;

                                case "comprobante": comprobante = reader.result.replace(/^data:.+;base64,/, ''); break;

                                case "boleta": boleta = reader.result.replace(/^data:.+;base64,/, ''); break;
                            }
                        };
                        reader.onerror = function (error) {
                            console.log('Error: ', error);
                        };
                    } else {
                        /* switch(item.id){
                             case "identificacion" : showNotificacionAlert("identificacion"); break;
                             case "titulo_Media" : showNotificacionAlert("identificacion"); break;
                             case "titulo_Diploma" : showNotificacionAlert("identificacion"); break;
                             case "titulo_Apostille" : showNotificacionAlert("identificacion"); break;
                             case "titulo_Equiparacion" : showNotificacionAlert("identificacion"); break;
                             case "titulo_Bachillerato" : showNotificacionAlert("identificacion"); break;
                             case "titulo_Bachillerato_Licenciatura" : showNotificacionAlert("identificacion"); break;
                             case "TCU" : showNotificacionAlert("identificacion"); break;
                             case "comprobante" : showNotificacionAlert("identificacion"); break;
                             case "boleta" : showNotificacionAlert("identificacion"); break;
                         }*/
                    }

                });
            }

        });

    }

    function setcargarDocs() {
        var alertPlaceholder = document.querySelector('#notificaciones_container');
        alertPlaceholder.innerHTML = "";
        var contenedores = document.querySelectorAll(`[id^="proceso_graduacion_informacion_"]`);
        contenedores.forEach((item, idex, arr) => {
            var inputs = item.querySelectorAll(`[type^="file"]`);

            inputs.forEach((item, idex, arr) => {
                item.onchange = cargarDocs;
            });

        });

    }

    function verificarData() {
        var send = false;
        var alertPlaceholder = document.querySelector('#notificaciones_container');
        alertPlaceholder.innerHTML = "";
        var contenedores = document.querySelectorAll(`[id^="proceso_graduacion_informacion_"]`);
        contenedores.forEach((item, idex, arr) => {
            var style = window.getComputedStyle(item);
            var display = style.getPropertyValue('display');
            if (display == "block") {
                var inputs = item.querySelectorAll(`[type^="file"]`);

                inputs.forEach((item, idex, arr) => {
                    var file = item.files[0];

                    if (typeof file !== 'undefined') {
                        switch (item.id) {
                            case "identificacion":
                                if (identificacion != "") {
                                    send = true
                                } else {
                                    send = false
                                }
                                break;

                            case "titulo_Media":
                                if (titulo_Media != "") {
                                    send = true
                                } else {
                                    send = false
                                }
                                break;

                            case "titulo_Diploma":
                                if (titulo_Diploma != "") {
                                    send = true
                                } else {
                                    send = false
                                }
                                break;

                            case "titulo_Apostille":
                                if (titulo_Apostille != "") {
                                    send = true
                                } else {
                                    send = false
                                }
                                break;

                            case "titulo_Equiparacion":
                                if (titulo_Equiparacion != "") {
                                    send = true
                                } else {
                                    send = false
                                }
                                break;

                            case "titulo_Bachillerato":
                                if (titulo_Bachillerato != "") {
                                    send = true
                                } else {
                                    send = false
                                }
                                break;

                            case "titulo_Bachillerato_Licenciatura":
                                if (titulo_Bachillerato_Licenciatura != "") {
                                    send = true
                                } else {
                                    send = false
                                }
                                break;

                            case "TCU":
                                if (TCU != "") {
                                    send = true
                                } else {
                                    send = false
                                }
                                break;

                            case "comprobante":
                                if (comprobante != "") {
                                    send = true
                                } else {
                                    send = false
                                }
                                break;

                            case "boleta":
                                if (boleta != "") {
                                    send = true
                                } else {
                                    send = false
                                }
                                break;
                        }
                    } else {
                    }

                });
            }

        });

        return send
    }

    function hideAll() {
        var container = document.getElementById("proceso_graduacion_informacion_BN");
        container.style.display = "none";
        var container = document.getElementById("proceso_graduacion_informacion_BE");
        container.style.display = "none";
        var container = document.getElementById("proceso_graduacion_informacion_LN");
        container.style.display = "none";
        var container = document.getElementById("proceso_graduacion_informacion_LE");
        container.style.display = "none";
        var container = document.getElementById("proceso_graduacion_informacion_MN");
        container.style.display = "none";
        var container = document.getElementById("proceso_graduacion_informacion_ME");
        container.style.display = "none";
        var container = document.getElementById("proceso_graduacion_informacion_PG");
        container.style.display = "none";

    }
    function hideInfo() {
        var container = document.getElementById("proceso_graduacion_carreras_container");
        container.style.display = "none";
    }

    function showNotificacionAlert(notificacion) {
        var alertPlaceholder = document.querySelector('#notificaciones_container');
        var div_alert = document.createElement('div');
        var p_text = document.createElement('p');
        p_text.innerHTML = notificacion;
        div_alert.className = "alert alert-warning";
        div_alert.id = 'alert_docente_no_encontrado'
        div_alert.style.borderRadius = "5px";
        div_alert.style.marginTop = "5px";
        div_alert.appendChild(p_text);
        div_alert.style.fontSize = "15px";
        div_alert.style.fontWeight = "900";
        alertPlaceholder.appendChild(div_alert);
    }
});