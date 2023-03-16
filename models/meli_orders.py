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
    # Order fields Aca crear el modelo
    shipping_id = fields.Char('ID de envío')
    

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
                    obj["fulfilled"]=order["fulfilled"]
                    print(obj)

                current_page += 1
            else: 
                there_is_orders = False