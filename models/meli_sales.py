# -*- coding: utf-8 -*-

from ast import If
from odoo import models, fields, api
import requests
import json
import requests
import base64
import logging
from datetime import datetime
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

API_URI = 'https://api.mercadolibre.com'
USERS_URI = API_URI + '/users'
ME_URI = USERS_URI + '/me'
ITEMS_URI = API_URI + '/items'
ITEM_URI = API_URI + '/items' + '/{}'
SEARCH_ITEM_URI = USERS_URI + '/{}/items/search'
ORDERS_URI =API_URI + '/orders'
SHIPMENTS_URI = ORDERS_URI + '/{}/shipments'
#GET_ORDER = ORDERS_URI + '/search?seller={}&order.status=paid'
GET_ORDER = ORDERS_URI + '/search?seller={}'
ALBERT_ID='422252521'
class MkSales(models.Model):
    _name = 'meli.sales'
    _rec_name="meli_order_id"

    meli_order_id = fields.Char(string="Número de orden")
    meli_item_id = fields.Char(string="Código de item")
    meli_shipping_id = fields.Char(string="Código de envío")
    logistic_type = fields.Char(string="Tipo de logistica")
    date_created = fields.Datetime('Fecha de creación')
    date_closed = fields.Datetime('Fecha de cierre')
    date_updated = fields.Datetime('Fecha de actualización')
    total_amount = fields.Float('Monto total')
    paid_amount = fields.Float('Monto pagado')
    status = fields.Char('Estado')
    buyer_nickname = fields.Char('Nick del comprador')
    buyer_name = fields.Char('Nombre del comprador')
    # Shipping fields
    sh_shipping_id = fields.Char('Código de envio')
    sh_logistic_type = fields.Char('Tipo de logística')
    sh_status = fields.Char('Estado de envío')
    sh_tracking_method = fields.Char('Tipo de seguimiento')
    sh_geolocation_map = fields.Char('Ubicación de envío')
    sh_country = fields.Char('Pais')
    sh_city = fields.Char('Ciudad')
    sh_address_line = fields.Char('Dirección de envío')
    sh_receiver_name = fields.Char('Nombre de recepcionista')
    sh_comment = fields.Text('Comentario')
    #Items fields
    it_image = fields.Binary('Imagen')
    it_title= fields.Char('Título')
    it_category= fields.Char('Categoría')
    it_price= fields.Char('Precio')
    it_initial_quantity= fields.Char('Cantidad Inicial')
    it_available_quantity= fields.Char('Cantidad disponible')
    it_sold_quantity= fields.Char('Cantidad vendida')
    it_condition= fields.Char('Condición')
    it_warranty= fields.Char('Garantía')   

    def getImage(self, url):
        return base64.b64encode(requests.get(url).content)

    def get_data_from_api(self, uri, header):
        response = requests.get(uri, headers=header)
        json_response = json.loads(response.text)
        return json_response

    def sync_ventas(self):
        #Obtener el token
        connector_obj = self.env['meli.connector'].search([])
        for conn in connector_obj:
            token = conn.token
        header = {'Authorization': 'Bearer '+ token}
        #Autenticar
        response_user_me = requests.get(ME_URI, headers=header)
        json_user_me= json.loads(response_user_me.text)
        _logger.info(json_user_me)
        if json_user_me["status"] == 401:
            raise ValidationError("El Token ha caducado, por favor generarlo de nuevo")
        #Obtener las ordenes
        url_orders = GET_ORDER.format(json_user_me['id'])
        response_orders = requests.get(url_orders, headers=header)
        json_orders = json.loads(response_orders.text)
        #_logger.info("\n\n %s",json_orders)
        data = json_orders["results"]
        for order in data:
            # Getting Shipping Data
            shipping = self.get_data_from_api(SHIPMENTS_URI.format(order["id"]), header)
            sh_shipping_id = shipping["id"] if shipping["status"]!=404 else ""
            sh_logistic_type = "" if shipping["status"]==404 else "full" if shipping["logistic_type"]  == "fulfillment" else "notfull"
            sh_status = shipping["status"] if shipping["status"]!=404 else ""
            sh_status_history = shipping["status_history"] if shipping["status"]!=404 else ""
            sh_shipping_items=shipping["shipping_items"] if shipping["status"]!=404 else ""
            sh_tracking_method=shipping["tracking_method"] if shipping["status"]!=404 else ""
            sh_receiver_address=shipping["receiver_address"] if shipping["status"]!=404 else ""
            sh_geolocation_map="https://www.google.com.pe/maps/place/{},%20{}".format(sh_receiver_address["latitude"],sh_receiver_address["longitude"]) if shipping["status"]!=404 else ""
            sh_country = sh_receiver_address["country"]["name"] if shipping["status"]!=404 else ""
            sh_city = sh_receiver_address["city"]["name"] if shipping["status"]!=404 else ""
            sh_address_line = sh_receiver_address["address_line"] if shipping["status"]!=404 else ""
            sh_receiver_name = sh_receiver_address["receiver_name"] if shipping["status"]!=404 else ""
            sh_comment = sh_receiver_address["comment"] if shipping["status"]!=404 else ""

            # Getting Item Data
            order_items = order['order_items'][0]
            item = self.get_data_from_api(ITEM_URI.format(order_items["item"]["id"]), header)
            it_image = self.getImage(item["pictures"][0]["url"]) if len(item["pictures"])>0 else ""
            it_title= item["title"]
            it_category= item["category_id"]
            it_price= item["price"]
            it_initial_quantity= item["initial_quantity"]
            it_available_quantity= item["available_quantity"]
            it_sold_quantity= item["sold_quantity"]
            it_condition= item["condition"]
            it_attributes= item["attributes"]
            it_warranty= item["warranty"]

            # Getting Order Data
            item_id = order_items["item"]["id"]
            # url_items = 'https://api.mercadolibre.com/items/{}'.format(item_id)
            # response_items = requests.get(url_items, headers=header)
            # json_items = json.loads(response_items.text)
            #logistic_type = "full" if json_items["shipping"]["logistic_type"] == "fulfillment" else "notfull"
            # if sh_logistic_type == "full":
            #     _logger.info(self.get_shippings( order["id"],header))
            order_obj={
                'meli_order_id': order["id"],
                'meli_item_id':item_id,
                'meli_shipping_id':sh_shipping_id,
                'logistic_type':sh_logistic_type,
                'date_created':datetime(int(order["date_created"][0:4]),int(order["date_created"][5:7]),int(order["date_created"][8:10])),
                'date_closed':datetime(int(order["date_closed"][0:4]),int(order["date_closed"][5:7]),int(order["date_closed"][8:10])),
                'date_updated':datetime(int(order["last_updated"][0:4]),int(order["last_updated"][5:7]),int(order["last_updated"][8:10])),
                'total_amount':order["total_amount"],
                'paid_amount':order["paid_amount"],
                'status':order["status"],
                'buyer_nickname':order["buyer"]["nickname"],
                'sh_shipping_id' : sh_shipping_id,
                'sh_logistic_type' : sh_logistic_type,
                'sh_status' : sh_status,
                'sh_tracking_method' : sh_tracking_method,
                'sh_geolocation_map':sh_geolocation_map,
                'sh_country':sh_country,
                'sh_city':sh_city,
                'sh_address_line':sh_address_line,
                'sh_receiver_name':sh_receiver_name,
                'sh_comment':sh_comment,
                'it_image':it_image,
                'it_title': it_title,
                'it_category': it_category,
                'it_price': it_price,
                'it_initial_quantity': it_initial_quantity,
                'it_available_quantity': it_available_quantity,
                'it_sold_quantity': it_sold_quantity,
                'it_condition': it_condition,
                'it_warranty': it_warranty                  
                #'buyer_name':order["buyer"]["first_name"] + " " + order["buyer"]["last_name"],
            }
            qty_order = self.env['meli.sales'].search([('meli_order_id','=',item_id)])
            
            if len(qty_order) == 0:
                self.env['meli.sales'].sudo().create(order_obj)
            else:
                qty_order.sudo().write(order_obj)
