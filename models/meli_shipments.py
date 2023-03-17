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
#Campos no relacionales
    
    snapshot_packing = fields.Char('Paquete instantánea')
    receiver_id = fields.Char('Id del destinatario')
    base_cost = fields.Integer('Cumplido') 

    #Status_history
    date_shipped = fields.Datetime('Fecha de envío')
    date_returned = fields.Datetime('Fecha de regreso')
    date_delivered = fields.Datetime('Fecha de entrega')
    date_first_visit = fields.Datetime('Fecha de primera visita')
    date_not_delivered = fields.Datetime('Fecha no entregada')
    date_cancelled = fields.Datetime('Fecha cancelada')
    date_handling = fields.Datetime('Fecha de manejo')
    date_ready_to_ship = fields.Datetime('Fecha lista para enviar')
    
    type = fields.Char('Tipo')
    return_details = fields.Char('Detalles de devolución')
    sender_id = fields.Char('Id del remitente')
    mode = fields.Char('Modo')
    order_cost = fields.Integer('Costo de la orden')
    service_id = fields.Char('Id del servicio')
    tracking_number = fields.Char('Número de tracking')
    
 
    # cost_components
    cost_components_loyal_discount = fields.Float('Descuento ?????')
    cost_components_special_discount = fields.Float('Descuento especial')
    cost_components_compensation = fields.Float('Compensasión')
    cost_components_gap_discount = fields.Float('Descuento brecha')
    cost_components_ratio = fields.Char('Relación')

    id = fields.Char('Id')
    tracking_method = fields.Char('Método de tracking')
    last_updated = fields.Datetime('Última actualización')
    items_types = fields.Char('Tipo de items')
    comments = fields.Char('Comentarios')
    substatus = fields.Char('Substatus')
    date_created = fields.Datetime('Fecha de creación')
    date_first_printed = fields.Datetime('Fecha de primera impresión')
    created_by = fields.Char('Creado por')
    application_id = fields.Char('Id de aplicación')
    
    #Sender address
    sender_address_country_name = fields.Char('Nombre de país')
    sender_address_address_line = fields.Char('Dirección')
    sender_address_scoring = fields.Char('Puntuación')
    sender_address_agency = fields.Char('Agencia')
    sender_address_city_name = fields.Char('Ciudad')
    sender_address_geolocation_type = fields.Char('Tipo de geolocalización')
    sender_address_latitude = fields.Char('Latitud')
    sender_address_municipality_name = fields.Char('Nombre de municipalidad')
    sender_address_location_id = fields.Char('Id de locación')
    sender_address_street_name = fields.Char('Nombre de la calle')
    sender_address_zip_code = fields.Char('Código ZIP')
    sender_address_geolocation_source = fields.Char('Fuente de geolocalización')
    sender_address_intersection = fields.Char('Intersección')
    sender_address_street_number = fields.Char('Número de la calle')
    sender_address_comment = fields.Char('Comentario')
    sender_address_id = fields.Char('Id')
    sender_address_state_name = fields.Char('Nombre de estado')
    sender_address_neighborhood_name = fields.Char('Nombre del vecindario')
    sender_address_geolocation_last_updated = fields.Datetime('Última actualización de la geolocalización')
    sender_address_longitude = fields.Char('Longitud')
    
    # Sibling
    sibling_reason = fields.Char('Razón')
    sibling_sibling_id = fields.Char('Id hermano')
    sibling_description = fields.Char('Descripción')
    sibling_source = fields.Char('Fuente')
    sibling_date_created = fields.Datetime('Fecha de creación')
    sibling_last_updated = fields.Datetime('Fecha de última actualización')

    
    return_tracking_number = fields.Integer('Número de tracking de regreso')
    site_id = fields.Char('Id de sitio')
    carrier_info = fields.Char('Información del operador')
    market_place = fields.Char('Mercado')


    #Receiver address
    receiver_address_country_name = fields.Char('Nombre de país')
    receiver_address_address_line = fields.Char('Dirección')
    receiver_address_scoring = fields.Char('Puntuación')
    receiver_address_agency = fields.Char('Agencia')
    receiver_address_city_name = fields.Char('Ciudad')
    receiver_address_geolocation_type = fields.Char('Tipo de geolocalización')
    receiver_address_latitude = fields.Char('Latitud')
    receiver_address_municipality_name = fields.Char('Nombre de municipalidad')
    receiver_address_location_id = fields.Char('Id de locación')
    receiver_address_street_name = fields.Char('Nombre de la calle')
    receiver_address_zip_code = fields.Char('Código ZIP')
    receiver_address_geolocation_source = fields.Char('Fuente de geolocalización')
    receiver_address_delivery_preference = fields.Char('Preferencia de entrega')
    receiver_address_intersection = fields.Char('Intersección')
    receiver_address_street_number = fields.Char('Número de la calle')
    receiver_address_comment = fields.Char('Comentario')
    receiver_address_id = fields.Char('Id')
    receiver_address_state_name = fields.Char('Nombre de estado')
    receiver_address_neighborhood_name = fields.Char('Nombre del vecindario')
    receiver_address_geolocation_last_updated = fields.Datetime('Última actualización de la geolocalización')
    receiver_address_receiver_phone = fields.Char('Teléfono del receptor')
    receiver_address_longitude = fields.Char('Longitud')


    customer_id = fields.Char('Id de cliente')
    order_id = fields.Char('Id de orden')
    status = fields.Char('Estado')
    logistic_type = fields.Char('Tipo de logística')



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
