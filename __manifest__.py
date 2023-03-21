# -*- encoding: utf-8 -*-
{
    'name': 'Rifcif MELI Connector',
    'version': '1.0.3',
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
        'security/ir.model.access.xml',
        'views/assets_backend.xml',
        'views/product_template.xml',
        'views/meli_connector.xml',
        'views/meli_orders.xml',
        'views/meli_shipments.xml',
        'views/meli_items.xml',
        'views/sale_order.xml',
        'wizards/order_wizard.xml',
        'wizards/wizard.xml',
        #'views/settings_inherit.xml'
    ],
    'qweb': ['static/src/xml/template.xml'],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
