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

class MercadolibreItems(models.Model):
    _name = 'meli.items'
    _rec_name="title"

    # Vista tree

    id_items = fields.Char('Id de item')
    title = fields.Char('Titulo')
    price = fields.Char('Precio')
    inventory_id = fields.Char('Id de inventario')
    currency_id = fields.Char('Id de moneda')
    initial_quantity = fields.Integer('Cantidad inicial')
    available_quantity = fields.Integer('Cantidad disponible')
    sold_quantity = fields.Integer('Cantidad vendidad')
    logistic_type = fields.Char('Tipo de logistica')

    # Vista Form

    category_id = fields.Char('Id de categoria')
    base_price = fields.Char('Precio base')
    condition= fields.Char('Condición del item')
    warranty = fields.Char('Tipo de garantia') # Preguntar
    permalink = fields.Char('Link permanente')
    pictures = fields.Char('Imagen') # Preguntar
    geolocation = fields.Char('Localización')
    author = fields.Char('Autor') # Preguntar
    book_cover = fields.Char('Tipo de tapa')
    book_genre = fields.Char('Género del libro')
    isbn = fields.Char('Codigo de barra')
    language = fields.Char('Idioma')
    max_recommended_age = fields.Char('Edad maxima recomendada')
    tags = fields.Char('Tags')

    def create_items_from_meli_items(self):
        pass