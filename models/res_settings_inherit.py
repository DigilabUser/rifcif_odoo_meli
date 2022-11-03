# -*- coding: utf-8 -*-
import logging
import requests
import json
from odoo import models, fields, api
_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    meli_client_id = fields.Char('Client ID', store=True)
    meli_key_id = fields.Char('Key ID', store=True)


    def execute(self):
        CLIENT_ID = self.meli_client_id
        CLIENT_SECRET = self.meli_key_id
        url = 'https://api.mercadolibre.com/oauth/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(CLIENT_ID, CLIENT_SECRET)
        response = requests.post(url)
        json_obj = json.loads(response.text)
        _logger.info("------------------------- Credenciales MERCADOLIBRE ---------------------------")
        _logger.info(CLIENT_ID)
        _logger.info(CLIENT_SECRET)
        _logger.info(json_obj)
        _logger.info("------------------------------------------------------------------------------")

        self.meli_token = json_obj['access_token']  
                
    meli_token = fields.Char('Token',compute=execute)
    # def connect(self):

    #     CLIENT_ID = self.meli_client_id
    #     CLIENT_SECRET = self.meli_key_id
    #     url = 'https://api.mercadolibre.com/oauth/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(CLIENT_ID, CLIENT_SECRET)
    #     response = requests.post(url)
    #     json_obj = json.loads(response.text)
    #     self.meli_token = json_obj['access_token']    


