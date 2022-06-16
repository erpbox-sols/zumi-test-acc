# -*- coding: utf-8 -*-

from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    market = fields.Char(string="Market")
    latitude = fields.Char(string="Latitude")
    longitude = fields.Char(string="Longitude")
    user_name = fields.Char(string="Creator")
