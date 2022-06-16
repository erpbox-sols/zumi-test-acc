from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    x_salesperson = fields.Many2one('hr.employee', string="SalesPerson")
    delivery_failed = fields.Selection([('cash', 'No Money'), ('unavailable', 'Customer Unavailable'),
                                        ('quality', 'Bale Quality')], string="Delivery Failed Reason")
    pick_up_type = fields.Selection([('shop', 'Delivery to customer shop'), ('hub', 'Hub')], string="Delivery method",
                                     required=True, default='shop')
    in_store = fields.Boolean(string="In store")
