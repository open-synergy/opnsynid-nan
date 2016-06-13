# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    fiscal_position_id = fields.Many2one(
        string='Fiscal Position',
        comodel_name='account.fiscal.position',
        )
