# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Sale(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _generate_seq(self, name, date_order, company_id, so_names):
        if name == _('New'):
            seq_date = None
            if date_order:
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(date_order))
            if company_id:
                name = self.env['ir.sequence'].with_context(force_company=company_id).next_by_code(
                    'sale.order', sequence_date=seq_date) or _('New')
            else:
                name = self.env['ir.sequence'].next_by_code(
                    'sale.order', sequence_date=seq_date) or _('New')

        if name in so_names:
            self._generate_seq(name, date_order, company_id, so_names)
        else:
            return name

    @api.model
    def create(self, vals):
        so_names = self.mapped('name')
        name = self._generate_seq(vals.get('name', _('New')), vals.get(
            'date_order', False), vals.get('company_id', False), so_names)

        vals.update({'name': name})

        res = super().create(vals)
        return res

class AccountMove(models.Model):
    _inherit = 'account.move'

    active = fields.Boolean(string="Active")

