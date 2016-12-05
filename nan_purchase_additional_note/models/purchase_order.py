# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    notes_po = fields.Text(
        string="Notes PO")
