# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class AccountMoveReport(models.Model):
    _name = "account.move.report"
    _description = 'Unique Customer'
    _auto = False
    _order = "month_date"

    unique_customer = fields.Integer(string="Customer", readonly=True)
    month_date = fields.Date(string='Date', readonly=True)
    end_date = fields.Date(string='End Date', readonly=True)
    avg_revenue = fields.Integer(string="Average Revenue", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'account_move_report')

        self._cr.execute("""
            CREATE or REPLACE view account_move_report as (
                SELECT
                    min(account_move.id) as id,
                    count(distinct(partner_id)) AS unique_customer,
                    sum(amount_total)/count(distinct(partner_id)) AS avg_revenue,
                    TO_CHAR(invoice_date, 'YYYY-mm-01') AS month_date,
                    TO_CHAR(CAST(TO_CHAR(invoice_date, 'YYYY-mm-01') as date) + interval '1 month -1 day', 'YYYY-mm-dd') AS end_date
                FROM
                    account_move
                WHERE
                    type = 'out_invoice' and state='posted'
                GROUP BY
                    month_date
            )
        """)


class ReturningCustomerReport(models.Model):
    _name = "returning.customer.report"
    _description = 'Retained Customer'
    _auto = False
    _order = "invoice_date"

    invoice_date = fields.Date(string='Date', readonly=True)
    # end_date = fields.Date(string='End Date', readonly=True)
    returning_customer = fields.Integer(string="Customer", readonly=True)
    avg_revenue = fields.Integer(string="Average Revenue", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'returning_customer_report')
        self._cr.execute("""
            CREATE or REPLACE view returning_customer_report as (
               SELECT
                    min(am.id) as id,
                    TO_CHAR(am.invoice_date, 'YYYY-mm-01') as invoice_date,
                    SUM(am.amount_total)/COUNT(DISTINCT(am.partner_id)) AS avg_revenue,
                    COUNT(DISTINCT(am.partner_id)) as returning_customer
                FROM
                    account_move am
                INNER JOIN
                    account_move am2 ON am.partner_id = am2.partner_id
                WHERE
                    am.type='out_invoice' AND am2.type='out_invoice' and
                    am.state='posted' AND am2.state='posted' and
                    TO_CHAR(am2.invoice_date, 'YYYY-mm-dd') < TO_CHAR(am.invoice_date, 'YYYY-mm-01')
                GROUP BY TO_CHAR(am.invoice_date, 'YYYY-mm-01')
               )
        """)


class NewCustomerReport(models.Model):
    _name = "new.customer.report"
    _description = 'New Customer'
    _auto = False
    _order = "partner_create_date"

    partner_create_date = fields.Date(string='Month Start Date', readonly=True)
    new_customer = fields.Integer(string="New Customer", readonly=True)
    avg_revenue = fields.Integer(string="Average Revenue", readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'new_customer_report')
        self._cr.execute("""
            CREATE or REPLACE view new_customer_report as (
                SELECT
                    min(rp.id) as id,
                    COUNT(DISTINCT(rp.id)) as new_customer,
                    TO_CHAR(rp.create_date, 'YYYY-mm-01') as partner_create_date,
                    sum(am.amount_total)/count(distinct(rp.id)) as avg_revenue
                FROM
                    res_partner rp
                INNER JOIN
                    account_move am
                ON
                    rp.id = am.partner_id
                WHERE
                    customer_rank >=1 AND
                    am.type='out_invoice' AND
                    am.state='posted'
                GROUP BY
                    TO_CHAR(rp.create_date, 'YYYY-mm-01'))
        """)


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    margin = fields.Float(string='Margin', readonly=True)
    cost_price = fields.Float(string='Cost Price', readonly=True)
    price_unit = fields.Float(string='Unit Price', readonly=True)
    market = fields.Char(string='Market')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    sales_person_id = fields.Many2one('hr.employee', string='X SalesPerson')
    delivery_agent_id = fields.Many2one('hr.employee', string='Delivery Agent')
    net_sale = fields.Float(string='Total Net Sale')
    pure_net_sale = fields.Float(string='Net Sale')
    total_qty = fields.Float(string='Total Quantity')
    net_total_qty = fields.Float(string='Net Quantity')
    route_id = fields.Many2one('stock.location.route',string='Route')
    sales_return = fields.Float(string='Total Return', readonly=True)
    net_sales_return = fields.Float(string='Net Return', readonly=True)
    
    def _select(self):
        return super(AccountInvoiceReport, self)._select() + """
            , move.market as market,
            move.warehouse_id as warehouse_id,
            move.sales_person_id as sales_person_id,
            move.delivery_agent_id as delivery_agent_id,
            move.net_sale as net_sale,
            move.pure_net_sale as pure_net_sale,
            move.total_qty as total_qty,
            move.net_total_qty as net_total_qty,
            line.route_id as route_id,
            move.sales_return as sales_return,
            move.net_sales_return as net_sales_return
            """

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + """
            , move.market,
            move.warehouse_id,
            move.sales_person_id,
            move.delivery_agent_id,
            move.net_sale,
            move.pure_net_sale,
            move.total_qty,
            move.net_total_qty,
            line.route_id,
            move.sales_return,
            move.net_sales_return
        """
