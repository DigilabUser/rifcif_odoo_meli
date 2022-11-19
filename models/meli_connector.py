# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json
from odoo.exceptions import ValidationError
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)
class MkConnector(models.Model):
    _name = 'meli.connector'

    name = fields.Char(string="Name")
    client = fields.Char(string="Client")
    key = fields.Char(string="Key")
    token = fields.Char(string="Token")

    def connect(self):
        CLIENT_ID = self.client
        CLIENT_SECRET = self.key
        url = 'https://api.mercadolibre.com/oauth/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(CLIENT_ID, CLIENT_SECRET)
        try:
            response = requests.post(url)
            json_obj = json.loads(response.text)
            _logger.info(json_obj)
            self.token = json_obj['access_token']
        except ValueError:
            raise ValidationError(ValueError)