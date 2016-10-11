# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.onchange("product_id")
    def onchange_product(self):
        account = False
        if self.product_id:
            self.name = self.product_id.name
            product = self.product_id
            categ = self.product_id.categ_id
            if product.property_account_expense:
                account = product.property_account_expense.id
            else:
                if categ.property_account_expense_categ:
                    account = categ.property_account_expense_categ.id
        self.general_account_id = account
