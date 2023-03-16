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
GET_ORDER = ORDERS_URI + '/search?seller={}&order.date_created.from={}&order.date_created.to={}&sort=date_desc'
ALBERT_ID='422252521'
PRINT_TICKET_URI = API_URI + '/shipment_labels?shipment_ids={}&response_type=pdf'

class MkWizard(models.TransientModel):
    _name = 'meli.sales.wizard'

    #Se define los rango de fechas con un valor por default del día de hoy a las 00:00:01 de inicio
    #y de final el dia de hoy a las 23:59:59.
    #Se pone un Timedelta de 3 para coincidir con la diferencia horaria de Chile
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
        
        #Obtener las ordenes
        date_init_formatted = str(self.date_from).replace(" ","T")+'.000-00:00'
        date_end_formatted = str(self.date_to).replace(" ","T")+'.000-00:00'
        #Se pide las ordenes en un intervalo de tiempo
        url_orders = GET_ORDER.format(json_user_me['id'], date_init_formatted,date_end_formatted)
        response_orders = requests.get(url_orders, headers=header)
        #Se transforma la respuesta en formato JSON
        json_orders = json.loads(response_orders.text)
        if str(json_orders["status"]) == '4':
            raise ValidationError(json_orders["message"])        
        #Tenemos el resultado de todas las ordenes en el data.
        data = json_orders["results"]
        for order in data:
            # Getting Shipping Data
            shipping = self.get_data_from_api(SHIPMENTS_URI.format(order["id"]), header)
            if str(shipping['status'])[0]!='4':
                sh_shipping_id = shipping["id"]
                sh_logistic_type = "full" if shipping["logistic_type"]  == "fulfillment" else "notfull"
                sh_status = shipping["status"]
                sh_status_history = shipping["status_history"]
                sh_shipping_items=shipping["shipping_items"]
                sh_tracking_method=shipping["tracking_method"]
                sh_receiver_address=shipping["receiver_address"]
                sh_geolocation_map="https://www.google.com.cl/maps/place/{},%20{}".format(sh_receiver_address["latitude"],sh_receiver_address["longitude"])
                sh_country = sh_receiver_address["country"]["name"]
                sh_city = sh_receiver_address["city"]["name"]
                sh_address_line = sh_receiver_address["address_line"]
                sh_receiver_name = sh_receiver_address["receiver_name"]
                sh_comment = sh_receiver_address["comment"]              
            else:
                raise ValidationError("El Token ha caducado, por favor generarlo de nuevo")                

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
            order_obj={
                'meli_order_id': order["id"],
                'meli_item_id':item_id,
                'meli_shipping_id':sh_shipping_id,
                'logistic_type':sh_logistic_type,
                'date_created':datetime(int(order["date_created"][0:4]),int(order["date_created"][5:7]),int(order["date_created"][8:10]),int(order["date_created"][11:13]),int(order["date_created"][14:16]),int(order["date_created"][17:19]))+timedelta(hours=5),
                'date_closed':datetime(int(order["date_closed"][0:4]),int(order["date_closed"][5:7]),int(order["date_closed"][8:10]),int(order["date_closed"][11:13]),int(order["date_closed"][14:16]),int(order["date_closed"][17:19]))+timedelta(hours=5),
                'date_updated':datetime(int(order["last_updated"][0:4]),int(order["last_updated"][5:7]),int(order["last_updated"][8:10]),int(order["last_updated"][11:13]),int(order["last_updated"][14:16]),int(order["last_updated"][17:19]))+timedelta(hours=5),
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
            #qty_order = self.env['meli.sales'].search([('meli_order_id','=',item_id)])
            qty_order = self.env['meli.sales'].search([('meli_order_id','=', order["id"])])
            
            if len(qty_order) == 0:
                self.env['meli.sales'].sudo().create(order_obj)
            else:
                qty_order.sudo().write(order_obj)


class MkWizardMultiTicket(models.TransientModel):
    _name = 'meli.multi.ticket.wizard'

    def _get_default_tickets(self):
        _logger.info("============================")
        _logger.info(self._context.get('tickets',""))
        _logger.info("============================")

        return self._context.get('tickets',"")

    meli_tickets = fields.Binary('Tickets Impresos')
    meli_orders_ids = fields.Many2many('meli.sales', string='Ordenes Mercadolibre')

    def printticket(self):
        connector_obj = self.env['meli.connector'].search([])
        for conn in connector_obj:
            token = conn.token
        header = {'Authorization': 'Bearer '+ token} 
        str_tickets = ""  
        for item in self.meli_orders_ids:
            str_tickets += item.meli_shipping_id + ','
        #Obtener el ticket
        print_uri = PRINT_TICKET_URI.format(str_tickets)
        _logger.info(print_uri)
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
            self.meli_tickets = base64.b64encode(out)
           # context = "{'tickets':"+base64.b64encode(out)+"}"      
        else:
            print(response.status_code)
           # context= ""
        return {
            #'context': context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'meli.multi.ticket.wizard',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }