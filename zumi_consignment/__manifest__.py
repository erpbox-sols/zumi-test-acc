# -*- coding: utf-8 -*-
{
    'name': 'Zumi Consignment',
    'summary': """Zumi Consignment""",
    'description': 'Zumi Consignment',
    'author': 'Arpit Goel',
    'website': 'https://www.erpbox-solutions.com/',
    "support": "goelarpit1997@gmail.com",
    'category': 'Inventory',
    'version': '0.1.0',
    'depends': ['sale_management', 'stock', 'purchase'],
    'data': [
        # 'security/ir.model.access.csv',
        'reports/stock_report_template.xml',
        'views/stock_views.xml',
    ],
    'license': "Other proprietary",
    "auto_install": False,
    "installable": True,
}