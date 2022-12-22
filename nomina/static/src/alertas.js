'use strict';
odoo.define('cursos.docente.javascript', function(require) {

    require('web.dom_ready');
    var ajax = require('web.ajax');

    var button = $('#boton');

    var _onButton = function(e) {
        console.log(e);
    }

    button.click(_onButton);
})