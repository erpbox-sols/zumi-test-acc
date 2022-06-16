# See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import datetime
from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    days_with_zumi = fields.Integer(compute="_get_days_with_zumi", string='Days With Zumi',
                                    help="Number of days that customer connect with zumi ")
    inactive_days = fields.Integer(compute="_get_days_with_zumi", string='Inactive Days',
                                   help="Number of days that customer inactive with zumi. Here only count days from last 'Done' sales order")
    inactive_weeks = fields.Integer(compute="_get_days_with_zumi", string='Inactive Weeks',
                                    help="Number of weeks that customer inactive with zumi. Here only count week from last 'Done' sales order")
    average_basket = fields.Float(compute="_get_days_with_zumi", string='Average Basket',
                                  help="Average sale of customer with zumi. Here only count average for 'Done' Sales Order")
    
    frequency_month = fields.Float(compute="_get_month_frequency", string='Frequency Month')
    
    def _get_month_frequency(self):
        sale_obj = self.env['sale.order']
        for partner in self:
            partner.frequency_month = 0.0
            domain = [('partner_id', '=', partner.id),('state', 'in',('sale','done'))]
            sale_data = sale_obj.sudo().read_group(domain, ['date_order'], ['date_order:month'])
            total_sale_order = 0
            total_months = 0
            if sale_data:
                for sale in sale_data:
                    total_sale_order += sale.get('date_order_count')
                    total_months += 1
            if total_sale_order and total_months:
                partner.frequency_month = total_sale_order / total_months
        
    def _get_days_with_zumi(self):
        today = datetime.now().date()
        sale_obj = self.env['sale.order']
        for partner in self:
            partner.days_with_zumi = 0
            partner.inactive_days = 0
            partner.inactive_weeks = 0
            partner.average_basket = 0.0
            # Customer with zumi days
            days = today - partner.create_date.date()
            partner.days_with_zumi = int(days.days)
            # Customer inactive days
            # Find last sale order date of the customer
            sale_id = sale_obj.search([('partner_id', '=', partner.id), ('state', 'in',('sale','done'))], order='date_order desc', limit=1)
            if sale_id and sale_id.date_order:
                last_order_date = sale_id.date_order.date()
                inactive_days = today - sale_id.date_order.date()
                partner.inactive_days = int(inactive_days.days) or 0
                # Find Inactive weeks
                weeks = int((int(inactive_days.days) % 365) / 7)
                partner.inactive_weeks = weeks
            # Find average basket
            sale_ids = sale_obj.search([('partner_id', '=', partner.id), ('state', '=','sale')])
            order_counter = 0
            order_total = 0.0
            for order in sale_ids:
                order_counter += 1
                order_total += order.amount_total
            if order_total and order_counter:
                average = order_total / order_counter
                partner.average_basket = average
            
            