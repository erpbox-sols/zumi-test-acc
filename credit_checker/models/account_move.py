from odoo import api, models, fields

class AccountmoveExtended(models.Model):
    _inherit = "account.move"

    is_credit_cutomer = fields.Boolean("Credit Customer",default=False)

    def update_invoice_credit(self):
        invoices = self.search([])
        for invoice in invoices:
            for line in invoice.invoice_line_ids:
                if line.product_id.categ_id.name == 'Commitment Fee':
                   invoice.is_credit_cutomer = True
    
    def action_post(self):
        res = super(AccountmoveExtended, self).action_post()
        for invoice in self:
            for line in invoice.invoice_line_ids:
                if line.product_id.categ_id.name == 'Commitment Fee':
                   invoice.is_credit_cutomer = True
        return res
