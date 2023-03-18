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
    
    snapshot_packing = fields.Char('Paquete instantánea') # Ya esta
    receiver_id = fields.Char('Id del destinatario') # Ya esta
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
    cost_components_loyal_discount = fields.Float('Descuento')
    cost_components_special_discount = fields.Float('Descuento especial')
    cost_components_compensation = fields.Float('Compensasión')
    cost_components_gap_discount = fields.Float('Descuento brecha')
    cost_components_ratio = fields.Char('Relación')

    shipping_id = fields.Char('N° de envío')
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
            shipment_id = order["ml_order_id"]
            url_shipments = SHIPMENTS_URI.format(order["ml_order_id"])
            json_shipments = self.get_data_from_api(url_shipments,header)
            print(json_shipments)
            if json_shipments["status"]!=404:
                print("\n\n---------------\n\n")
                print(json_shipments)
                obj={}
                obj["shipment_id"] = json_shipments["id"]
                obj["receiver_id"] = json_shipments["receiver_id"]
                obj["snapshot_packing"] = json_shipments["snapshot_packing"]
                obj["base_cost"]=json_shipments["base_cost"]

                #Status_history
                obj["date_shipped"]=json_shipments["status_history"]["date_shipped"]
                obj["date_returned"]=json_shipments["status_history"]["date_returned"]
                obj["date_delivered"]=json_shipments["status_history"]["date_delivered"]
                obj["date_first_visit"]=json_shipments["status_history"]["date_first_visit"]
                obj["date_not_delivered"]=json_shipments["status_history"]["date_not_delivered"]
                obj["date_cancelled"]=json_shipments["status_history"]["date_cancelled"]
                obj["date_handling"]=json_shipments["status_history"]["date_handling"]
                obj["date_ready_to_ship"]=json_shipments["status_history"]["date_ready_to_ship"]

                obj["type"]=json_shipments["type"]
                obj["return_details"]=json_shipments["return_details"]
                obj["sender_id"]=json_shipments["sender_id"]
                obj["mode"]=json_shipments["mode"]
                obj["order_cost"]=json_shipments["order_cost"]
                obj["service_id"]=json_shipments["service_id"]
                obj["tracking_number"]=json_shipments["tracking_number"]

                # cost_components
                obj["cost_components_loyal_discount"]=json_shipments["cost_components"]["loyal_discount"]
                obj["cost_components_special_discount"]=json_shipments["cost_components"]["special_discount"]
                obj["cost_components_compensation"]=json_shipments["cost_components"]["compensation"]
                obj["cost_components_gap_discount"]=json_shipments["cost_components"]["gap_discount"]
                obj["cost_components_ratio"]=json_shipments["cost_components"]["ratio"]

                obj["id"]=json_shipments["id"]
                obj["tracking_method"]=json_shipments["tracking_method"]
                obj["last_updated"]=json_shipments["last_updated"]
                obj["items_types"]=json_shipments["items_types"]
                obj["comments"]=json_shipments["comments"]
                obj["substatus"]=json_shipments["substatus"]
                obj["date_created"]=json_shipments["date_created"]
                obj["date_first_printed"]=json_shipments["date_first_printed"]
                obj["created_by"]=json_shipments["created_by"]
                obj["application_id"]=json_shipments["application_id"]
                
                #Sender address
                obj["sender_address_country_name"]=json_shipments["sender_address"]["country"]["name"]
                obj["sender_address_address_line"]=json_shipments["sender_address"]["address_line"]
                obj["sender_address_scoring"]=json_shipments["sender_address"]["scoring"]
                obj["sender_address_agency"]=json_shipments["sender_address"]["agency"]
                obj["sender_address_city_name"]=json_shipments["sender_address"]["city"]["name"]
                obj["sender_address_geolocation_type"]=json_shipments["sender_address"]["geolocation_type"]
                obj["sender_address_latitude"]=json_shipments["sender_address"]["latitude"]
                obj["sender_address_municipality_name"]=json_shipments["sender_address"]["municipality"]["name"]
                obj["sender_address_location_id"]=json_shipments["sender_address"]["location_id"]
                obj["sender_address_street_name"]=json_shipments["sender_address"]["street_name"]
                obj["sender_address_zip_code"]=json_shipments["sender_address"]["zip_code"]
                obj["sender_address_geolocation_source"]=json_shipments["sender_address"]["geolocation_source"]
                obj["sender_address_intersection"]=json_shipments["sender_address"]["intersection"]
                obj["sender_address_street_number"]=json_shipments["sender_address"]["street_number"]
                obj["sender_address_comment"]=json_shipments["sender_address"]["comment"]
                obj["sender_address_id"]=json_shipments["sender_address"]["id"]
                obj["sender_address_state_name"]=json_shipments["sender_address"]["state"]["name"]
                obj["sender_address_neighborhood_name"]=json_shipments["sender_address"]["neighborhood"]["name"]
                obj["sender_address_geolocation_last_updated"]=json_shipments["sender_address"]["geolocation_last_updated"]
                obj["sender_address_longitude"]=json_shipments["sender_address"]["longitude"]

                # Sibling
                obj["sibling_reason"] = json_shipments["sibling"]["reason"]
                obj["sibling_sibling_id"] = json_shipments["sibling"]["sibling_id"]
                obj["sibling_description"] = json_shipments["sibling"]["description"]
                obj["sibling_source"] = json_shipments["sibling"]["source"]
                obj["sibling_date_created"] = json_shipments["sibling"]["date_created"]
                obj["sibling_last_updated"] = json_shipments["sibling"]["last_updated"]

                obj["return_tracking_number"] = json_shipments["return_tracking_number"]
                obj["site_id"] = json_shipments["site_id"]
                obj["carrier_info"] = json_shipments["carrier_info"]
                obj["market_place"] = json_shipments["market_place"]

                #Receiver address
                obj["receiver_address_country_name"] = json_shipments["receiver_address"]["country"]["name"]
                obj["receiver_address_address_line"] = json_shipments["receiver_address"]["address_line"]
                #obj["receiver_address_scoring"] = json_shipments["receiver_address"]["scoring"]
                obj["receiver_address_agency"] = json_shipments["receiver_address"]["agency"]
                obj["receiver_address_city_name"] = json_shipments["receiver_address"]["city"]["name"]
                obj["receiver_address_geolocation_type"] = json_shipments["receiver_address"]["geolocation_type"]
                obj["receiver_address_latitude"] = json_shipments["receiver_address"]["latitude"]
                obj["receiver_address_municipality_name"] = json_shipments["receiver_address"]["municipality"]["name"]
                #obj["receiver_address_location_id"] = json_shipments["receiver_address"]["location_id"]
                obj["receiver_address_street_name"] = json_shipments["receiver_address"]["street_name"]
                obj["receiver_address_zip_code"] = json_shipments["receiver_address"]["zip_code"]
                obj["receiver_address_geolocation_source"] = json_shipments["receiver_address"]["geolocation_source"]
               #obj["receiver_address_delivery_preference"] = json_shipments["receiver_address"]["delivery_preference"]
                obj["receiver_address_intersection"] = json_shipments["receiver_address"]["intersection"]
                obj["receiver_address_street_number"] = json_shipments["receiver_address"]["street_number"]
                obj["receiver_address_comment"] = json_shipments["receiver_address"]["comment"]
                obj["receiver_address_id"] = json_shipments["receiver_address"]["id"]
                obj["receiver_address_state_name"] = json_shipments["receiver_address"]["state"]["name"]
                obj["receiver_address_neighborhood_name"] = json_shipments["receiver_address"]["neighborhood"]["name"]
                obj["receiver_address_geolocation_last_updated"] = json_shipments["receiver_address"]["geolocation_last_updated"]
                obj["receiver_address_receiver_phone"] = json_shipments["receiver_address"]["receiver_phone"]
                obj["receiver_address_longitude"] = json_shipments["receiver_address"]["longitude"]

                obj["customer_id"] = json_shipments["customer_id"]
                obj["order_id "] = json_shipments["order_id"]
                obj["status"] = json_shipments["status"]
                obj["logistic_type"] = json_shipments["logistic_type"]
                
                #Aqui estoy actualizando ciertos campos del meli.order
                order.sudo().write({
                    'logistic_type':json_shipments["logistic_type"] if json_shipments["logistic_type"]=="fulfillment" else "not full",
                    'shipping_status':json_shipments["status"]
                })

                #self.env["meli.shipments"].create(obj)
