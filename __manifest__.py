# -*- encoding: utf-8 -*-
{
    'name': 'Rifcif MELI Connector',
    'version': '1.0.0',
    'author': 'Ingenieria Rifcif SAC',
    'colaborators':[
    'Luis Enrique Alva Villena <luis.alva@digilab.pe>',
    'Diego Alonso Alva Vela <diego.alva@digilab.pe>'
    ],
    'depends': ['sale_management', 'stock'],
    'summary': 'Este modulo brinda una integración de odoo con MercadoLibre Chile',
    'description': '',
    'data': [
        'security/ir.model.access.csv',
        'views/assets_backend.xml',
        'views/product_template.xml',
        'views/meli_connector.xml',
    ],
    'qweb': ['static/src/xml/template.xml'],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
