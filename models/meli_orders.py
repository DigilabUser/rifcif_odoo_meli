# -*- coding: utf-8 -*-

from ast import If
from odoo import models, fields, api
import requests
import json
import requests
import base64
from base64 import b64decode
import logging
from datetime import datetime
from datetime import timedelta
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)
class MercadolibreOrders(models.Model):
    _name = 'meli.order'
    _rec_name="ml_order_id"

    #campos relacionados
    item_ids = fields.One2many('meli.order.items', 'order_id', string='Items')
    payment_ids = fields.One2many('meli.order.payments', 'order_id', string='payment')
    current_page = fields.Integer(default=1)
    #orders = fields.One2many('meli.order', 'order_id')
    # Order fieldsellerr el modelo

    # Seller
    seller_nickname = fields.Char('Nombre del vendedor')
    seller_id = fields.Char('Id del vendedor')

    fulfilled = fields.Boolean('Fulfilled')
    buying_mode = fields.Char('Modo de compra')
    # Taxes
    taxes_amount = fields.Float('Impuestos')
 
    # order_request
    order_request_change = fields.Char('Cambio de pedido')
    order_request_return = fields.Char('Retorno de pedido')

    expiration_date = fields.Datetime('Fecha de caducidad')
    # Feedback
    feedback_sale = fields.Char('Venta')
    feedback_purchase = fields.Char('Comprar')
    # Shipping
    shipping_id = fields.Char('N° de Envío')

    date_closed = fields.Datetime('Fecha de cierre')

    ml_order_id = fields.Char('N° Orden')
    
    manufacturing_ending_date = fields.Datetime('Fecha de finalizacion de fabrica')
    hidden_for_seller = fields.Boolean('Oculto para el vendedor')

    date_last_updated = fields.Datetime('Fecha última actualización')
    last_updated = fields.Datetime('Última actualización')
    comments = fields.Char('Comentarios')
    pack_id = fields.Char('Id paquete')

    # Coupon
    coupon_amount= fields.Integer('Cantidad cupones')
    coupon_id = fields.Char('Id coupon')

    shipping_cost = fields.Float('Costo de envio')

    date_created = fields.Datetime('Fecha de creación')
    application_id = fields.Char('Id aplicación')
    pickup_id = fields.Char('Id recoger')
    status_detail = fields.Char('Estado detalle')
    buyer_nickname = fields.Char('Nombre comprador')
    buyer_id = fields.Char('Comprador')
    total_amount = fields.Integer('Cantidad total')
    paid_amount = fields.Float('Monto de pago')
    status= fields.Char('Estado')
    logistic_type = fields.Char('Tipo de logística')
    shipping_status = fields.Char('Estado de envío')
    sale_order_id = fields.Many2one('sale.order', string='Orden de Venta')
    delivery_address = fields.Char('Dirección de entrega')


    def create_sale_order_from_meli_order(self):
        #Me traigo todas las MELI order que sean not full
        meli_order_ids = self.env['meli.order'].search([('logistic_type','=','not full'),('sale_order_id','=',False)])
        #Las recorro
        for meli_order in meli_order_ids:
            #aca creo mi cliente.
            #Consumir el API BILLING con el meli_order["ml_order_id"]
            #https://api.mercadolibre.com/orders/{}/billing_info <--- de aca vas a traer el doc_number
            #Hacer busqueda con el numero de doc partner_exist = self.env["res.partner"].search([('vat','=',numero de documento)])
            #json_billing = self.get_data_from_api(url_billing,header)
            #--------
            
            #partner_exist = self.env["res.partner"].search([('vat','=',doc_number)])
            #El cliente no existe
            if len(partner_exist)==0:
                #Si el cliente no existe, lo creo
                new_partner = self.env['res.partner'].sudo().create({
                    'name':'prueba',
                    'lastname':'prueba',
                    'vat':'prueba',
                    'street':meli_order['delivery_address'],
                     'customer_rank':1
                })
                partner_exist = new_partner
            #_---------
            #aca voy a crear mi orden de venta
            obj={}
            obj['partner_id']=partner_exist['id']
            print(obj)
            # obj['date_order']=sale['date_order']
            # obj['name']=sale['name']
            # obj['amount_total']=sale['amount_total']
