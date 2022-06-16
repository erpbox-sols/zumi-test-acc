# See LICENSE file for full copyright and licensing details.

from odoo import models


class CostUpdateWizard(models.TransientModel):
    _name = "sale.cost.update"
    _description = "Help to update cost in the selected sale order"

    def update_cost(self):
        """ - Method will update purchase price in the sale order.
            - For all selected sale order(except cancel) order purchase price update
        """
        po_line_obj = self.env['purchase.order.line']
        #Get dropship route id 
        route_id = self.env.ref('stock_dropshipping.route_drop_shipping')
        order_ids = self.env['sale.order'].browse(self._context.get('active_ids'))
        inv_obj = self.env['account.move']
        company_id = self.env.company
        for order in order_ids:
            # Find purchase order line related to sale order
            po_line = po_line_obj.search([('sale_order_id','=', order.id)])
            for line in order.order_line.filtered(lambda self: self.display_type == False):
                route_ids = line.product_id and line.product_id.route_ids.ids
                # Here we check if dropship route found in product and get PO line
                if po_line:
                    for pl in po_line.filtered(lambda self: self.product_id.id == line.product_id.id and self.display_type == False):
                        if pl.invoice_lines:
                            for vline in pl.invoice_lines:
                                line.purchase_price = vline.price_unit
                        else:
                            line.purchase_price = pl.price_unit
                else:
                    # product price will be set when if dropship route is not in the product
                    line.purchase_price = line.product_id.standard_price
                
                # Following code for the set cost price 0.0 for service type product
                if line.product_id.type == 'service':
                    line.purchase_price = 0.0
                
                # Following code to update the invoice reference in the sale order  
                if line.state in ('sale', 'done') and not line.invoice_lines:
                    invoice_id = inv_obj.search([('invoice_origin','=', line.order_id.name), ('state', '!=', 'cancel')])
                    
                    if invoice_id:
                        # If got invoice then find related invoice line
                        inv_line_ids = invoice_id.invoice_line_ids.filtered(lambda line: line.exclude_from_invoice_tab == False and line.display_type == False)
                        
                        #If found multiple invoice line then need match product_id of Sale Order Line and Invoice Line 
                        for inv_line in inv_line_ids:
                            if inv_line.product_id.id == line.product_id.id:
                                line.invoice_lines = [(6,0,[inv_line.id])]
                        
                    
