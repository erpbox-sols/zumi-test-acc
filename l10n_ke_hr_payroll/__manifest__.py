{
    "name": "Kenya Payroll",
    "version": "13.0.1.0.0",
    "depends": ["hr_payroll",
                'account',
                'hr_payroll_account',
                'hr_contract_types',
                # 'l10n_ke',
                'base_vat'],
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.serpentcs.com",
    "maintainer": "Serpent Consulting Services Pvt. Ltd.",
    "category": "Payroll Localization",
    "license": "LGPL-3",
    "sequence": 1,
    "description": """
        Kenya Payroll Salary Rules.
    """,
    "summary": """
        Kenya Payroll Salary Rules.
        ======================================

        -Configuration of hr_payroll for Kenya localization
        -All main contributions rules for Kenya payslip.
    """,
    'data': [
        'security/ir.model.access.csv',
        'data/account_data.xml',
        'data/hr_salary_rule_category_data.xml',
        'data/salary_rule.xml',
        'data/hr_rule_input.xml',
        'data/product_data.xml',
        'data/email_template.xml',
        'views/hr_payslip_view.xml',
        'views/hr_contract_view.xml',
        'wizard/payslip_send_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    # "price": 149,
    # "currency": 'EUR',
}
