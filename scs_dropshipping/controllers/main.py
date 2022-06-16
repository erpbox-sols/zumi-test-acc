# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import datetime
from odoo.http import request
from odoo import http


class ProductController(http.Controller):

    @http.route('/get/product', type='json', auth="public")
    def get_product_details(self, **post):
        """
            - Get a list of all stored products
            - To get field value, pass field in the list
            Returns:
                A list of dict mappings containing product details 
                e.g [{id: 1, lst_price: 10.0, standard_price: 11.0, barcode: 121923, partner_ref: 23}]
        """
        product_obj = request.env['product.product']
        product_data = product_obj.sudo().search_read(domain=post.get('domain'), fields=post.get('fields'))
        return product_data

    @http.route('/get/customer', type='json', auth="public")
    def get_customer_details(self, **post):
        """
            - Get a list of customers from odoo
            - To get field value, pass field in the list
            Returns
                A list of dict mappings representing the customers on odoo 
                e.g [{id: 1, name: 'shad'}]
        """
        partner_obj = request.env['res.partner']
        partner_data = partner_obj.sudo().search_read(domain=post.get('domain'), fields=post.get('fields'))
        return partner_data

    @http.route('/get/category', type='json', auth="public")
    def get_categories(self, **post):
        """
            Get a list of all product categories available 
        """
        categ_obj = request.env['product.category']
        categories_data = categ_obj.sudo().search_read(fields=post.get('fields'))
        return categories_data
