odoo.define('rifcif_odoo_meli.JsToCallWizard', function (require) {
    "use strict";
    
    var ListController = require('web.ListController');
    
    var JsTocallWizard = ListController.include({
      renderButtons: function($node){
        this._super.apply(this, arguments);
        if (this.$buttons) {
          this.$buttons.on('click', '.o_button_to_sync_meli', this.action_to_sync_meli.bind(this));
          this.$buttons.on('click', '.o_button_to_sync_meli_ventas', this.action_to_sync_meli_ventas.bind(this));
          this.$buttons.appendTo($node);
        }
      },
      action_to_sync_meli: function(event) {
        console.log("PROBANDO ")
        event.preventDefault();
        var self = this;
        var rpc = require('web.rpc');
        console.log("Paso 2")
        rpc.query({
                    model: 'product.template',
                    method: 'testing_python',
                    args: [{

                      'arg1': "value1",

              }]
                }).then(function () { console.log("Todo") } )   
      },
      action_to_sync_meli_ventas: function(event) {
        console.log("PROBANDO ")
        event.preventDefault();
        var self = this;
        var rpc = require('web.rpc');
        console.log("Paso 2")
        rpc.query({
                    model: 'meli.sales',
                    method: 'sync_ventas',
                    args: [{

                      'arg1': "value1",

              }]
                }).then(function () { console.log("Todo") } )   
      },      
    });
    });