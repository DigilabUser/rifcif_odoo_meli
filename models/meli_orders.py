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
ORDERS_URI = API_URI + '/orders/'
BILLING_URI = ORDERS_URI + '{}/billing_info'

class MercadolibreOrders(models.Model):
    _name = 'meli.order'
    _rec_name="ml_order_id"

    #campos relacionados
    item_ids = fields.One2many('meli.order.items', 'order_id', string='Items')
    payment_ids = fields.One2many('meli.order.payments', 'order_id', string='payment')
    current_page = fields.Integer(default=1)
    #orders = fields.One2many('meli.order', 'order_id')
    # Order fieldsellerr el modelo

    # Seller
    seller_nickname = fields.Char('Nombre del vendedor')
    seller_id = fields.Char('Id del vendedor')

    fulfilled = fields.Boolean('Fulfilled')
    buying_mode = fields.Char('Modo de compra')
    # Taxes
    taxes_amount = fields.Float('Impuestos')
 
    # order_request
    order_request_change = fields.Char('Cambio de pedido')
    order_request_return = fields.Char('Retorno de pedido')

    expiration_date = fields.Datetime('Fecha de caducidad')
    # Feedback
    feedback_sale = fields.Char('Venta')
    feedback_purchase = fields.Char('Comprar')
    # Shipping
    shipping_id = fields.Char('N° de Envío')

    date_closed = fields.Datetime('Fecha de cierre')

    ml_order_id = fields.Char('N° Orden')
    
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
    buyer_nickname = fields.Char('Nombre comprador')
    buyer_id = fields.Char('Comprador')
    total_amount = fields.Integer('Cantidad total')
    paid_amount = fields.Float('Monto de pago')
    status= fields.Char('Estado')
    logistic_type = fields.Char('Tipo de logística')
    shipping_status = fields.Char('Estado de envío')
    sale_order_id = fields.Many2one('sale.order', string='Orden de Venta')
    delivery_address = fields.Char('Dirección de entrega')


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

    def create_sale_order_from_meli_order(self):

        #Obtener el token
        connector_obj = self.env['meli.connector'].search([])
        for conn in connector_obj:
            token = conn.token
        header = {'Authorization': 'Bearer '+ token}       
        #Traerme todas las ordenes descargadas


        #Me traigo todas las MELI order que sean not full
        meli_order_ids = self.env['meli.order'].search([('logistic_type','=','not full'),('sale_order_id','=',False)])
        #Las recorro
        for meli_order in meli_order_ids:

            #aca creo mi cliente.
            #Consumir el API BILLING con el meli_order["ml_order_id"]
            #https://api.mercadolibre.com/orders/{}/billing_info <--- de aca vas a traer el doc_number
            #Hacer busqueda con el numero de doc partner_exist = self.env["res.partner"].search([('vat','=',numero de documento)])
            #json_billing = self.get_data_from_api(url_billing,header)
            #--------
            
            order_id= meli_order["ml_order_id"]
            url_billing= BILLING_URI.format(order_id)
            json_billing= self.get_data_from_api(url_billing, header)
            
            #print(json_billing)
            

            number_doc = json_billing["billing_info"]["doc_number"]

            partner_exist = self.env["res.partner"].search([('vat','=',number_doc)])

            # Variables locales
            data_name = ""
            data_lastname = ""
            data_ruc = ""
            data_stree_name = ""
            data_stree_number = ""
            # data_las_name = ""

            for data in json_billing["billing_info"]["additional_info"]:
                # if data["type"] == "LAST_NAME":
                #     data_las_name= data["value"]
                if data["type"] == "DOC_NUMBER":
                    data_ruc = data["value"]
                if data["type"] == "FIRST_NAME":
                    data_name = data["value"]
                if data["type"] == "LAST_NAME":
                    data_lastname = data["value"]                    
                if data["type"] == "STREET_NAME":
                    data_stree_name = data["value"]
                if data["type"] == "STREET_NUMBER":
                    data_stree_number = data["value"]

            data_name = data_name + " " + data_lastname
            data_street =  data_stree_name + " " + data_stree_number
            # print(data_name)
            # print(data_las_name)
            # print(data_ruc)

            # #El cliente no existe
            if len(partner_exist)==0:
                 # Si el cliente no existe, lo creo
                new_partner = self.env['res.partner'].sudo().create({
                    'name': data_name,
                    #'lastname': data_las_name,
                    'vat': data_ruc,
                    'street': data_street,
                    'customer_rank':1
                })
                partner_exist = new_partner
            # ---------
            # aca voy a crear mi orden de venta
            obj={}
            obj['partner_id']=partner_exist['id']
            obj['order_ml']=meli_order['ml_order_id']
            #obj['partner_invoice_id'] = partner_exist['street']
            #obj['vat'] = partner_exist['vat']
            obj['date_order']=meli_order['date_created']
            obj['amount_total']=meli_order['total_amount']             
            sale_order = self.env["sale.order"].create(obj)

            for line in meli_order["item_ids"]:

                product_id = self.env['product.template'].search([('isbn','=', line['isbn'])])
                if product_id:
                    line_vals = {
                        'order_id': sale_order.id,
                        'product_id': product_id.id,
                        'product_uom_qty': line['quantity'],
                        'price_unit': line['unit_price'],
                        'name': line['title'],
                        'display_type': False,
                    }
                    print(line_vals)
                    self.env['sale.order.line'].create(line_vals)
            order= self.env['sale.order'].search([('id','=',sale_order.id)])
            meli_order.sudo().write({
                'sale_order_id':order.id
            })