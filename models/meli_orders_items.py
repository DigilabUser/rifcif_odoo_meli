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

class MercadolibreOrdersItems(models.Model):
    _name = 'meli.order.items'

    order_id = fields.Many2one('meli.order', string='order')
    item_id = fields.Char("Item ID")
    isbn = fields.Char("ISBN")
    title = fields.Char("Titulo")
    #product_id = fields.Many2one('product.template', string='Producto')
    quantity= fields.Integer('Cantidad')
    sale_fee= fields.Float('Tarifa de venta') 
    listing_type= fields.Char('Tipo de listado') 
    unit_price= fields.Float('Precio unitario') 
    full_unit_price= fields.Float('Precio unitario FULL') 
    base_exchange_rate= fields.Float('Tipo de cambio') 
    currency_id= fields.Char('Moneda')

    #Categoria
    category_id = fields.Char('Categoria')
    #Iventario
    inventory_id = fields.Char('Inventario')
    #geolocalizacion
    geolocation = fields.Char('Geolocalización')
    #permalink
    permalink = fields.Char('Enlace Permanente')
    #condicion
    condition = fields.Char('Condicion')
    #Idioma
    language = fields.Char('Idioma')
    #Edad maxima recomendada
    max_recommended_age = fields.Char('Edad maxima recomendada')
    #Altura del paquete
    package_height = fields.Char('Altura del paquete')
    #Peso del paquete
    package_weight = fields.Char('Peso del paquete')
    #Año de publicación 
    publication_year = fields.Char('Año de publicación')
    #Garantia
    warranty = fields.Char('Garantia') 

    shipping_cost = fields.Float('Costo de envio')
    paid_amount = fields.Float('Monto de pago')