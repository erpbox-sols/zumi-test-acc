# See LICENSE file for full copyright and licensing details.

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def write(self, vals):
        """
            - Super call of write method to update cost price in related sale order.
            - In Purchase order line update cost price and save PO, it will modify the cost price in related sale order.
        """
        sale_obj = self.env['sale.order']
        # route_id = self.env.ref('stock_dropshipping.route_drop_shipping')
        price_unit = 0.0
        if vals.get('price_unit'):
            price_unit = vals.get('price_unit')
        for record in self.filtered(lambda self: self.display_type == False):
            # Here we get product routes
            if not price_unit:
                price_unit = record.price_unit
            # route_ids = record.product_id and record.product_id.route_ids.ids
            # Here we remove code to update cost only in dropship product and cost price update for all product with route
            if record.sale_order_id:
                for so_line in record.sale_order_id.order_line.filtered(lambda line: line.product_id.id == record.product_id.id and line.display_type == False):
                    so_line.purchase_price = price_unit
        return super(PurchaseOrderLine, self).write(vals)