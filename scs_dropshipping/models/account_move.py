# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    sales_person_id = fields.Many2one('hr.employee', string='X SalesPerson')
    delivery_agent_id = fields.Many2one('hr.employee', string='Delivery Agent')
    sales_return = fields.Float(compute='_get_return_amount', string='Total Return', store=True)
    net_sale = fields.Float(compute="_get_net_sale", string='Total Net Sale', store=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    total_qty = fields.Float(compute='_get_net_sale', string='Total Quantity', store=True)
    market = fields.Char(string='Market')
    pure_net_sale = fields.Float(compute="_pure_net_sale", string='Net Sale', store=True)
    net_sales_return = fields.Float(compute='_get_return_amount', string='Net Return', store=True)
    net_total_qty = fields.Float(compute='_pure_net_sale', string='Net Quantity', store=True)
    is_cost_updated = fields.Boolean(string='Cost Updated', copy=False)
    margin = fields.Monetary(compute='_get_margin', help="It gives profitability by calculating the difference between the Unit Price and the cost.", currency_field='currency_id', store=True)
    total_cost = fields.Monetary(compute='get_total_cost', string='Cost')

    def get_total_cost(self):
        for inv in self:
            total_cost = 0.0
            for line in inv.invoice_line_ids.filtered(lambda line: line.display_type == False):
                if line.cost_price > 0:
                    total_cost += line.cost_price
            inv.total_cost = total_cost
    
    @api.depends('invoice_line_ids.inv_margin')
    def _get_margin(self):
        for inv in self.filtered(lambda invoice: invoice.state == 'posted'):
            margin_total = 0.0
            for line in inv.invoice_line_ids:
                margin_total += line.inv_margin
            if inv.type == 'out_invoice':
                inv.margin = margin_total
            if inv.type == 'out_refund':
                inv.margin = -1 * (margin_total)
    
    def update_cost_price(self):
        """
            - This method call on scheduler
            - Scheduler call on every hour
        """
        sale_line_obj = self.env['sale.order.line']
        invoices = self
        if not invoices:
            invoices = self.env['account.move'].search([('is_cost_updated', '=', False),('type', '=', 'out_invoice')])
        for ln in invoices.invoice_line_ids.filtered(lambda line: line.display_type == False):
            sale_lines = sale_line_obj.search([('invoice_lines', 'in', [ln.id]), ('product_id', '=', ln.product_id.id)])
            if sale_lines:
                for sl in sale_lines:
                    if sl.purchase_price:
                        ln.cost_price = sl.purchase_price
                    else:
                        ln.cost_price = ln.product_id.standard_price
            else:
                ln.cost_price = ln.product_id.standard_price
            if ln.cost_price > 0:
                ln.move_id.is_cost_updated = True

    def update_route(self):
        """ - Method will update route in the invoice
            - Find route from sale order line and update in invoice
            - This method call from the server action
        """
        for inv_line in self.invoice_line_ids:
            if inv_line.sale_line_ids:
                for line in inv_line.sale_line_ids:
                    if line.route_id:
                        inv_line.route_id = line.route_id.id 

    @api.depends('state','amount_total')
    def _get_net_sale(self):
        for inv in self.filtered(lambda invoice: invoice.state == 'posted' and invoice.type in ('out_invoice', 'out_refund')):
            total_qty = 0.0
            for line in inv.invoice_line_ids:
                total_qty += line.quantity
            if inv.type == 'out_invoice':
                inv.net_sale = inv.amount_total
                inv.total_qty = total_qty
            if inv.type == 'out_refund':
                inv.net_sale = -1 * (inv.amount_total)
                inv.total_qty = -1 * (total_qty)
    
    @api.depends('sales_return', 'state', 'amount_total')
    def _pure_net_sale(self):
        route_id = self.env.ref('stock_dropshipping.route_drop_shipping')           
        # Following code for Pure net sale
        net_total = 0.0
        net_qty = 0.0
        for inv in self:
            if inv.state == 'posted':
                for line in inv.invoice_line_ids.filtered(lambda self: self.display_type == False):
                    route_ids = line.product_id.route_ids.ids
                    if line.move_id.type == 'out_invoice' and route_id.id not in route_ids:
                        net_total += line.quantity * line.price_unit
                        net_qty += line.quantity
                    line.move_id.pure_net_sale = net_total
                    line.move_id.net_total_qty = net_qty
                inv.pure_net_sale = inv.pure_net_sale - inv.net_sales_return    

    @api.depends('reversed_entry_id','state')
    def _get_return_amount(self):
        route_id = self.env.ref('stock_dropshipping.route_drop_shipping')
        #FIXME: if credit not is posted - cancel and again - posted
        for rinv in self:
            net_return = 0.0
            if  rinv.type == 'out_refund' and rinv.state == 'posted':
                rinv.reversed_entry_id.sales_return = (-1 * rinv.amount_total_signed)
                for line in rinv.invoice_line_ids.filtered(lambda self: self.display_type == False): 
                    route_ids = line.product_id.route_ids.ids
                    if route_id.id not in route_ids:
                        net_return += line.quantity * line.price_unit
                rinv.reversed_entry_id.net_sales_return = net_return
              
    def set_return_amount(self):
        " Method use to calculate the return amount for the historical invoice data"
        self._cr.execute("""
            SELECT
                reversed_entry_id,
                amount_total_signed
            FROM
                account_move
            WHERE
                type='out_refund' and
                reversed_entry_id is not null
        """)
        datas = self._cr.dictfetchall()
        if datas:
            for data in datas:
                self._cr.execute("""
                UPDATE
                    account_move
                SET
                    sales_return = %s
                WHERE
                    id=%s
            """ % (-1 * data.get('amount_total_signed'),data.get('reversed_entry_id')))
            self._cr.commit()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    cost_price = fields.Float(string='Cost Price', help="This value fetch from sale order cost price")
    inv_margin = fields.Float(compute='_get_margin', string='Margin', digits='Product Price', store=True)
    route_id = fields.Many2one('stock.location.route', related='sale_line_ids.route_id', store=True, string='Route')

    @api.depends('product_id', 'cost_price', 'quantity', 'price_unit', 'price_subtotal')
    def _get_margin(self):
        for line in self:
            currency = line.move_id.currency_id
            price = line.cost_price
            margin = line.price_subtotal - (price * line.quantity)
            line.inv_margin = currency.round(margin) if currency else margin

    def write(self, vals):
        """
            - Super call of write method to update Unit price in related sale order.
        """
        sale_line_obj = self.env['sale.order.line']
        if vals.get('price_unit'):       
            for move_line in self.filtered(lambda self: self.display_type == False and self.move_id.type=='out_invoice'):
                # Here find sale order line which mapped with the move line
                for so_line in sale_line_obj.search([('invoice_lines','in', [move_line.id])]):
                    so_line.price_unit = vals.get('price_unit')

        # Following code for to update cost price from the vendor bill into sale order line cost price
        for line in self.filtered(lambda self: self.display_type == False and self.move_id.type=='in_invoice'):
            if line.purchase_line_id and line.price_unit > 0:
                sale_line = line.purchase_line_id.sale_line_id
                if sale_line:
                    sale_line.purchase_price = line.price_unit    
        return super(AccountMoveLine, self).write(vals)


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    margin = fields.Float(string='Margin', readonly=True)
    cost_price = fields.Float(string='Cost Price', readonly=True)
    price_unit = fields.Float(string='Unit Price', readonly=True)
    
    @api.model
    def _select(self):
        result = super(AccountInvoiceReport, self)._select()
        result += ', line.inv_margin as margin, line.cost_price, line.price_unit'
        return result

    @api.model
    def _group_by(self):
        result = super(AccountInvoiceReport, self)._group_by()
        result += ', line.inv_margin, line.cost_price, line.price_unit'
        return result
