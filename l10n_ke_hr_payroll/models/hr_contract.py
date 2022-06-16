
import base64
from odoo import api, fields, models, _
from odoo.tests.common import Form
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero
from odoo.tools.safe_eval import safe_eval
import time
from datetime import datetime, date, timedelta
import calendar as base_calendar

MONTH_LIST = [('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'), ('4', 'Apr'),
              ('5', 'May'), ('6', 'Jun'), ('7', 'Jul'), ('8', 'Aug'),
              ('9', 'Sep'), ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec')]


class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    def _compute_inv_recods(self):
        for rec in self:
            rec.invoice_count = len(rec.move_ids)

    invoice_count = fields.Integer(compute='_compute_inv_recods')
    move_ids = fields.One2many('account.move', 'payslip_batch_id', string='Invoices', readonly=True,
        states={'draft': [('readonly', False)]})
    month = fields.Selection(MONTH_LIST, string='Month', readonly=True,
                default=str(int(datetime.now().strftime('%m'))),
                 states={'draft': [('readonly', False)]},
                 required=True)
    year = fields.Char('Year', readonly=True,
                      default=lambda *a: time.strftime('%Y'),
                      states={'draft': [('readonly', False)]},
                      required=True)
    
    @api.onchange('month', 'year')
    def onchange_month(self):
        if self.month:
            month_date = date(int(self.year), int(self.month), 1)
            self.date_start = month_date.replace(day=1)
            self.date_end = month_date.replace(day=base_calendar.monthrange(month_date.year, month_date.month)[1])

    def action_open_bills(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', self.move_ids.ids]],
            "name": "Payslips",
        }

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    tax_pin = fields.Char("KRA PIN")
    NHIF = fields.Char("NHIF No.")
    NSSF = fields.Char("NSSF No.")
    resident = fields.Boolean("Resident", default=True)
    emp_type = fields.Selection([
        ('employee', 'Employee'),
        ('student', 'Student'),
        ('trainee', 'Trainee'),
        ('contractor', 'Contractor'),
        ('freelance', 'Freelancer'),
        ], string='Employee Type', default='employee', required=True,
        help="""The employee type. Although the primary purpose may seem to
        categorize employees, this field has also an impact in the Contract
        History. Only Employee type is supposed to be under contract and will
        have a Contract History.""")
    disability = fields.Boolean("Employee has disability?", help="""Check this
                                box if the employee has disability and
                                is registered with Council of Persons
                                with Disability and has a certificate of
                                exemption from commissioner of Domestic
                                Taxes""")
    helb = fields.Boolean("HELB Loan?")
    helb_rate = fields.Float("HELB Monthly Amount", help="""HELB will issue
                        Loan payment instructions for your employee upon
                        contacting them. Upon the employment of any loanee,
                        you need to inform the Board in writing within a
                        period of three months of such employment. Fill in
                        the monthly figure advised by HELB.""")
    pension = fields.Boolean("Personal Pension/Providend Fund Scheme?",
                        help="""Check this box if the employee is registered
                        to a personal pension or provident fund scheme.
                        Contribution to any registered defined benefit fund
                        or defined contribution fund is an admissible
                        deduction in arriving at the employee's taxable pay
                        of the month""")
    pension_contrib = fields.Float("Actual Pension Contribution (Monthly)")
    disability_rate = fields.Float("Disability Exempt Amount", help="""	For
                        Persons with Disability, First KShs 150,000 pm is
                        exempt from tax. Here, you can record expenses
                        related to personal care and home care allowable up to
                        a maximum of KShs 50,000 per month.""")
    disability_cert = fields.Float("Disability Cert Number", help="""Persons
                        with Disability must apply for certificate of
                        exemption from Commissioner of Domestic Taxes.
                        Cetificate is issued within 30 days and is valid for 3
                        years""")
    hosp = fields.Boolean("H.O.S.P Deposit?", help="""Check this box if the
                        employee is making monthly deposits in respect of
                        funds deposited in “approved Institution” under
                        "Registered Home Ownership Savings Plan". Such
                        Employee is eligible to a deduction up to a maximum
                        of Kshs. 4,000 /- (Four thousand shillings) per month
                        or Kshs. 48,000/- per annum """)
    hosp_deposit = fields.Float("Actual Deposit to H.O.S.P (Monthly)")
    mortgage = fields.Boolean("Owner Occupied Interest (O.C.I)?", help="""
                        Check this box if the employee is paying any
                        interest on load borrowed to finance the purchase or
                        improvement of his or her own house which is
                        occupying.The amount of interest allowable under the
                        law to be deducted from taxable pay must not exceed
                        Kshs.150,000 per year (equivalent to Kshs. 12,500 per
                        month).""")
    mortgage_interest = fields.Float("Actual Interest paid (Monthly)")
    currency_id = fields.Many2one("res.currency", requied=True,
                    default=lambda self: self.env.company.currency_id)
    nssf_vol = fields.Boolean("NSSF Voluntary Contributions?")
    emp_nssf_vol = fields.Float("Voluntary Member Amount")
    employer_nssf_vol = fields.Float("Voluntary Employer Amount")
    nssf_t3 = fields.Boolean("NSSF Tier III Contributions?")
    emp_amt_nssf_t3 = fields.Float("Tier III Member Amount")
    employer_amt_nssf_t3 = fields.Float("Tier III Employer Amount")


class HrContract(models.Model):
    _inherit = 'hr.contract'

    allowance_ids = fields.One2many('hr.contract.allowance', 'contract_id',
                                    'Allowances')
    deduction_ids = fields.One2many('hr.contract.deductions', 'contract_id',
                                    'Deductions')
    tax_applicable = fields.Selection(related="type_id.tax_applicable",
                        string="Remuneration Model", help="""Select the
                        applicable Taxation rate based on the type of
                        contract given to the employee
                        [PAYE] - Applies to all employments but it does not
                        include earnings from 'casual employment' which means
                        any engagement with any one employer which is made for
                        a period of less than one month, the emoluments of
                        which are calculated by reference to the period of the
                        engagement or shorter intervals
                        [Withholding Tax] - Applies to both resident and non
                        resident individuals hired on consultancy agreements
                        or terms and is deducted from consultancy fees or
                        contractual fees and paid to KRA on monthly basis.""")
    # tax_charged = fields.Float("Tax charged")
    # pension_relief = fields.Float("LESS: Pension cont. relief")
    personal_relief = fields.Float("LESS: Personal relief", default=2400.00)
    # insurance_relief = fields.Float("LESS: Insurance relief")
    # NSSF = fields.Float("NSSF")
    # NHIF = fields.Float("NHIF")
    # WHT = fields.Float("WHT")
    other_ded = fields.Float("Other Deductions")
    bonus = fields.Float("Bonus")
    rem_type = fields.Selection(related="type_id.rem_type", string="Remuneration Model")
    car = fields.Boolean("Car Benefit", help="""Check this box if the employee
                        is provided with a motor vehicle by employer. the
                        chargeable benefit for private use shall be the higher
                        of the rate determined by the Commissioner of taxes
                        and the prescribed rate of benefit. Where such vehicle
                        is hired or leased from third party, employees shall
                        be deemed to have received a benefit in that year of
                        income, equal to the cost of hiring or leasing""")
    car_benefits_ids = fields.One2many('hr.contract.car.benefits', 'contract_id',
                                        'Car Benefits')
    house = fields.Boolean("Housing Benefit?", help="""Check this box if your
                            employee is entitled to housing by employer.
                            Such benefit is taxable""")
    house_type = fields.Selection([('own', "Employer's Owned House"),
                                ('rented', "Employer's Rented House"),
                                ('agric', 'Agriculture Farm'),
                                ('director',
            'House to Non full time service Director')], string="House Type")
    rent = fields.Float("Rent of House/Market Value", help="""This the actual
                        rent of house paid by the employer if the house is
                        rented by employer on behalf of the employee.
                        If the House is owned by the Employer, then this
                        is the Market value of the rent of the house.""")
    rent_recovered = fields.Float("Rent Recovered from Employee",
            help="""This is the actual rent recovered from the employee if
            any""")
    emp_type = fields.Selection(related="employee_id.emp_type", string="Employee Type")

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.job_id = self.employee_id.job_id
            self.department_id = self.employee_id.department_id
            self.active_employee = self.employee_id.active


class HrContractType(models.Model):
    _inherit = "hr.contract.type"

    rem_type = fields.Selection([('monthly', '	Monthly Pay'),
            ('hourly', 'Hourly Pay'), ('daily', 'Daily Pay')],
            string="Remuneration Model",
            requied=True,
            help="""You specify which remuneration model that is used in this
            contract.
            [Monthly] - Employee is paid a predetermined monthly Salary
            [Hourly] - Employee is paid based on number of hours worked
            [Daily] - Employee is paid based on number of days worked""")
    tax_applicable = fields.Selection([('paye', 'P.A.Y.E - Pay As You Earn'),
                    ('wht', 'Withholding Tax')], string="Applicable Tax",
                    default='paye', required=True)


class HrEmployeeAllowance(models.Model):
    _name = 'hr.contract.allowance'
    _description = "Contract Allowances"

    contract_id = fields.Many2one('hr.contract', 'Contract')
    salary_rule_id = fields.Many2one('hr.salary.rule', 'Salary Rule',
                                    domain=[('category_id','=',2)])
    amount = fields.Float('Amount')

class HrEmployeeDeductions(models.Model):
    _name = 'hr.contract.deductions'
    _description = "Contract Deductions"

    contract_id = fields.Many2one('hr.contract', 'Contract')
    salary_rule_id = fields.Many2one('hr.salary.rule', 'Salary Rule',
                                    domain=[('category_id','=',4)])
    amount = fields.Float('Amount')

class HrEmployeeCarBenefits(models.Model):
    _name = 'hr.contract.car.benefits'
    _description = "Car benefits"

    contract_id = fields.Many2one('hr.contract', 'Contract')
    name = fields.Char('Car Registration Number', required=True)
    make = fields.Char('make', requied=True)
    body = fields.Selection([('saloon', 'Saloon Hatch Backs and Estates'),
                            ('pickup', 'Pick Ups,Panel Vans Uncovered'),
                            ('cruiser',
        'Land Rovers/Cruisers(excluding Range Rover and similar cars)')],
        string="Body Type", requied=True)
    cc_rate = fields.Integer("CC Rating", requied=True)
    cost_type = fields.Selection([('hwned', 'Owned'), ('hired', 'Hired')],
                                string="Type of Car Cost", requied=True)
    cost_hire = fields.Float("Cost of Hire")
    cost_own = fields.Float("Cost of Owned Car")


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def compute_sheet(self):
        self.ensure_one()
        context = dict(self._context)
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': from_date.strftime('%B %Y'),
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        if not self.employee_ids:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']
        move = self.env['account.move']
        journal = self.env['account.journal']
        account_move_line_obj = self.env['account.move.line']

        contracts = self.employee_ids._get_contracts(payslip_run.date_start, payslip_run.date_end, states=['open', 'close'])
        contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        work_entries = self.env['hr.work.entry'].search([
            ('date_start', '<=', payslip_run.date_end),
            ('date_stop', '>=', payslip_run.date_start),
            ('employee_id', 'in', self.employee_ids.ids),
        ])
        self._check_undefined_slots(work_entries, payslip_run)

        validated = work_entries.action_validate()
        if not validated:
            raise UserError(_("Some work entries could not be validated."))

        default_values = Payslip.default_get(Payslip.fields_get())
        for contract in contracts:
            if contract.employee_id.emp_type == 'employee':
                values = dict(default_values, **{
                    'employee_id': contract.employee_id.id,
                    'credit_note': payslip_run.credit_note,
                    'payslip_run_id': payslip_run.id,
                    'date_from': payslip_run.date_start,
                    'date_to': payslip_run.date_end,
                    'month': payslip_run.month,
                    'year': payslip_run.year,
                    'contract_id': contract.id,
                    'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
                })
                payslip = self.env['hr.payslip'].new(values)
                payslip._onchange_employee()
                values = payslip._convert_to_write(payslip._cache)
                payslips += Payslip.create(values)
            elif contract.employee_id.emp_type == 'contractor':
                if not contract.employee_id.address_home_id:
                    raise UserError(_("Employee %s doesn't have Address mentioned under Private information.")% (contract.employee_id.name))
                journal = journal.search([('type', '=', 'purchase')], limit=1)
                if not journal:
                    raise UserError(_("Please configure Purchase type Journal."))
                # sales_dept = self.env.ref('l10n_ke_hr_payroll.dep_sales_agents')
                base_account_id = False
                bonus_account_id = False
                if contract.employee_id.job_id and contract.employee_id.job_id.name == 'Sales Agent':
                    base_account_id = self.env['account.account'].search([('code', '=', '60045-2')], limit=1)
                    bonus_account_id = self.env['account.account'].search([('code', '=', '60050')], limit=1)
                move_rec = move.create({
                            'partner_id': contract.employee_id.address_home_id.id,
                            'ref': payslip_run.name,
                            'journal_id': journal.id,
                            'payslip_batch_id': payslip_run.id,
                            'type': 'in_invoice'})
                
                credit_amt = contract.wage/100*5 # 5% of Gross Salary
                bonus_tax_amt = 0
                if contract.bonus:
                    bonus_tax_amt = contract.bonus/100*5
                lines = []
                lines.append(self.get_main_product_credit_vals(move_rec.partner_id,
                    contract.wage - credit_amt - contract.other_ded + contract.bonus - bonus_tax_amt,
                    base_account_id))
                lines.append(self.get_main_product_vals(move_rec.partner_id, contract.wage))
            
                if contract.bonus:
                    lines.append(self.get_bonus_vals(move_rec.partner_id, contract.bonus,
                            bonus_account_id))
                if contract.other_ded:
                    lines.append(self.get_deduction_vals(move_rec.partner_id, contract.other_ded,
                            base_account_id))
                
                inv_lines_list = [(0, 0, line) for line in lines]
                move_rec.with_context({'payroll_bypass': True}).write({'line_ids': inv_lines_list})

                move_rec._recompute_tax_lines()
                context.update({"payroll_bypass": True})
                move_rec.with_context(context)._recompute_dynamic_lines()
        payslips.compute_sheet()
        payslip_run.state = 'verify'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }
    
    def get_main_product_credit_vals(self, partner, credit_amt, base_account_id):
        account = self.env['account.account'].search([('code', '=', '20003')], limit=1).id
        if base_account_id:
            account = base_account_id.id
        return {'account_id': account,
                'credit': credit_amt,
                'exclude_from_invoice_tab': True,
                'partner_id': partner.id,
                'move_id': self.id}
    
    def get_main_product_vals(self, partner, wage):
        tax_rec = self.env.ref('l10n_ke_hr_payroll.WHT')
        account = self.env['account.account'].search([('code', '=', '20002')], limit=1)
        return {'account_id': account.id,
                'debit': wage,
                'product_id': self.env.ref('l10n_ke_hr_payroll.product_product_pro_service').id,
                'name': 'Professional Services',
                'quantity': 1.0,
                'price_unit': wage,
                'tax_ids': [(6,0,[tax_rec.id])],
                'partner_id': partner.id,
                'move_id': self.id}
    
    def get_bonus_vals(self, partner, bonus, bonus_account):
        tax_rec = self.env.ref('l10n_ke_hr_payroll.WHT')
        account = self.env['account.account'].search([('code', '=', '20002')], limit=1)
        if bonus_account:
            account = bonus_account
        return {'account_id': account.id,
                'debit': bonus,
                'name': 'Bonus',
                'quantity': 1.0,
                'price_unit': bonus,
                'tax_ids': [(6,0,[tax_rec.id])],
                'partner_id': partner.id,
                'move_id': self.id}
    
    def get_deduction_vals(self, partner, deduction, base_account_id):
        account = self.env['account.account'].search([('code', '=', '20003')], limit=1).id
        if base_account_id:
            account = base_account_id.id
        return {'account_id': account,
                'credit': deduction,
                'price_unit': deduction,
                'name': 'Other Deductions',
                'quantity': 1.0,
                'partner_id': partner.id,
                'move_id': self.id}

    def _get_available_contracts_domain(self):
        return [('contract_ids.state', 'in', ('open', 'close')), ('company_id', '=', self.env.company.id),
                ('emp_type', 'in', ('employee','contractor'))]
    
    def _get_employee_primary(self):
        emp_rec = self.env['hr.employee'].search([('emp_type','in', ('employee','contractor'))])   
        return  [('id', 'in', emp_rec.ids)]

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees',
                                    default=lambda self: self._get_employees(), required=True, domain=_get_employee_primary)
    

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    month = fields.Selection(MONTH_LIST, string='Month', readonly=True,
                            default=str(int(datetime.now().strftime('%m'))),
                             states={'draft': [('readonly', False)]},
                             required=True)
    year = fields.Char('Year', readonly=True,
                          default=lambda *a: time.strftime('%Y'),
                          states={'draft': [('readonly', False)]},
                          required=True)
    
    @api.onchange('employee_id')
    def onchange_contract(self):
        if not self.contract_id:
            self.worked_days_line_ids = [(6,0,[])]
    
    @api.onchange('month', 'year', 'employee_id')
    def onchange_month(self):
        if self.month:
            month_date = date(int(self.year), int(self.month), 1)
            self.date_from = month_date.replace(day=1)
            self.date_to = month_date.replace(day=base_calendar.monthrange(month_date.year, month_date.month)[1])
            if self.contract_id:
                if (self.contract_id.date_start.month == self.date_from.month and
                        self.contract_id.date_start.year == self.date_from.year and
                        self.contract_id.date_start > self.date_from):
                    self.date_from = self.contract_id.date_start
                if (self.contract_id.date_end and
                        self.contract_id.date_end.month == self.date_to.month and
                        self.contract_id.date_end.year == self.date_to.year and
                        self.contract_id.date_end < self.date_to):
                    self.date_to = self.contract_id.date_end
    
    def _get_non_work_hours(self, date_from, date_to, contract):
        calendar = contract.resource_calendar_id
        nb_of_days = (date_to - date_from).days + 1
        non_work_hours = 0
        for day in range(1, nb_of_days+1): 
            flag_date = date_from.replace(day=day)
            week_day = flag_date.weekday()
            if not [cal_att for cal_att in calendar.attendance_ids
                    if int(cal_att.dayofweek) == int(week_day)]:
                continue
            work_entries = self.env['hr.work.entry'].search(
            [('employee_id', '=', contract.employee_id.id),
            ('state', 'in', ['validated', 'draft']),
            ('contract_id', '=', contract.id),
            ('date_start', '>=', flag_date),
            ('date_stop', '<=', flag_date),
            ])
            if not work_entries:
                non_work_hours += calendar.hours_per_day
        return non_work_hours
        
    
    def _get_worked_day_lines(self):
        """
        :returns: a list of dict containing the worked days values that should be applied for the given payslip
        """
        res = []
        # fill only if the contract as a working schedule linked
        self.ensure_one()
        contract = self.contract_id
        if contract.resource_calendar_id:
            paid_amount = self._get_contract_wage()
            unpaid_work_entry_types = self.struct_id.unpaid_work_entry_type_ids.ids

            month_date = date(int(self.year), int(self.month), 1)
            month_date_from = month_date.replace(day=1)
            month_date_to = month_date.replace(day=base_calendar.monthrange(month_date.year, month_date.month)[1])
            non_work_hours = 0
            if month_date_from != self.date_from or month_date_to != self.date_to:
                non_work_hours = self._get_non_work_hours(month_date_from, month_date_to, contract)
            work_hours = contract._get_work_hours(self.date_from, self.date_to)
            work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
            biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
            add_days_rounding = 0
            for work_entry_type_id, hours in work_hours_ordered:
                work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
                is_paid = work_entry_type_id not in unpaid_work_entry_types
                calendar = contract.resource_calendar_id
                days = round(hours / calendar.hours_per_day, 5) if calendar.hours_per_day else 0
                if work_entry_type_id == biggest_work:
                    days += add_days_rounding
                day_rounded = self._round_days(work_entry_type, days)
                add_days_rounding += (days - day_rounded)
                non_work_hours = round(non_work_hours,5)
                total_hours = hours + non_work_hours 
                attendance_line = {
                    'sequence': work_entry_type.sequence,
                    'work_entry_type_id': work_entry_type_id,
                    'number_of_days': day_rounded,
                    'number_of_hours': hours,
                    'amount': hours * paid_amount / total_hours if is_paid else 0,
                }
                res.append(attendance_line)
        return res

    def action_payslip_done(self):
        """
            Generate the accounting entries related to the selected payslips
            A move is created for each journal and for each month.
        """
        if any(slip.state == 'cancel' for slip in self):
            raise ValidationError(_("You can't validate a cancelled payslip."))
        self.write({'state' : 'done'})
        self.mapped('payslip_run_id').action_close()
        if self.env.context.get('payslip_generate_pdf'):
            for payslip in self:
                if not payslip.struct_id or not payslip.struct_id.report_id:
                    report = self.env.ref('hr_payroll.action_report_payslip', False)
                else:
                    report = payslip.struct_id.report_id
                pdf_content, content_type = report.render_qweb_pdf(payslip.id)
                if payslip.struct_id.report_id.print_report_name:
                    pdf_name = safe_eval(payslip.struct_id.report_id.print_report_name, {'object': payslip})
                else:
                    pdf_name = _("Payslip")
                self.env['ir.attachment'].create({
                    'name': pdf_name,
                    'type': 'binary',
                    'datas': base64.encodestring(pdf_content),
                    'res_model': payslip._name,
                    'res_id': payslip.id
                })
        precision = self.env['decimal.precision'].precision_get('Payroll')

        # Add payslip without run
        payslips_to_post = self.filtered(lambda slip: not slip.payslip_run_id)

        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_to_post |= run.slip_ids

        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

        # Map all payslips by structure journal and pay slips month.
        # {'journal_id': {'month': [slip_ids]}}
        slip_mapped_data = {slip.struct_id.journal_id.id: {fields.Date().end_of(slip.date_to, 'month'): self.env['hr.payslip']} for slip in payslips_to_post}
        for slip in payslips_to_post:
            slip_mapped_data[slip.struct_id.journal_id.id][fields.Date().end_of(slip.date_to, 'month')] |= slip

        for journal_id in slip_mapped_data: # For each journal_id.
            for slip_date in slip_mapped_data[journal_id]: # For each month.
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                date = slip_date
                partner = slip.employee_id.address_home_id and slip.employee_id.address_home_id.id
                move_dict = {
                    'narration': '',
                    'ref': date.strftime('%B %Y'),
                    'journal_id': journal_id,
                    'date': date,
                }

                for slip in slip_mapped_data[journal_id][slip_date]:
                    move_dict['narration'] += slip.number or '' + ' - ' + slip.employee_id.name or ''
                    move_dict['narration'] += '\n'
                    for line in slip.line_ids.filtered(lambda line: line.category_id):
                        amount = -line.total if slip.credit_note else line.total
                        if line.code == 'NET': # Check if the line is the 'Net Salary'.
                            for tmp_line in slip.line_ids.filtered(lambda line: line.category_id):
                                if tmp_line.salary_rule_id.not_computed_in_net: # Check if the rule must be computed in the 'Net Salary' or not.
                                    if amount > 0:
                                        amount -= abs(tmp_line.total)
                                    elif amount < 0:
                                        amount += abs(tmp_line.total)
                        if float_is_zero(amount, precision_digits=precision):
                            continue
                        debit_account_id = line.salary_rule_id.account_debit.id
                        credit_account_id = line.salary_rule_id.account_credit.id

                        if debit_account_id: # If the rule has a debit account.
                            debit = amount if amount > 0.0 else 0.0
                            credit = -amount if amount < 0.0 else 0.0

                            existing_debit_lines = (
                                line_id for line_id in line_ids if
                                line_id['name'] == line.name
                                and line_id['account_id'] == debit_account_id
                                and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0)))
                            debit_line = next(existing_debit_lines, False)

                            if not debit_line:
                                debit_line = {
                                    'name': line.name,
                                    'partner_id': partner or False,
                                    'account_id': debit_account_id,
                                    'journal_id': slip.struct_id.journal_id.id,
                                    'date': date,
                                    'debit': debit,
                                    'credit': credit,
                                    'analytic_account_id': line.salary_rule_id.analytic_account_id.id or slip.contract_id.analytic_account_id.id,
                                }
                                line_ids.append(debit_line)
                            else:
                                debit_line['debit'] += debit
                                debit_line['credit'] += credit
                        
                        if credit_account_id: # If the rule has a credit account.
                            debit = -amount if amount < 0.0 else 0.0
                            credit = amount if amount > 0.0 else 0.0
                            existing_credit_line = (
                                line_id for line_id in line_ids if
                                line_id['name'] == line.name
                                and line_id['account_id'] == credit_account_id
                                and (line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0)
                            )
                            credit_line = next(existing_credit_line, False)

                            if not credit_line:
                                credit_line = {
                                    'name': 'Payable',
                                    'partner_id': partner or False,
                                    'account_id': credit_account_id,
                                    'journal_id': slip.struct_id.journal_id.id,
                                    'date': date,
                                    'debit': debit,
                                    'credit': credit,
                                    'analytic_account_id': line.salary_rule_id.analytic_account_id.id or slip.contract_id.analytic_account_id.id,
                                }
                                line_ids.append(credit_line)
                            else:
                                credit_line['debit'] += debit
                                credit_line['credit'] += credit

                for line_id in line_ids: # Get the debit and credit sum.
                    debit_sum += line_id['debit']
                    credit_sum += line_id['credit']

                # The code below is called if there is an error in the balance between credit and debit sum.
                if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                    acc_id = slip.journal_id.default_credit_account_id.id
                    if not acc_id:
                        raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_credit = next(existing_adjustment_line, False)

                    if not adjust_credit:
                        adjust_credit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': partner or False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': 0.0,
                            'credit': debit_sum - credit_sum,
                        }
                        line_ids.append(adjust_credit)
                    else:
                        adjust_credit['credit'] = debit_sum - credit_sum

                elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                    acc_id = slip.journal_id.default_debit_account_id.id
                    if not acc_id:
                        raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_debit = next(existing_adjustment_line, False)

                    if not adjust_debit:
                        adjust_debit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': partner or False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': credit_sum - debit_sum,
                            'credit': 0.0,
                        }
                        line_ids.append(adjust_debit)
                    else:
                        adjust_debit['debit'] = credit_sum - debit_sum

                # Add accounting lines in the move
                move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                move = self.env['account.move'].create(move_dict)
                for slip in slip_mapped_data[journal_id][slip_date]:
                    slip.write({'move_id': move.id, 'date': date})
        return True
