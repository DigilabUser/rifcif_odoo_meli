# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json
from odoo.exceptions import ValidationError
import logging
import base64
import datetime
from datetime import datetime
from datetime import timedelta
_logger = logging.getLogger(__name__)
API_URI = 'https://api.mercadolibre.com'
USERS_URI = API_URI + '/users'
ME_URI = USERS_URI + '/me'
ITEMS_URI = API_URI + '/items'
ITEM_URI = API_URI + '/items' + '/{}'
#SEARCH_ITEM_URI = USERS_URI + '/{}/items/search&sort=date_desc&'
ORDERS_URI =API_URI + '/orders'
SHIPMENTS_URI = ORDERS_URI + '/{}/shipments'
#GET_ORDER = ORDERS_URI + '/search?seller={}&order.date_created.from=2022-11-09T00:00:00.000-00:00&order.date_created.to=2022-11-10T00:00:00.000-00:00&sort=date_desc'
GET_ORDER = ORDERS_URI + '/search?seller={}&order.date_created.from={}&order.date_created.to={}&sort=date_desc&limit={}&offset={}'
ALBERT_ID='422252521'
PRINT_TICKET_URI = API_URI + '/shipment_labels?shipment_ids={}&response_type=pdf'

class MLOrderWizard(models.TransientModel):
    _name = 'meli.order.wizard'

    date_from = fields.Datetime('Fecha Inicial', default=datetime.now().replace(hour=00, minute=00, second=1)+timedelta(hours=3))
    date_to = fields.Datetime('Fecha Final', default=datetime.now().replace(hour=23, minute=59, second=59)+timedelta(hours=3))

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
        counter = 0
        #Obtener las ordenes
        date_init_formatted = str(self.date_from).replace(" ","T")+'.000-00:00'
        date_end_formatted = str(self.date_to).replace(" ","T")+'.000-00:00'        
        while(there_is_orders):
            offset = (current_page - 1) * limit
            url_orders = GET_ORDER.format(json_user_me['id'],date_init_formatted,date_end_formatted, limit,offset)
            response_orders = requests.get(url_orders, headers=header)
            #Se transforma la respuesta en formato JSON
            json_orders = json.loads(response_orders.text)
            #print(json_orders)
            # if str(json_orders["status"]) == '4':
            #     raise ValidationError(json_orders["message"])
            data = json_orders["results"]
            if len(data)!= 0:
                for order in data:
                    #print(order)
                    obj={}
                    obj["ml_order_id"] = order["id"]
                    obj["seller_nickname"]=order["seller"]["nickname"]
                    obj["seller_id"]=order["seller"]["id"]
                    obj["fulfilled"]=order["fulfilled"]
                    obj["taxes_amount"]=order["taxes"]["amount"]
                    obj["order_request_change"]=order["order_request"]["change"]
                    obj["order_request_return"]=order["order_request"]["return"]
                    obj["expiration_date"]=datetime(int(order["expiration_date"][0:4]),int(order["expiration_date"][5:7]),int(order["expiration_date"][8:10]),int(order["expiration_date"][11:13]),int(order["expiration_date"][14:16]),int(order["expiration_date"][17:19]))+timedelta(hours=5)
                    #obj["feedback_sale"]=order["feedback"]["sale"]
                    #obj["feedback_purchase"]=order["feedback"]["purchase"]
                    obj["shipping_id"]=order["shipping"]["id"]
                    obj["date_closed"]=datetime(int(order["date_closed"][0:4]),int(order["date_closed"][5:7]),int(order["date_closed"][8:10]),int(order["date_closed"][11:13]),int(order["date_closed"][14:16]),int(order["date_closed"][17:19]))+timedelta(hours=5)
                    obj["manufacturing_ending_date"]=order["manufacturing_ending_date"]
                    #obj["hidden_for_seller"]=order["hidden_for_seller"]
                    obj["date_last_updated"]=datetime(int(order["last_updated"][0:4]),int(order["last_updated"][5:7]),int(order["last_updated"][8:10]),int(order["last_updated"][11:13]),int(order["last_updated"][14:16]),int(order["last_updated"][17:19]))+timedelta(hours=5)
                    obj["last_updated"]=datetime(int(order["last_updated"][0:4]),int(order["last_updated"][5:7]),int(order["last_updated"][8:10]),int(order["last_updated"][11:13]),int(order["last_updated"][14:16]),int(order["last_updated"][17:19]))+timedelta(hours=5)
                    #obj["comments"]=order["comments"]
                    obj["pack_id"]=order["pack_id"]
                    obj["coupon_amount"]=order["coupon"]["amount"]
                    obj["coupon_id"]=order["coupon"]["id"]
                    obj["shipping_cost"]=(int(order["paid_amount"]) - int(order["total_amount"]))/(1.19)
                    obj["date_created"]=datetime(int(order["date_created"][0:4]),int(order["date_created"][5:7]),int(order["date_created"][8:10]),int(order["date_created"][11:13]),int(order["date_created"][14:16]),int(order["date_created"][17:19]))+timedelta(hours=5)
                    #obj["application_id"]=order["application_id"]
                    obj["pickup_id"]=order["pickup_id"]
                    obj["status_detail"]=order["status_detail"]
                    obj["buyer_nickname"]=order["buyer"]["nickname"]
                    obj["buyer_id"]=order["buyer"]["id"]
                    obj["total_amount"]=order["total_amount"]
                    obj["paid_amount"]=order["paid_amount"]
                    obj["status"]=order["status"]                   
                    #print(obj)

                    order_exist= self.env['meli.order'].search([("ml_order_id","=",obj["ml_order_id"])])
                    if len(order_exist)==0:
                        res = self.env["meli.order"].sudo().create(obj)
                        #Aca me traigo los items
                        for item in order["order_items"]:
                            print("ITEM={}".format(item))
                            url_item = ITEM_URI.format(item["item"]["id"])
                            response_item = requests.get(url_item, headers=header)
                            json_item = json.loads(response_item.text)
                            #obtengo el ISBN
                            isbn = ""
                            lang = ""
                            cond = ""
                            max_age = "" 
                            height = ""
                            weight = ""
                            publi = ""
                            for rec in json_item["attributes"]:
                                if rec["id"] == "GTIN":
                                    isbn=rec["value_name"]
                                if rec["id"] == "LANGUAGE":
                                    lang = rec["value_name"]
                                if rec["id"] == "ITEM_CONDITION":
                                    cond = rec["value_name"] 
                                if rec["id"] == "MAX_RECOMMENDED_AGE":
                                    max_age = rec["value_name"]
                                if rec["id"] == "PACKAGE_HEIGHT":
                                    height = rec["value_name"]
                                if rec["id"] == "PACKAGE_WEIGHT":
                                    weight = rec["value_name"]
                                if rec["id"] == "PUBLICATION_YEAR":
                                    publi = rec["value_name"]
                                
                            print(json_item)
                            obj_item={}
                            obj_item["order_id"] = res.id
                            obj_item["title"] = item["item"]["title"]
                            obj_item["item_id"] = item["item"]["id"]
                            obj_item["isbn"] = isbn
                            obj_item["quantity"]=item["quantity"]
                            obj_item["sale_fee"]=item["sale_fee"]
                            obj_item["listing_type"]=item["listing_type_id"]
                            obj_item["unit_price"]=item["unit_price"]
                            obj_item["full_unit_price"]=item["full_unit_price"]
                            obj_item["base_exchange_rate"]=item["base_exchange_rate"]
                            obj_item["currency_id"]=item["currency_id"]
                            #categoria
                            obj_item['category_id'] = json_item['category_id']
                            #iventario
                            obj_item['inventory_id']=json_item['inventory_id']
                            #geolocalizacion
                            obj_item["geolocation"]="https://www.google.com/maps/@{},{},15z".format(str(json_item["geolocation"]["latitude"]), str(json_item["geolocation"]["longitude"]))
                            #permalink
                            obj_item['permalink']=json_item['permalink']
                            #condicion orden[22]
                            obj_item['condition']=cond
                            #Idioma orden[23]
                            obj_item['language']=lang
                            #Edad maxima recomendada orden[25]
                            obj_item['max_recommended_age']=max_age
                            #Altura del paquete orden[28]
                            obj_item['package_height']=height
                            #Peso del paquete orden[30]
                            obj_item['package_weight']=weight
                            #Año de publicación orden[34]
                            obj_item['publication_year']=publi
                            #Garantia
                            obj_item['warranty'] = json_item['warranty']
                            #Aca Crea
                            self.env["meli.order.items"].sudo().create(obj_item)
                        for payment in order["payments"]:
                            obj_payment={}
                            obj_payment["order_id"] = res.id
                            obj_payment["reason"] = payment["reason"]
                            obj_payment["status_code"] = payment["status_code"]
                            obj_payment["total_paid_amount"]=payment["total_paid_amount"]
                            obj_payment["operation_type"]=payment["operation_type"]
                            obj_payment["transaction_amount"]=payment["transaction_amount"]
                            obj_payment["collector_id"]=payment["collector"]["id"]
                            obj_payment["payment_id"]=payment["id"]
                            obj_payment["shipping_cost"]=payment["shipping_cost"]
                            obj_payment["currency_id"]=payment["currency_id"]
                            self.env["meli.order.payments"].sudo().create(obj_payment)

                        counter +=1
                        print(counter)
                    else:
                        pass
                current_page += 1
            else: 
                there_is_orders = False
        print("Se crearon {} registros".format(counter))