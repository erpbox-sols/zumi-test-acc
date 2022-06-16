from odoo import api, models, fields

class StockPicking(models.Model):
	_inherit = "stock.picking"

	delivery_receipt = fields.Selection([('delivery', 'Delivery'),
											('receipt', 'Receipt')], string="Delivery/Receipt", copy=False)