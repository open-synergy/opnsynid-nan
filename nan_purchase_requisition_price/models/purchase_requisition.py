# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.multi
    def _compute_all(self):
        for pr in self:
            pr.amount_total = 0.0
            for line in pr.line_ids:
                pr.amount_total += line.price_subtotal

    amount_total = fields.Float(
        string='Estimated Price',
        digits=dp.get_precision('Product Price'),
        compute='_compute_all',
    )


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    @api.multi
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.price_unit * line.product_qty

    price_unit = fields.Float(
        string='Estimated Unit Price',
        digits=dp.get_precision('Product Price'),
        default=0,
    )

    price_subtotal = fields.Float(
        string='Estimated Price Subtotal',
        digits=dp.get_precision('Product Price'),
        compute='_compute_subtotal',
    )
