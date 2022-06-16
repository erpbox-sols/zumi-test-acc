# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class StockMove(models.Model):
    _inherit = "stock.move"
    
    picking_code = fields.Selection(related='picking_id.picking_type_id.code', readonly=True)


class InventoryTarget(models.Model):
    _name = "inventory.target"
    _description = 'Inventory Target'
    _auto = False

    actual_sold = fields.Float(compute='_get_delivered_product', string="Actual Sold", help='Dilivered Qty')
    actual_total_sold = fields.Float(compute='_get_delivered_product',string="Actual Total Sold", help='Delivered + Dropship Qty')
    location_id = fields.Many2one('stock.location', string='Location', help='Source Location Of Stock Move')
    product_id = fields.Many2one('product.product', string='Product')
    qty_on_hand = fields.Float(compute='_get_delivered_product', string='On Hand')
    target = fields.Integer(string='Target')
    total_delivered_qty = fields.Float(string='Delivered Qty')
    total_dropship_qty = fields.Float(string='Dropship Qty', help='Sum of Total Delivery + Dropship Qty')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'inventory_target')
        self._cr.execute("""
            CREATE or REPLACE view inventory_target as (
                SELECT
                    min(sm.id) as id,
                    sm.location_id as location_id,
                    sm.product_id as product_id,
                    ls.target as target,
                    CASE
                        WHEN
                            spt.name = 'Delivery Orders'
                        THEN
                            sum(sm.product_uom_qty)
                        ELSE 0
                    END AS total_delivered_qty,
                    
                    CASE
                        WHEN
                            spt.name = 'Dropship'
                        THEN
                            sum(sm.product_uom_qty)
                        ELSE 0
                    END AS total_dropship_qty
                FROM
                    stock_move as sm
                LEFT JOIN
                    stock_location ls on (sm.location_id=ls.id)
                INNER JOIN
                    stock_picking_type spt ON (sm.picking_type_id= spt.id)
                WHERE
                    sm.state = 'done' AND
                    ls.usage = 'internal' AND ls.active='t' AND
                    spt.name in ('Delivery Orders', 'Dropship')
                GROUP BY
                    sm.location_id,
                    sm.product_id,
                    ls.target,
                    spt.name
            )
        """)

    def _get_delivered_product(self):
        '''
            - Mehtod used to get the total delivered product quantity for each location stock location
        '''       
        for data in self:
            data.actual_sold = 0.0
            product_data = data.product_id.with_context({'location':data.location_id.id})._product_available()
            data.qty_on_hand = product_data[data.product_id.id].get('qty_available', 0.0)
            total_deliver_dropship_qty = data.total_delivered_qty + data.total_dropship_qty
            if data.total_delivered_qty > 0:
                data.actual_sold = data.total_delivered_qty/7
            if total_deliver_dropship_qty > 0:
                data.actual_total_sold = total_deliver_dropship_qty/7
# quant_obj = self.env['stock.quant']
#
# qty_available = quant_obj._get_available_quantity(product_id, loc_id)

                  