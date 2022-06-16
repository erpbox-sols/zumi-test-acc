# See LICENSE file for full copyright and licensing details.

{
    'name': 'Credit Checker',
    'summary': 'set credit customer for commitment product list',
    'version': '13.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Erpbox solutions',
    'website': 'info@erpbox-solutions.com',
    'sequence': 1,
    'category': 'Extra Tools',
    'depends': ['account', 'scs_dropshipping'],
    'data': [
        'data/credit_checking_action.xml',
        'views/account_move_view.xml',
        ],
    'installable': True,
    'auto_install': False,
}
