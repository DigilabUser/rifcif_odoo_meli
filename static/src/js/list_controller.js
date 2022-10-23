odoo.define('rifcif_odoo_meli.JsToCallWizard', function (require) {
    "use strict";
    
    var ListController = require('web.ListController');
    
    var JsTocallWizard = ListController.include({
      renderButtons: function($node){
        this._super.apply(this, arguments);
        if (this.$buttons) {
          this.$buttons.on('click', '.o_button_to_sync_meli', this.action_to_sync_meli.bind(this));
          this.$buttons.appendTo($node);
        }
      },
      action_to_sync_meli: function(event) {
        event.preventDefault();
        var self = this;
        var rpc = require('web.rpc');

        rpc.query({
                    model: 'product.template',
                    method: 'testing_python',
                    args: []
                }).then(function (returned_value) { console.log("Todo") } )   
      },
    });
    });