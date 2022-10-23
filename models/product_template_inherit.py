# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class ProductTemplateInherit(models.Model):
    _inherit="product.template"

    def testing_python(self):
        raise ValidationError("ACA VA TU CODIGO")