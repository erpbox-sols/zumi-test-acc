# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = "account.move"

    def get_paid_amount(self, payment_id):
        for rec in self._get_reconciled_info_JSON_values():
            if rec['account_payment_id'] == payment_id.id:
                return rec['amount']




