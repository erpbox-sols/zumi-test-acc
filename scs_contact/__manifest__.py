# See LICENSE file for full copyright and licensing details.

{
    'name': 'Contact Extended',
    'summary': 'This module help to added fields in the contacts',
    'version': '13.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'sequence': 1,
    'category': 'Extra Tools',
    'depends': ['contacts', 'hr','sale','sale_management','account_followup'],
    'data': ['views/res_partner_view.xml',
            'views/sale_order_view.xml'],
    'installable': True,
    'auto_install': False,
}
