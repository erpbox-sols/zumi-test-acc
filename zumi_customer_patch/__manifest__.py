# -*- coding: utf-8 -*-
{
    'name': "Zumi Customer Patch",

    'summary': """
        Add market, longitude and latitude as fields!""",

    'description': """
        Add market, (lat, long) as fields to customer model 
    """,

    'author': "@shaddyshad",
    'website': "https://github.com/shaddyshad",

    'category': 'Partner',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock'],

    # always loaded
    'data': [
        'views/res_partner.xml',
        'views/sale_order_view.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
