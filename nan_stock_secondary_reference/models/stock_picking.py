# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    secondary_ref = fields.Char(
        string="Secondary Reference",
        readonly=True
    )

    @api.multi
    def action_done(self):
        res = super(StockPicking, self).\
            action_done()

        obj_ir_sequence = self.env['ir.sequence']

        second_sequence =\
            self.picking_type_id.second_sequence_id

        if second_sequence:
            self.secondary_ref = obj_ir_sequence.next_by_id(
                second_sequence.id)
        return res
