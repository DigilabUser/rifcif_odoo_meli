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

API_URI = 'https://api.mercadolibre.com'
USERS_URI = API_URI + '/users'
ME_URI = USERS_URI + '/me'
ITEMS_URI = API_URI + '/items'
ITEM_URI = API_URI + '/items' + '/{}'
#SEARCH_ITEM_URI = USERS_URI + '/{}/items/search&sort=date_desc&'
ORDERS_URI =API_URI + '/orders'
SHIPMENTS_URI = ORDERS_URI + '/{}/shipments'
#GET_ORDER = ORDERS_URI + '/search?seller={}&order.status=paid'
GET_ORDER = ORDERS_URI + '/search?seller={}&limit={}&offset={}'
PRINT_TICKET_URI = API_URI + '/shipment_labels?shipment_ids={}&response_type=pdf'
ALBERT_ID='422252521'

class MercadolibreOrders(models.Model):
    _name = 'meli.order'

    current_page = fields.Integer(default=1)
    #orders = fields.One2many('meli.order', 'order_id')
    # Order fieldsellerr el modelo

    # Seller
    seller_nickname = fields.Char('Nombre del vendedor')
    seller_id = fields.Char('Id del vendedor')

    fulfilled = fields.Boolean('Cumplido') # Preguntar
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
    shipping_id = fields.Char('ID de envío')

    date_closed = fields.Datetime('Fecha de cierre')

    id = fields.Char('Id')
    
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
    
    # preguntar tags

    buyer_name = fields.Char('Nombre comprador')
    buyer_id = fields.Char('Id comprador')
    total_amount = fields.Integer('Cantidad total')
    paid_amount = fields.Float('Monto de pago')

    # preguntar mediations

    currency_id = fields.Char('Id divisa')
    status= fields.Char('Estado')

    def getImage(self, url):
        '''
        Función que convierte un URL a una imagen en BASE64 para poder guardarla en un 
        campo Binary
        '''
        return base64.b64encode(requests.get(url).content)

    def get_data_from_api(self, uri, header):
        """
        Función que nos permite consumir un API RestFUL y que nos devuelve la respuesta

        Attributes:
            uri (str): Endpoint donde se va a consumir
            header (str): Cabecera
        """
        response = requests.get(uri, headers=header)
        json_response = json.loads(response.text)
        return json_response

    def syncOrders(self):
        '''
        Función que sincroniza las ventas de mercadoLibre y las trae a Odoo
        '''
        #Seteo un flag para que jale todos los pedidos
        there_is_orders= True
        #Obtener el token
        connector_obj = self.env['meli.connector'].search([])
        for conn in connector_obj:
            token = conn.token
        header = {'Authorization': 'Bearer '+ token}
        #Autenticar
        response_user_me = requests.get(ME_URI, headers=header)
        json_user_me= json.loads(response_user_me.text)
        #Si el Token está caducado, avisará para crear uno nuevo.
        if json_user_me["status"] == 401:
            raise ValidationError("El Token ha caducado, por favor generarlo de nuevo")
        limit = 50 # Cantidad de órdenes por página
        current_page = 1
        while(there_is_orders):
            offset = (current_page - 1) * limit
            url_orders = GET_ORDER.format(json_user_me['id'], limit,offset)
            response_orders = requests.get(url_orders, headers=header)
            #Se transforma la respuesta en formato JSON
            json_orders = json.loads(response_orders.text)
            #print(json_orders)
            # if str(json_orders["status"]) == '4':
            #     raise ValidationError(json_orders["message"])
            data = json_orders["results"]
            if len(data)!= 0:
                for order in data:
                    print(order)
                    obj={}
                    obj["seller_nickname"]=order["seller"]["nickname"]
                    obj["seller_id"]=order["seller"]["id"]
                    obj["fulfilled"]=order["fulfilled"]
                    obj["buying_mode"]=order["buying_mode"]
                    obj["taxes_amount"]=order["taxes"]["amount"]
                    obj["order_request_change"]=order["order_request"]["change"]
                    obj["order_request_return"]=order["order_request"]["return"]
                    obj["expiration_date"]=order["expiration_date"]
                    obj["feedback_sale"]=order["feedback"]["sale"]
                    obj["feedback_purchase"]=order["feedback"]["purchase"]
                    obj["shipping"]=order["shipping"]["id"]
                    
                    print(obj)

                current_page += 1
            else: 
                there_is_orders = False