# -*- coding: utf-8 -*-
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    meli_order_id = fields.Many2one('meli.order', string='meli_order')
