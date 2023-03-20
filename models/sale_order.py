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
ORDERS_URI =API_URI + '/orders'
GET_ORDER = ORDERS_URI + '/search?seller={}&order.status=paid'
ALBERT_ID='422252521'
class SaleOrderInherit(models.Model):
    _inherit="sale.order"
    
    order_ml = fields.Char('N° Orden ML')