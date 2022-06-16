# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class StockMoveReport(models.Model):
    _name = "stock.move.report"
    _description = 'Dropship Delivery'
    _auto = False

    drop_per = fields.Float(string="Dropship", readonly=True)
    delv_per = fields.Float(string='Delivery', readonly=True)
    picking_name = fields.Char(string='Picking Name', readonly=True)
    date = fields.Date(string='Date', readonly=True)
    
    def init(self):
        tools.drop_view_if_exists(self._cr, 'stock_move_report')
        self._cr.execute("""
            CREATE or REPLACE view stock_move_report as (
                SELECT
                    min(sm.id) as id,
                    spt.name as picking_name,
                    sm.date as date,
                    CASE
                        WHEN
                            spt.name = 'Delivery Orders'
                        THEN
                            sum(sm.product_uom_qty) / (SELECT
                                                            sum(sm.product_uom_qty)
                                                        FROM
                                                            stock_move sm
                                                        INNER JOIN
                                                            stock_picking_type spt
                                                        ON
                                                            sm.picking_type_id = spt.id
                                                        WHERE
                                                            spt.name in ('Delivery Orders','Dropship')
                                                        AND
                                                            sm.state='done')*100
                        ELSE 0
                    END as drop_per,
                    
                    CASE
                        WHEN
                            spt.name = 'Dropship'
                        THEN
                            sum(sm.product_uom_qty) / (SELECT
                                                            sum(sm.product_uom_qty)
                                                        FROM
                                                            stock_move sm
                                                        INNER JOIN
                                                            stock_picking_type spt
                                                        ON
                                                            sm.picking_type_id = spt.id
                                                        WHERE
                                                            spt.name in ('Delivery Orders','Dropship')
                                                        AND
                                                            sm.state='done')*100
                        ELSE 0
                    END as delv_per
                FROM
                    stock_move sm
                    INNER JOIN
                        stock_picking_type spt
                    ON
                        sm.picking_type_id = spt.id
                WHERE
                    spt.name in ('Delivery Orders','Dropship')
                AND
                    sm.state='done'
                GROUP BY
                    spt.name,
                    sm.date
            )
        """)
