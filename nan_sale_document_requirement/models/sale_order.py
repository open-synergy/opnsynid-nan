# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    document_requirement = fields.Text(
        string="Document Requirement")
