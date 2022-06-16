# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"
    
    purchase_price = fields.Float('Cost', readonly=True)
    market = fields.Char('Market', readonly=True)
    delivery_agent = fields.Many2one('hr.employee', string='Delivery Agent')
    x_salesperson = fields.Many2one('hr.employee', string='X SalesPerson')
    price_unit = fields.Float(string='Unit Price', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['purchase_price'] = ",l.purchase_price as purchase_price"
        fields['market'] = ",s.market"
        fields['delivery_agent'] = ", s.delivery_agent"
        fields['x_salesperson'] = ", s.x_salesperson"
        fields['price_unit'] = ", l.price_unit"
        groupby += ', l.purchase_price, s.market, s.delivery_agent, s.x_salesperson, l.price_unit'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoiced = fields.Boolean(compute='get_cancel_so', store=True, string='Invoiced')
    is_cost_updated = fields.Boolean(string='Cost Updated', copy=False)
    
    @api.depends('state')
    def get_cancel_so(self):
        for rec in self.filtered(lambda so: so.state == 'cancel'):
            if len(rec.order_line.invoice_lines) > 0:
                rec.invoiced = True

    def _prepare_invoice(self):
        """
            - Override this method to set sales person in new created invoice from sale order
        """
        self.ensure_one()
        result = super(SaleOrder, self)._prepare_invoice()
        result['sales_person_id'] = self.x_salesperson.id
        result['warehouse_id'] = self.warehouse_id.id
        result['market'] = self.market
        result['delivery_agent_id'] = self.delivery_agent.id
        return result

    def auto_update_sale_cost(self):
        """ - Method will update purchase price in the sale order.
            - For all selected sale order(except cancel) order purchase price update
        """
        po_line_obj = self.env['purchase.order.line']
        #Get dropship route id 
        route_id = self.env.ref('stock_dropshipping.route_drop_shipping')
        order_ids = self.env['sale.order'].search([('is_cost_updated', '=', False)])
        inv_obj = self.env['account.move']
        company_id = self.env.company
        for order in order_ids:
            # Find purchase order line related to sale order
            po_line = po_line_obj.search([('sale_order_id','=', order.id)])
            for line in order.order_line.filtered(lambda self: self.display_type == False):
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
                # Check Cost Price is updated or not. 
                # If not then is_cost_updated filed not update
                if line.purchase_price > 0:
                    line.order_id.is_cost_updated = True
                # Following code for the set cost price 0.0 for service type product
                if line.product_id.type == 'service':
                    line.purchase_price = 0.0


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
 
    market = fields.Char(related='order_id.market', store=True)
    
    def _prepare_invoice_line(self):
        """
            - Override method to set cost price from sale order to invoice
        """
        result = super(SaleOrderLine, self)._prepare_invoice_line()
        result['cost_price'] = self.purchase_price
        return result


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        """
            - Override this method to set sales person in invoice form sale order in case create 
              invoice with down payment in percentage or in fixed amount
        """
        result = super(SaleAdvancePaymentInv,self)._prepare_invoice_values(order, name, amount, so_line)
        if order.x_salesperson:
            result['sales_person_id'] = order.x_salesperson.id
        if order.warehouse_id:
            result['warehouse_id'] = order.warehouse_id.id
        if order.market:
            result['market'] = order.market
        if order.delivery_agent:
            result['delivery_agent_id'] = order.delivery_agent.id
        return result