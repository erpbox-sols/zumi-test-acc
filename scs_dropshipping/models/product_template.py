# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    nm_days = fields.Integer(string='Days', compute='_get_product_details', store=True, help='Difference of last stock move - current date in days')
    nm_qty = fields.Float(string='Non Moving Qty', compute='_get_product_details', store=True, help='This is on hand stock of non-moving products')
    nm_value = fields.Float(string='Product Valuation', compute='_get_product_details', store=True, help='This is valuation for non-moving products')

    @api.depends('qty_available', 'virtual_available', 'write_date')
    def _get_product_details(self):
        ''' Method helps to calculate the
            - Product non moving days
            - Product stock for non moving days
            - Valuation for non moving products
        '''
        today = datetime.now().date()
        stock_move_obj = self.env['stock.move']
        for product in self:
            product.nm_days = 0
            product.nm_qty = 0.0
            product.nm_value = 0.0
            product_id = self.env['product.product'].search([('product_tmpl_id', '=', product.id)], limit=1)
            move_id = stock_move_obj.search([('product_id', '=', product_id.id), ('state', '=', 'done')], order='id desc', limit=1)
            if move_id and move_id.date:
                days = (today - move_id.date.date()).days
                if days and product.qty_available:
                    product.nm_days = days
                    product.nm_qty = product.qty_available
                    product.nm_value = (product.qty_available * product.standard_price)
            elif product.create_date:
                new_days= (today - product.create_date.date()).days
                if new_days and product.qty_available:
                    product.nm_days = new_days
                    product.nm_qty = product.qty_available
                    product.nm_value = (product.qty_available * product.standard_price)