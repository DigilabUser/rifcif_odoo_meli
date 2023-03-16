# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json
from odoo.exceptions import ValidationError
import logging
import base64
import datetime
_logger = logging.getLogger(__name__)
API_URI = 'https://api.mercadolibre.com'
USERS_URI = API_URI + '/users'
ME_URI = USERS_URI + '/me'
ITEM_URI = API_URI + '/items' + '/{}'
ITEMS_USER_URI = USERS_URI + '/{}/items/search?orders=available_quantity_desc&limit=100'
#SEARCH_ITEM_URI = USERS_URI + '/{}/items/search&sort=date_desc&'
ORDERS_URI =API_URI + '/orders'


class MkStock(models.Model):
    _name = 'meli.stock'

    item_id = fields.Char(string="Item ID")
    titulo = fields.Char(string="Titulo")
    codigo_inventario = fields.Char(string="Codigo de inventario")
    cantidad_inicial = fields.Integer(string="Cantidad inicial")
    cantidad_disponible = fields.Integer(string="Cantidad disponible")
    cantidad_vendida = fields.Integer(string="Cantidad vendidad")

    def get_data_from_api(self, uri, header):
        response = requests.get(uri, headers=header)
        json_response = json.loads(response.text)
        return json_response

    def syncOrders(self):
        #Obtener el token
        connector_obj = self.env['meli.connector'].search([])
        for conn in connector_obj:
            token = conn.token
        header = {'Authorization': 'Bearer '+ token}
        #Autenticar
        response_user_me = requests.get(ME_URI, headers=header)
        json_user_me= json.loads(response_user_me.text)
        if json_user_me["status"] == 401:
            raise ValidationError("El Token ha caducado, por favor generarlo de nuevo")
        #Obtener los items
        items_array = []
        url_items = ITEMS_USER_URI.format(json_user_me['id'])
        response_items = requests.get(url_items, headers=header)
        json_items = json.loads(response_items.text)
        _logger.info(json_items)
        data = json_items["results"]
        for item in data:
            items_array.append(item)
            # if len(data)==0:
            #     flag=False
        for item in items_array:
            url_items = ITEM_URI.format(item)            
            response_items = requests.get(url_items, headers=header)
            json_items = json.loads(response_items.text)
            obj = {
                "item_id":json_items["id"],
                "titulo":json_items["title"],
                "codigo_inventario":json_items["inventory_id"],
                "cantidad_inicial":json_items["initial_quantity"],
                "cantidad_disponible":json_items["available_quantity"],
                "cantidad_vendida":json_items["sold_quantity"]
            }
            qty_item = self.env['meli.stock'].search([('item_id','=', json_items["id"])])
            
            if len(qty_item) == 0:
                self.env['meli.stock'].sudo().create(obj)
            else:
                qty_item.sudo().write(obj)                
                
