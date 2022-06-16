# -*- coding: utf-8 -*-
{
    'name': 'Zumi Africa Sales',
    'summary': """Zumi Africa Sales""",
    'description': 'Zumi Africa Sales',
    'author': 'Arpit Goel',
    'website': 'https://www.erpbox-solutions.com/',
    "support": "goelarpit1997@gmail.com",
    'category': 'Accounting',
    'version': '0.1.0',
    'depends': ['sale_management','account', 'account_accountant', 'purchase'],
    'data': [
        'security/zumi_africa_security.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/purchase_order_views.xml',
    ],
    'license': "Other proprietary",
    "auto_install": False,
    "installable": True,
}