# -*- coding: utf-8 -*-
{
    'name': 'Zumi Africa Payment Report',
    'summary': """Zumi Africa Payment Report""",
    'description': 'Zumi Africa Payment Report',
    'author': 'Arpit Goel',
    'website': 'https://www.erpbox-solutions.com/',
    "support": "goelarpit1997@gmail.com",
    'category': 'Accounting',
    'version': '0.1.0',
    'depends': ['account', 'contacts', 'sale_management', 'stock', 'mrp', 'purchase', 'account_asset', 'hr'],
    'data': [
        # 'security/ir.model.access.csv',
        'reports/outstanding_payment_report_template.xml',
        'reports/payment_report_view.xml',
    ],
    'license': "Other proprietary",
    "auto_install": False,
    "installable": True,
}