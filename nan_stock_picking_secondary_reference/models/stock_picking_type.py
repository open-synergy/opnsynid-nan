# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    second_sequence_id = fields.Many2one(
        string="Second Sequence",
        comodel_name="ir.sequence",
        required=False
    )
