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
GET_ORDER = ORDERS_URI + '/search?seller={}&order.date_created.from=2022-11-09T00:00:00.000-00:00&order.date_created.to=2022-11-10T00:00:00.000-00:00&sort=date_desc'
PRINT_TICKET_URI = API_URI + '/shipment_labels?shipment_ids={}&response_type=pdf'
ALBERT_ID='422252521'

class MkSales(models.Model):
    _name = 'meli.sales'
    _rec_name="meli_order_id"

    # Order fields
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
    sh_ticket = fields.Binary('Ticket de envío')
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

    def printticket(self):
        connector_obj = self.env['meli.connector'].search([])
        for conn in connector_obj:
            token = conn.token
        header = {'Authorization': 'Bearer '+ token}        
        #Obtener el ticket
        print_uri = PRINT_TICKET_URI.format(self.sh_shipping_id)
        response = requests.get(print_uri, headers=header)
        _logger.info(response.status_code)        
        # Save the PDF
        if response.status_code == 200:
            with open('prueba.pdf', "wb") as f:
                f.write(response.content)
                f.close()
            file = open("prueba.pdf", "rb")
            out = file.read()
            file.close()
            self.sh_ticket = base64.b64encode(out)            
        else:
            print(response.status_code)
        return response.content