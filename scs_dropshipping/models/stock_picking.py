# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class StockLocation(models.Model):
    _inherit = 'stock.location'
    
    target = fields.Integer(string='Target', help="Set Quantity Target")
