# -*- coding: utf-8 -*-
{
    'name': "Zumi Patch",

    'summary': """
        Fixes sales order name duplication!""",

    'description': """
        Just the summary
    """,

    'author': "@the-macharia",
    'website': "http://atlancis.com",

    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale'],

    # always loaded
    'data': [
        'views/views.xml',
    ]
}
