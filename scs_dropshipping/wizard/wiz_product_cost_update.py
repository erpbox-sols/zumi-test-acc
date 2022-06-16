# See LICENSE file for full copyright and licensing details.

from odoo import models


class CostUpdateWizard(models.TransientModel):
    _name = "product.cost.update"
    _description = "Help to update cost in the selected sale order"

    def update_product_cost(self):
        """ - Method will update product cost price only for the product which has no dropship route.
            - Product cost price will be calculate average cost based on the purchase order
            - For product average price, count purchase order from 01-01-2021 till today
        """
        route_id = self.env.ref('stock_dropshipping.route_drop_shipping')
        prod_tmpl_ids = self.env['product.template'].browse(self._context.get('active_ids'))
        po_line_obj = self.env['purchase.order.line']
        so_line_obj = self.env['sale.order.line']
        company_id = self.env.company
        for pt in prod_tmpl_ids:
            self._cr.execute('select id from product_product where product_tmpl_id=%s' % (pt.id,))
            product_id = self._cr.fetchone()
            if product_id:
                po_line_ids = po_line_obj.search([('product_id','=',product_id[0])])
                purchase_total = 0.0
                po_qty_total = 0
                for pl in po_line_ids:
                    # find the purchase order to count only PO with specific date range
                    #if pl.order_id and str(pl.order_id.date_approve) >= po_date_range:
                    subtotal = pl.product_qty * pl.price_unit
                    purchase_total += subtotal
                    po_qty_total += pl.product_qty
                # calculate average price
                if purchase_total and po_qty_total:
                    product_average_price = purchase_total / po_qty_total
                    if not pt.standard_price:
                        pt.with_context(force_company=company_id.id).sudo().write({'standard_price': product_average_price})                                    
                                