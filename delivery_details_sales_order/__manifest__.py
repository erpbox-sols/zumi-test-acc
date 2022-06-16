# -*- coding: utf-8 -*-
{
    'name': "Delivery details for sales order",

    'summary': """
        Adds delivery agent name and id to a given sales order """,

    'author': "@shaddyshad",
    'website': "https://github.com/shaddyshad",

    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'views/res_delivery.xml'
    ]
}
