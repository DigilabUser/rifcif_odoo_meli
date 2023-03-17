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
USERS_URI = API_URI + '/users'
ME_URI = USERS_URI + '/me'
ITEMS_URI = API_URI + '/items'
ITEM_URI = API_URI + '/items' + '/{}'
#SEARCH_ITEM_URI = USERS_URI + '/{}/items/search&sort=date_desc&'
ORDERS_URI =API_URI + '/orders'
SHIPMENTS_URI = ORDERS_URI + '/{}/shipments'
#GET_ORDER = ORDERS_URI + '/search?seller={}&order.status=paid'
GET_ORDER = ORDERS_URI + '/search?seller={}&limit={}&offset={}'
PRINT_TICKET_URI = API_URI + '/shipment_labels?shipment_ids={}&response_type=pdf'
ALBERT_ID='422252521'

class MercadolibreShipments(models.Model):
    _name = 'meli.shipments'

    