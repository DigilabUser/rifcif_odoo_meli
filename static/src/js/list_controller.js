odoo.define('rifcif_odoo_meli.JsToCallWizard', function (require) {
    "use strict";
    
    var ListController = require('web.ListController');
    
    var JsTocallWizard = ListController.include({
      renderButtons: function($node){
        this._super.apply(this, arguments);
        if (this.$buttons) {
//          this.$buttons.on('click', '.o_button_to_sync_meli', this.action_to_sync_meli.bind(this));
//          this.$buttons.on('click', '.o_button_to_sync_meli_ventas', this.action_to_sync_meli_ventas.bind(this));
          this.$buttons.on('click', '.o_button_to_sync_meli_ventas_dates', this.action_to_sync_meli_ventas_dates.bind(this));
          this.$buttons.on('click', '.o_button_to_sync_meli_print_tickets', this.action_to_sync_meli_print_tickets.bind(this));
          this.$buttons.on('click', '.o_button_to_sync_meli_stock', this.action_to_sync_meli_stock.bind(this));
          this.$buttons.on('click', '.o_button_to_sync_meli_order', this.action_to_sync_meli_order.bind(this));
          this.$buttons.on('click', '.o_button_to_sync_meli_shipments', this.action_to_sync_meli_shipments.bind(this));
          this.$buttons.appendTo($node);
        }
      },
      action_to_sync_meli_stock: function(event) {
        console.log("PROBANDO ")
        event.preventDefault();
        var self = this;
        var rpc = require('web.rpc');
        console.log("Paso 2")
        rpc.query({
                    model: 'meli.stock',
                    method: 'syncOrders',
                    args: [{

                      'arg1': "value1",

              }]
                }).then(function () { console.log("Todo") } )   
      },
      action_to_sync_meli_order: function(event) {
        event.preventDefault();
        var self = this;
        self.do_action({
          name: "Traer ordenes de Mercadolibre",
          type: 'ir.actions.act_window',
          res_model: 'meli.order.wizard',
          view_mode: 'form',
          view_type: 'form',
          views: [[false, 'form']],
          target: 'new',
       });  
      },      
      action_to_sync_meli_shipments: function(event) {
        event.preventDefault();
        var self = this;
        var rpc = require('web.rpc');
        rpc.query({
          model: 'meli.shipments',
          method: 'syncShipments',
          args: [{
            'arg1':"sadasd"
          }]

        }).then(function () { console.log("Todo") } )
      },      
          
      // action_to_sync_meli_ventas: function(event) {
      //   console.log("PROBANDO ")
      //   event.preventDefault();
      //   var self = this;
      //   var rpc = require('web.rpc');
      //   console.log("Paso 2")
      //   rpc.query({
      //               model: 'meli.sales',
      //               method: 'sync_ventas',
      //               args: [{

      //                 'arg1': "value1",

      //         }]
      //           }).then(function () { console.log("Todo") } )   
      // },  
      action_to_sync_meli_ventas_dates: function(event) {
        event.preventDefault();
        var self = this;
        self.do_action({
          name: "Traer ordenes de Mercadolibre",
          type: 'ir.actions.act_window',
          res_model: 'meli.sales.wizard',
          view_mode: 'form',
          view_type: 'form',
          views: [[false, 'form']],
          target: 'new',
       }); 
      },   
      action_to_sync_meli_print_tickets: function(event) {
        event.preventDefault();
        var self = this;
        self.do_action({
          name: "Imprimir Tickets",
          type: 'ir.actions.act_window',
          res_model: 'meli.multi.ticket.wizard',
          view_mode: 'form',
          view_type: 'form',
          views: [[false, 'form']],
          target: 'new',
       }); 
      },       
                  
    });
    });