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
    def do_transfer(self):
        super(StockPicking, self).\
            action_done()
        for picking in self:
            if picking.state != "done":
                continue
            obj_ir_sequence = self.env['ir.sequence']

            second_sequence =\
                picking.picking_type_id.second_sequence_id

            if second_sequence:
                picking.write({"secondary_ref": obj_ir_sequence.next_by_id(
                    second_sequence.id)})
        return True
