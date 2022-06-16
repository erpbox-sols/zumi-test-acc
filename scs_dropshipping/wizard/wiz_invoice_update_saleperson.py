# See LICENSE file for full copyright and licensing details.

from odoo import models


class UpdateSalesperson(models.TransientModel):
    _name = "saleperson.update"
    _description = "Salesperson update in invoice"

    def inv_update_saleperson(self):
        """ - Method will update sales person in the invoice
            - Find sales person based on invoice origin and update in invoice
        """
        inv_obj = self.env['account.move']
        sale_obj = self.env['sale.order']
        for inv in inv_obj.search([('id', 'in', self._context.get('active_ids'))]):
            for sale in sale_obj.search([('invoice_ids','in', [inv.id])]):
                inv.sales_person_id = sale.x_salesperson
                inv.warehouse_id = sale.warehouse_id.id
                inv.market = sale.market
                inv.delivery_agent_id = sale.delivery_agent.id
    
