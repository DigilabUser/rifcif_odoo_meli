# -*- coding: utf-8 -*-

from email.policy import default
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class ProductTemplateInherit(models.Model):
    _inherit="product.template"
    
    shipping_type = fields.Selection([
        ('full', 'Full'),
        ('notfull', 'Not Full')
    ], string='Tipo de envío', default='notfull')

    def testing_python(self):
        raise ValidationError("ACA VA TU CODIGO")