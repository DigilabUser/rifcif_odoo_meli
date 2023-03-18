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
    taxes_amount = fields.Integer('Cantidad')
 
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
