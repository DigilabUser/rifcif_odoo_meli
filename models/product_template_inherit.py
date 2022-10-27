# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import requests
import json
import base64
import logging
_logger = logging.getLogger(__name__)

API_URI = 'https://api.mercadolibre.com'
USERS_URI = API_URI + '/users'
ME_URI = USERS_URI + '/me'
ITEMS_URI = USERS_URI + '/{}/items/search'


class ProductTemplateInherit(models.Model):
    _inherit="product.template"
    
    shipping_type = fields.Selection([
        ('full', 'Full'),
        ('notfull', 'Not Full')
    ], string='Tipo de envío', default='notfull')
    meli_product_id = fields.Char('MeLi ID')
    source_store = fields.Char('Tienda origen')

    def getImage(self, url):
        return base64.b64encode(requests.get(url).content)

    def testing_python(self):
        #Obtener el token
        connector_obj = self.env['meli.connector'].search([])
        for conn in connector_obj:
            token = conn.token
        header = {'Authorization': 'Bearer '+ token}
        #Autenticar
        response_user_me = requests.get(ME_URI, headers=header)
        json_user_me= json.loads(response_user_me.text)
        _logger.info(json_user_me)
        #Obtener items asociados al usuario
        url_items = ITEMS_URI.format(json_user_me['id'])
        response_items = requests.get(url_items, headers=header)
        json_items = json.loads(response_items.text)
        #Obtener detalle por cada item
        for item in json_items['results']:
            url_inventory = 'https://api.mercadolibre.com/items/{}'.format(item)
            response_inventory = requests.get(url_inventory, headers=header)
            json_inventory = json.loads(response_inventory.text)
            if (len(json_inventory) > 0):
                prod_obj = {
                    #'id': json_inventory['id'],
                    'name': json_inventory['title'],
                    'list_price': float(json_inventory['price']),
                    'standard_price': float(json_inventory['base_price']),
                    'meli_product_id':json_inventory['id'],
                    #'description_sale': json_inventory['descriptions'][0] if len['descriptions']>0 else '',
                    #'listing_type_id': json_inventory['listing_type_id'],
                    'image_1920': self.getImage(json_inventory['pictures'][0]['url']),
                    'qty_available': json_inventory['available_quantity'],
                    #'buying_mode': json_inventory['buying_mode'],
                    #'currency_id': json_inventory['currency_id'],
                    'type': 'product',
                    'shipping_type': 'full' if json_inventory['shipping']['logistic_type'] == 'fulfillment' else 'notfull',
                    #'condition': json_inventory['condition']
                    'sale_ok':True,
                    'source_store':'MercadoLibre'
                }
                qty_products = self.env['product.template'].search([('meli_product_id','=',json_inventory['id'] )])
                
                if len(qty_products) == 0:
                    self.env['product.template'].sudo().create(prod_obj)
                else:
                    qty_products.sudo().write(prod_obj)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }