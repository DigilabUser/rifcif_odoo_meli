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
    move_id = fields.Many2one('account.move', string='Factura/Boleta Electrónica')
    delivery_address = fields.Char('Dirección de entrega')

    type_doc = fields.Char('Tipo de documento')
    rut_user = fields.Char('Rut')


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

    def create_invoice_from_ml_orders(self, meli_order_id):
        if meli_order_id["sale_order_id"]:
            sale_id = self.env["sale.order"].search([("id", "=", meli_order_id["sale_order_id"]["id"])])
            document_class_type = "Factura Electrónica" if meli_order_id["type_doc"]=="factura" else "Boleta Electrónica" 
            document_class_type_id = self.env["sii.document_class"].search([("name","=",document_class_type)])
            sii_class_type_id = self.env["account.journal.sii_document_class"].search([("sii_document_class_id","=",document_class_type_id.id)])
            document_type_code = "33" if meli_order_id["type_doc"]=="factura" else "39" 
            document_type_code_id = self.env["l10n_latam.document.type"].search([("code","=",document_type_code)])
            #Creo las lineas de factura
            move_lines = []
            for item in sale_id["order_line"]:             
                move_lines.append( (0, 0, { 
                            'date':meli_order_id["date_created"], 
                            'journal_id':1,
                            'company_id':1, 
                            'company_currency_id':45,
                            'partner_id':meli_order_id["sale_order_id"]["partner_id"]["id"],
                            'product_id':item.product_id.id,
                            'name':item.name,
                            'quantity':item.product_uom_qty,
                            'price_unit':item.price_unit, 
                            'price_subtotal':item.price_subtotal,
                            'is_gd_line':False, 
                            'is_gr_line':False, 
                            'is_retention':False,
                            'product_uom_id':1, 
                            'currency_id':45, 
                            'exclude_from_invoice_tab':False, 
                            'tax_ids':[1]  
                            }))             
            #creo mi objeto para la factura
            obj={}
            obj["use_documents"]=True
            obj["journal_document_class_id"]= sii_class_type_id.id
            obj["document_class_id"] = document_class_type_id
            obj["partner_id"]=meli_order_id["sale_order_id"]["partner_id"]["id"]
            obj["l10n_latam_document_type_id"]= document_type_code_id.id
            obj['journal_id']=1
            obj['move_type']='out_invoice'
            obj['invoice_origin']=meli_order_id["sale_order_id"]["name"]
            obj['company_id']=1,
            obj['currency_id']=45
            obj['amount_untaxed']=meli_order_id["sale_order_id"]['amount_total']
            obj['meli_order_id']=meli_order_id["id"]
            obj['invoice_line_ids']= move_lines #Coloco las lineas de factura aca

            #Creo mi orden
            order_id=self.env["account.move"].sudo().create(obj)
            meli_order_id.write({'move_id':order_id.id})
             





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
            
            order_id= meli_order["ml_order_id"]
            url_billing= BILLING_URI.format(order_id)
            json_billing= self.get_data_from_api(url_billing, header)    

            number_doc = json_billing["billing_info"]["doc_number"]
            meli_order.write({'rut_user':number_doc})

            # Variables locales
            data_name = ""
            data_lastname = ""
            data_ruc = ""
            data_stree_name = ""
            data_stree_number = ""
            # data_las_name = ""

            for data in json_billing["billing_info"]["additional_info"]:
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

            #Busco al cliente
            partner_exist = self.env["res.partner"].search([('vat','=',number_doc)])
            if len(partner_exist)==0:
                 # Si el cliente no existe, lo creo
                new_partner = self.env['res.partner'].sudo().create({
                    'name': data_name,
                    #'lastname': data_las_name,
                    'vat': data_ruc,
                    'document_number': data_ruc,
                    'street': data_street,
                    'l10n_cl_sii_taxpayer_type':1 if self.type_doc=='factura' else 3,
                    'customer_rank':1
                })
                partner_exist = new_partner
            # aca voy a crear mi orden de venta
            obj={}
            obj['partner_id']=partner_exist['id']
            obj['order_ml']=meli_order['ml_order_id']
            obj['date_order']=meli_order['date_created']
            obj['amount_total']=meli_order['total_amount']  

            #Verifico si es una meli_orden en paquete
            if(meli_order["pack_id"] == False):
                #Si no es paquete, creo la orden
                sale_order = self.env["sale.order"].create(obj)
                #Creo las lineas de pedido
                for line in meli_order["item_ids"]:
                    product_id = self.env['product.template'].search([('isbn','=', line['isbn'])])
                    if product_id:
                        line_vals = {
                            'order_id': sale_order.id,
                            'product_id': product_id.id,
                            'product_uom_qty': line['quantity'],
                            'price_unit': int(line['unit_price'])*(1.19),
                            'name': line['title'],
                            'display_type': False,
                            }
                        print(line_vals)
                        self.env['sale.order.line'].create(line_vals)
                #Busco la orden creada
                order= self.env['sale.order'].search([('id','=',sale_order.id)])
                #Actualizo el campo para la trazabilidad
                meli_order.sudo().write({
                    'sale_order_id':order.id
                })
            else:
                # Si es paquete, trae los meli.order que tengan el mismo pack
                #Aqui tenemos mas de una orden => meli_order_pack
                meli_order_pack = self.env['meli.order'].search([("pack_id", "=", meli_order["pack_id"])])
                ml_order_id_pack = ""
                ml_order_date_pack=""
                ml_amount_pack=0
                for order_pack in meli_order_pack:
                    #|21312312213|12321312321|
                    ml_order_id_pack += "|"+ str(order_pack['ml_order_id']) + "|"
                    ml_order_date_pack = order_pack["date_created"]
                    ml_amount_pack +=order_pack["total_amount"]
                    
                obj={}
                obj['partner_id']=partner_exist['id']
                obj['order_ml']=ml_order_id_pack
                obj['date_order']=ml_order_date_pack
                obj['amount_total']=ml_amount_pack  
                #Creo la orden
                sale_order = self.env["sale.order"].create(obj)
                # Recorro las meli_orders con el mismo pack_id para obtener sus items
                for order_pack in meli_order_pack:
                    #Creo las lineas de pedido
                    for line in order_pack["item_ids"]:
                        product_id = self.env['product.template'].search([('isbn','=', line['isbn'])])
                        if product_id:
                            line_vals = {
                                'order_id': sale_order.id,
                                'product_id': product_id.id,
                                'product_uom_qty': line['quantity'],
                                'price_unit': int(line['unit_price'])*(1.19),
                                'name': line['title'],
                                'display_type': False,
                                }
                            print(line_vals)
                            self.env['sale.order.line'].create(line_vals)  
                    #Busco la orden creada
                    order= self.env['sale.order'].search([('id','=',sale_order.id)])
                    #Actualizo el campo para la trazabilidad
                    order_pack.sudo().write({
                        'sale_order_id':order.id
                    })                                              
                    print(order_pack['item_ids'])
            self.create_invoice_from_ml_orders(meli_order)



            