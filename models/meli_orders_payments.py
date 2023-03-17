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

class MercadolibreOrdersPayments(models.Model):
    _name = 'meli.order.payments'

    order_id = fields.Many2one('meli.order', string='order')

    reason = fields.Char('Motivo')
    status_code = fields.Char('Codigo Estado')
    total_paid_amount = fields.Float('Monto Pagado') #
    operation_type = fields.Char('Tipo Operacion') #
    transaction_amount = fields.Float('Cantidad de Transaccion')
    date_approved = fields.Datetime('Fecha Aprobado')
    collector_id = fields.Char('ID Cobrador')
    coupon_id = fields.Char('ID Coupon')
    installments = fields.Integer('# Cuotas')#
    authorization_code = fields.Char('Codigo de Autorización')
    taxes_amount= fields.Integer('Impuestos')
    id = fields.Integer('ID')
    date_last_modified = fields.Datetime('Ultima fecha de modificacion')
    coupon_amount = fields.Integer('Cantidad de cupon')
    shipping_cost = fields.Integer('Costo de envio')#
    installment_amount = fields.Float('Monto de cuota')
    date_created = fields.Char('Fecha de creacion')
    activation_uri = fields.Char('Activacion Uri')
    overpaid_amount = fields.Integer('Monto sobrepagado')
    card_id = fields.Integer('Tarjeta de identificacion')
    status_detail = fields.Char('Detalle de estado')
    issuer_id = fields.Char('ID emisor')
    payment_method_id = fields.Char('Metodo de pago')#
    payment_type = fields.Char('Tipo de pago')#
    deferred_period = fields.Char('Periodo diferido')
    atm_transfer_reference_transaction_id = fields.Char('ID de transaccion')
    atm_transfer_reference_company_id = fields.Char('ID de la empresa')
    site_id = fields.Char('ID del sitio')
    payer_id = fields.Integer('ID del pagador')
    marketplace_fee = fields.Float('Cuota del mercado')
    order_id_1 = fields.Integer('ID de pedido')
    currency_id = fields.Char('Moneda')#
    status = fields.Char('Estado')
    transaction_order_id = fields.Char('ID de trasaccion del pedido')