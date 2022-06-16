# -*- coding: utf-8 -*-

from odoo import models, fields


class Sales(models.Model):
    _inherit = 'sale.order'
    delivery_agent = fields.Many2one('hr.employee', 'Delivery Agent')

    market = fields.Char(string="Market")
    lat = fields.Float(string='Latitude')
    lng = fields.Float(string='longitude')

    priority = fields.Boolean(string='Priority')

    # delivery status 
    delivery_state = fields.Char(string="Delivery Status")