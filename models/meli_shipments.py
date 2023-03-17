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
ORDERS_URI =API_URI + '/orders'
SHIPMENTS_URI = ORDERS_URI + '/{}/shipments'
ALBERT_ID='422252521'

class MercadolibreShipments(models.Model):
    _name = 'meli.shipments'
    #Van los campos de milagros.


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

    def syncShipments(self):
        #Obtener el token
        connector_obj = self.env['meli.connector'].search([])
        for conn in connector_obj:
            token = conn.token
        header = {'Authorization': 'Bearer '+ token}       
        #Traerme todas las ordenes descargadas
        order_ids = self.env["meli.order"].search([])
        for order in order_ids:
            #Solicitar los shipments
            shipment_id = order["shipment_id"]
            url_shipments = SHIPMENTS_URI.format(shipment_id)
            response_shipment = self.get_data_from_api(url_shipments,header)
            #Transformar respuesta en JSON
            json_shipments = json.loads(response_shipment.text)
            print(json_shipments)
            for shipment in json_shipments:
                #armar el obj
                obj={}
                obj["receiver_id"] = shipment["receiver_id"]
            

                #self.env["meli.shipments"].create(obj)
