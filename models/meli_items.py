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

ALBERT_ID= '422252521'
API_URI = 'https://api.mercadolibre.com'

# Para traer items de usuario
USER_URI=  API_URI + '/users'
ITEMS_URI =  USER_URI + '/{}/items/search' 

# Para traer detalle de item
ITEM_URI = API_URI + '/items/{}'


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
    warranty = fields.Char('Tipo de garantia')
    permalink = fields.Char('Link permanente')
    pictures = fields.Binary('Imagen')
    geolocation = fields.Char('Localización')
    author = fields.Char('Autor')
    book_cover = fields.Char('Tipo de tapa')
    book_genre = fields.Char('Género del libro')
    isbn = fields.Char('Codigo de barra')
    language = fields.Char('Idioma')
    max_recommended_age = fields.Char('Edad maxima recomendada')

    tag_ids = fields.Many2many('meli.tags', string='Etiquetas')
    
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
    
    def getImage(self, url):
        '''
        Función que convierte un URL a una imagen en BASE64 para poder guardarla en un 
        campo Binary
        '''
        return base64.b64encode(requests.get(url).content)


    def create_items_from_meli_items(self):

        #Obtener el token
        connector_obj = self.env['meli.connector'].search([])
        for conn in connector_obj:
            token = conn.token
        header = {'Authorization': 'Bearer '+ token} 

        # Consumo de Api usuario
        url_items_user = ITEMS_URI.format(ALBERT_ID)
        json_items_user = self.get_data_from_api(url_items_user, header)

        # Consumo de Api usuario para traer id item
        for item in json_items_user["results"]:

            # Validando si el cliente existe:
            partner_exist = self.env["meli.items"].search([('id_items','=',item)])

            if len(partner_exist) == 0:

                # Trayendo el json para la description del item
                url_item_user = ITEM_URI.format(item)
                json_item = self.get_data_from_api(url_item_user, header)

                # Validacion inventory id
                if(json_item['inventory_id'] == None):
                    inventory = 'not full'
                else:
                    inventory = json_item['inventory_id']

                # Para ubicacion
                ubicacion = 'https://www.google.com.pe/maps/place/{},%20{}'
                link_ubicacion = ubicacion.format(json_item['geolocation']['latitude'],json_item['geolocation']['longitude'])

                # Variables locales
                autor = ''
                material_libro = ''
                genero_libro = ''
                isbn_libro = ''
                idioma_libro = ''
                edad_maxima_libro = ''
                garantia_libro = ''

                # Extraer datos de atributo
                for data in json_item['attributes']:
                    if data['id'] == 'AUTHOR':
                        autor = data['value_name']
                    if data['id'] == 'BOOK_COVER_MATERIAL':
                        material_libro = data['value_name']
                    if data['id'] == 'BOOK_GENRE':
                        genero_libro = data['value_name']
                    if data['id'] == 'GTIN':
                        isbn_libro = data['value_name']
                    if data['id'] == 'LANGUAGE':
                        idioma_libro = data['value_name']
                    if data['id'] == 'MAX_RECOMMENDED_AGE':
                        edad_maxima_libro = data['value_name']

                # Extraer dato de terms para garantia
                for data_temrs in json_item['sale_terms']:
                    if data_temrs['id'] == 'WARRANTY_TYPE':
                        garantia_libro = data_temrs['value_name']

                tags_ids = []

                # Recorriendo tags
                for data_tags in json_item['tags']:
                    # Buscando em meli.tags si existe el nombre
                    bs_tag = self.env["meli.tags"].search([('name','=',data_tags)])                    
                    # Valido si no existe
                    if len(bs_tag) == 0:
                        # Creo un tags si no encuentro
                        tag_respuesta = self.env["meli.tags"].create({"name": data_tags})
                        # Guardando el id del tag
                        bs_tag = tag_respuesta
                    #Guardando en mi lista de tags
                    tags_ids.append(bs_tag.id)



                # Llenado de objeto
                obj={}

                # Vista tree
                obj['id_items'] = json_item['id']
                obj['title'] = json_item['title']
                obj['price'] = json_item['price']
                obj['inventory_id'] = inventory
                obj['currency_id'] = json_item['currency_id']
                obj['initial_quantity'] = json_item['initial_quantity']
                obj['available_quantity'] = json_item['available_quantity']
                obj['sold_quantity'] = json_item['sold_quantity']
                obj['logistic_type'] = json_item['shipping']['logistic_type']

                # Vista Form
                obj['category_id']=json_item['category_id']
                obj['base_price']=json_item['base_price']
                obj['condition']=json_item['condition']
                obj['warranty']=garantia_libro
                obj['permalink']=json_item['permalink']
                obj['pictures']=self.getImage(json_item['pictures'][0]['url'])
                obj['geolocation']= link_ubicacion
                obj['author']= autor
                obj['book_cover']=material_libro
                obj['book_genre']=genero_libro
                obj['isbn']=isbn_libro
                obj['language']=idioma_libro
                obj['max_recommended_age']=edad_maxima_libro
                obj['tag_ids'] = tags_ids

                # Creacion del objeto
                self.env["meli.items"].create(obj)
                print("Creando el objeto")