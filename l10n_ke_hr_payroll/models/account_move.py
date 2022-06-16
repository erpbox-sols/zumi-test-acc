
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    payslip_batch_id = fields.Many2one("hr.payslip.run",
                                    string="Payslip Batch")

    def _check_balanced(self):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        moves = self.filtered(lambda move: move.line_ids)
        if not moves:
            return

        # /!\ As this method is called in create / write, we can't make the assumption the computed stored fields
        # are already done. Then, this query MUST NOT depend of computed stored fields (e.g. balance).
        # It happens as the ORM makes the create with the 'no_recompute' statement.
        if self._context.get("payroll_bypass") or self._context.get("active_model") == 'hr.payslip.run':
            return True
        self.env['account.move.line'].flush(['debit', 'credit', 'move_id'])
        self.env['account.move'].flush(['journal_id'])
        self._cr.execute('''
            SELECT line.move_id, ROUND(SUM(line.debit - line.credit), currency.decimal_places)
            FROM account_move_line line
            JOIN account_move move ON move.id = line.move_id
            JOIN account_journal journal ON journal.id = move.journal_id
            JOIN res_company company ON company.id = journal.company_id
            JOIN res_currency currency ON currency.id = company.currency_id
            WHERE line.move_id IN %s
            GROUP BY line.move_id, currency.decimal_places
            HAVING ROUND(SUM(line.debit - line.credit), currency.decimal_places) != 0.0;
        ''', [tuple(self.ids)])

        query_res = self._cr.fetchall()
        if query_res:
            ids = [res[0] for res in query_res]
            sums = [res[1] for res in query_res]
            raise UserError(_("Cannot create unbalanced journal entry. Ids: %s\nDifferences debit - credit: %s") % (ids, sums))


    def _get_values_account_move_line(
            self, account, journal, name, move,
            credit=0, debit=0, date=fields.Date.today()):
        return {
            'journal_id': journal.id,
            'name': name,
            'account_id': account.id,
            'move_id': move.id,
            'quantity': 1,
            'credit': credit,
            'debit': debit,
            'date': date,
        }


    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        context = dict(self._context)
        res = super(AccountMove, self)._onchange_partner_id()
        employee_obj = self.env['hr.employee']
        contract_obj = self.env['hr.contract']
        account_move_line_obj = self.env['account.move.line']
        for rec in self:
            if rec.partner_id:
                employee = employee_obj.sudo().search([('address_home_id', '=', rec.partner_id.id),
                                                       ('emp_type', '=', 'contractor')], limit=1)
                if employee:
                    contract = contract_obj.search([
                                ('employee_id', '=', employee.id),
                                ('state','=', 'open')], limit=1)
                    if employee.emp_type == 'contractor' and contract:
                        rec.line_ids = False
                        # sales_dept = self.env.ref('l10n_ke_hr_payroll.dep_sales_agents')
                        base_account_id = False
                        bonus_account_id = False
                        if employee.job_id and employee.job_id.id == 'Sales Agent':
                            base_account_id = self.env['account.account'].search([('code', '=', '60045-2')], limit=1)
                            bonus_account_id = self.env['account.account'].search([('code', '=', '60050')], limit=1)
                        credit_amt = contract.wage/100*5 # 5% of Gross Salary
                        lines = []
                        bonus_tax_amt = 0
                        if contract.bonus:
                            bonus_tax_amt = contract.bonus/100*5
                        
                        lines.append(rec.get_main_product_credit_vals(rec.partner_id,
                            contract.wage - credit_amt - contract.other_ded + contract.bonus - bonus_tax_amt,
                            base_account_id))
                        lines.append(rec.get_main_product_vals(rec.partner_id, contract.wage))

                        if contract.bonus:
                            lines.append(rec.get_bonus_vals(rec.partner_id, contract.bonus, bonus_account_id))
                        if contract.other_ded:
                            lines.append(rec.get_deduction_vals(rec.partner_id, contract.other_ded, base_account_id))
                        
                        rec.invoice_line_ids = [(0, 0, line) for line in lines]
                        
                        rec._recompute_tax_lines()
                        context.update({"payroll_bypass": True})
                        rec.with_context(context)._recompute_dynamic_lines()
        return res
    
    def get_main_product_credit_vals(self, partner, credit_amt, base_account_id):
        account = self.env['account.account'].search([('code', '=', '20003')], limit=1).id
        if base_account_id:
            account = base_account_id.id
        return {'account_id': account,
                'credit': credit_amt,
                'exclude_from_invoice_tab': True,
                'partner_id': partner.id,
                }
    
    def get_main_product_vals(self, partner, wage):
        tax_rec = self.env.ref('l10n_ke_hr_payroll.WHT')
        payable_account = self.env['account.account'].search([('code', '=', '20002')], limit=1)
        return {'account_id': payable_account.id,
                'debit': wage,
                'product_id': self.env.ref('l10n_ke_hr_payroll.product_product_pro_service').id,
                'name': 'Professional Services',
                'quantity': 1.0,
                'price_unit': wage,
                'tax_ids': [(6,0,[tax_rec.id])],
                'partner_id': partner.id,
                }
    
    def get_bonus_vals(self, partner, bonus, bonus_account):
        tax_rec = self.env.ref('l10n_ke_hr_payroll.WHT')
        account = self.env['account.account'].search([('code', '=', '20002')], limit=1).id
        if bonus_account:
            account = bonus_account.id
        return {'account_id': account,
                'debit': bonus,
                'name': 'Bonus',
                'quantity': 1.0,
                'price_unit': bonus,
                'tax_ids': [(6,0,[tax_rec.id])],
                'partner_id': partner.id,
                }
    
    def get_deduction_vals(self, partner, deduction, base_account_id):
        account = self.env['account.account'].search([('code', '=', '20003')], limit=1).id
        if base_account_id:
            account = base_account_id.id
        return {'account_id': account,
            'credit': deduction,
                'price_unit': -deduction,
                'name': 'Other Deductions',
                'quantity': 1.0,
                'partner_id': partner.id,
                # 'move_id': self.id
                }
    
    def _recompute_dynamic_lines(self, recompute_all_taxes=False, recompute_tax_base_amount=False):
        ''' Recompute all lines that depend of others.

        For example, tax lines depends of base lines (lines having tax_ids set). This is also the case of cash rounding
        lines that depend of base lines or tax lines depending the cash rounding strategy. When a payment term is set,
        this method will auto-balance the move with payment term lines.

        :param recompute_all_taxes: Force the computation of taxes. If set to False, the computation will be done
                                    or not depending of the field 'recompute_tax_line' in lines.
        '''
        for invoice in self:
            # Dispatch lines and pre-compute some aggregated values like taxes.
            for line in invoice.line_ids:
                if line.recompute_tax_line:
                    recompute_all_taxes = True
                    line.recompute_tax_line = False

            # Compute taxes.
            if recompute_all_taxes:
                invoice._recompute_tax_lines()
            if recompute_tax_base_amount:
                invoice._recompute_tax_lines(recompute_tax_base_amount=True)

            if not self._context.get('payroll_bypass') and invoice.is_invoice(include_receipts=True):

                # Compute cash rounding.
                invoice._recompute_cash_rounding_lines()

                # Compute payment terms.
                invoice._recompute_payment_terms_lines()

            # Only synchronize one2many in onchange.
            if invoice != invoice._origin:
                invoice.invoice_line_ids = invoice.line_ids.filtered(lambda line: not line.exclude_from_invoice_tab)

