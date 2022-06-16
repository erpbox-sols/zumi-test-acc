from odoo import api, models, fields

class ProductTemplateExtended(models.Model):
    _inherit = "product.template"

    list_price = fields.Float(
        'Sales Price', default=1.0,
        digits='Product Price',
        tracking=True,
        help="Price at which the product is sold to customers.")
    
    name = fields.Char('Name', index=True, required=True, translate=True, tracking=True,)
    allowed_modify_sale_price = fields.Boolean("Allowed Modify Sale Price", compute='_compute_allowed_modify_sale_price')
    allowed_inv_operations = fields.Boolean("Allowed Inventory Operations", compute='_compute_allowed_inventory_operations')

    def _compute_allowed_modify_sale_price(self):
        for product in self:
            if self.env.user.has_group('access_rights.group_sale_price_changes'):
                product.allowed_modify_sale_price = True
            else:
                product.allowed_modify_sale_price = False
    
    def _compute_allowed_inventory_operations(self):
        for product in self:
            if self.env.user.has_group('access_rights.group_allow_inventory_operations'):
                product.allowed_inv_operations = True
            else:
                product.allowed_inv_operations = False


class StockPickingExtended(models.Model):
    _inherit = "stock.picking"

    donot_allow_validate_incoming_shipment = fields.Boolean("Restrict Validate Incoming Shipment", compute='_compute_allowed_validate_incoming_shipment')

    def _compute_allowed_validate_incoming_shipment(self):
        for picking in self:
            if self.env.user.has_group('access_rights.group_allow_validate_incoming_shipment') and self.picking_type_id.code == 'incoming':
                picking.donot_allow_validate_incoming_shipment = False
            else:
                picking.donot_allow_validate_incoming_shipment = True