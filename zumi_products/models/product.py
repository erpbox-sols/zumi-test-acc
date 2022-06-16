from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _cron_product_variant_assign(self):
        product_template_ids = self.search([])
        for record in product_template_ids:
            if record.attribute_line_ids:
                product_attribute_value_ids = record.attribute_line_ids.mapped('value_ids').filtered(lambda x: x.supplier_id != False)
                for rec in product_attribute_value_ids:
                    product_template_attribute_value_ids = self.env['product.template.attribute.value'].sudo().search([('product_attribute_value_id', '=', rec.id)])
                    product_variant_id = False
                    for product_template_attribute_value_id in product_template_attribute_value_ids:
                        product_variant_id = record.product_variant_ids.filtered(lambda x: product_template_attribute_value_id.id in x.product_template_attribute_value_ids.ids)
                        if product_variant_id:
                            product_variant_id = product_variant_id[0]
                            break
                    variant_seller_ids = record.mapped('variant_seller_ids')
                    seller_ids = variant_seller_ids.filtered(lambda x: not x.product_id and x.name.id == rec.supplier_id.id)
                    for seller_id in seller_ids:
                        seller_id.update({
                                'product_id': product_variant_id.id,
                            })

    # @api.model
    # def create(self, vals):
    #     res = super(ProductTemplate, self).create(vals)
    #     if res.attribute_line_ids:
    #         product_attribute_value_ids = res.attribute_line_ids.mapped('value_ids').filtered(lambda x: x.supplier_id != False)
    #         for rec in product_attribute_value_ids:
    #             product_template_attribute_value_ids = self.env['product.template.attribute.value'].sudo().search([('product_attribute_value_id', '=', rec.id)])
    #             product_variant_id = False
    #             for product_template_attribute_value_id in product_template_attribute_value_ids:
    #                 product_variant_id = res.product_variant_ids.filtered(lambda x: product_template_attribute_value_id.id in x.product_template_attribute_value_ids.ids)
    #                 if product_variant_id:
    #                     break
    #             product_supplierinfo_id = self.env['product.supplierinfo'].sudo().search([('product_tmpl_id', '=', record.id), ('name', '=', rec.supplier_id.id)])
    #             if not product_supplierinfo_id:
    #             print("***************************   create")
    #             res.variant_seller_ids.create({
    #                     'name': rec.supplier_id.id,
    #                     'product_id': product_variant_id.id,
    #                     'product_tmpl_id': res.id,
    #                 })
    #     return res

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        for record in self:
            if record.attribute_line_ids:
                product_attribute_value_ids = record.attribute_line_ids.mapped('value_ids').filtered(lambda x: x.supplier_id != False)
                for rec in product_attribute_value_ids:
                    product_template_attribute_value_ids = self.env['product.template.attribute.value'].sudo().search([('product_attribute_value_id', '=', rec.id)])
                    product_variant_id = False
                    for product_template_attribute_value_id in product_template_attribute_value_ids:
                        product_variant_id = record.product_variant_ids.filtered(lambda x: product_template_attribute_value_id.id in x.product_template_attribute_value_ids.ids)
                        if product_variant_id:
                            break
                    product_supplierinfo_id = self.env['product.supplierinfo'].sudo().search([('product_tmpl_id', '=', record.id), ('name', '=', rec.supplier_id.id)])
                    if not product_supplierinfo_id:
                        product_supplierinfo_id = self.env['product.supplierinfo'].sudo().create({
                                'name': rec.supplier_id.id,
                                'product_id': product_variant_id.id,
                                'product_tmpl_id': record.id,
                            })
                    else:
                        product_supplierinfo_id = self.env['product.supplierinfo'].sudo().update({
                                'name': rec.supplier_id.id,
                                'product_id': product_variant_id.id,
                            })                   
        return res

class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    supplier_id = fields.Many2one('res.partner', string="Supplier")

    @api.constrains('supplier_id')
    def _check_supplier_id(self):
        for rec in self:
            if rec.supplier_id.attribute_code and rec.name != rec.supplier_id.attribute_code:
                raise ValidationError("Every Supplier can have only 1 unique Attribute Code !")

    @api.onchange('supplier_id')
    def _onchange_supplier_id(self):
        if self.supplier_id and self.name:
            if not self.supplier_id.attribute_code:
                self.supplier_id.attribute_code = self.name
