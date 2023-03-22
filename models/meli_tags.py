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

class MercadolibreTag(models.Model):
    _name = 'meli.tags'
    
    name = fields.Char('Nombre')
    color_numb = fields.Integer('Numero color')