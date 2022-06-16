# See LICENSE file for full copyright and licensing details.

{
    'name': 'Access Rights',
    'summary': 'Customisation For Access Rights',
    'version': '13.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Erpbox solutions',
    'website': 'info@erpbox-solutions.com',
    'sequence': 1,
    'category': 'Extra Tools',
    'depends': ['base', 'product', 'stock'],
    'data': [
        'security/group.xml',
        'views/base.xml',
    ],
    'installable': True,
    'auto_install': False,
}
