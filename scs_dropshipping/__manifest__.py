# See LICENSE file for full copyright and licensing details.

{
    'name': 'Dropship Extended',
    'summary': 'This module help to update cost price in sale order based on purchase price',
    'version': '13.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    'sequence': 1,
    'category': 'Extra Tools',
    'depends': ['sale','stock_dropshipping','sale_margin','account'],
    'data': ['security/ir.model.access.csv',
             'data/corn_view.xml',
             'wizard/wiz_sale_cost_update.xml',
             'wizard/wiz_product_cost_update.xml',
             'wizard/wiz_invoice_update_saleperson.xml',
             'views/sale_order_view.xml',
             'views/account_move_view.xml',
             'report/account_move_reprot.xml',
             'views/stock_picking_view.xml',
             'report/inventory_target.xml'
             ],
    'installable': True,
    'auto_install': False,
}
