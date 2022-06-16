# -*- coding: utf-8 -*-
{
    'name': 'Zumi Products',
    'summary': """Zumi Products""",
    'description': 'Zumi Products',
    'author': 'Arpit Goel',
    'website': 'https://www.erpbox-solutions.com/',
    "support": "goelarpit1997@gmail.com",
    'category': 'Inventory',
    'version': '0.1.0',
    'depends': ['sale_management', 'stock', 'purchase'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/product_views.xml',
        'data/ir_cron_data.xml',
    ],
    'license': "Other proprietary",
    "auto_install": False,
    "installable": True,
}