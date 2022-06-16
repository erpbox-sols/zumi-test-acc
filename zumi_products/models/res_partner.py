from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError

class ResPartner(models.Model):
	_inherit = "res.partner"

	attribute_code = fields.Char("Attribute Code", copy=False)