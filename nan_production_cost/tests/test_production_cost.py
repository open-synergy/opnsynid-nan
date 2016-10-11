# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class ProductionCostCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(ProductionCostCase, self).setUp(*args, **kwargs)
        self.obj_product = self.env[
            "product.product"]
        self.obj_bom = self.env[
            "mrp.bom"]
        self.obj_bom_line = self.env[
            "mrp.bom.line"]
        self.obj_mo = self.env[
            "mrp.production"]
        self.obj_byproduct = self.env[
            "mrp.subproduct"]
        self.obj_analytic_line = self.env[
            "account.analytic.line"]
        self.kg = self.env.ref(
            "product.product_uom_kgm")
        self.main_product = self._create_product(
            "Iso Eugenol")
        self.raw_product1 = self._create_product(
            "Crude Iso Eugenol",
            1500.00)
        self.byproduct1 = self._create_product(
            "Iso Eugenol FF1")
        self.byproduct2 = self._create_product(
            "Iso Eugenol FF2")
        self.byproduct3 = self._create_product(
            "Iso Eugenol FF3")
        self.bom = self.obj_bom.create({
            "name": "Iso Eugenol",
            "type": "normal",
            "product_tmpl_id": self.main_product.product_tmpl_id.id,
            "product_qty": 1.0,
            "product_uom": self.kg.id,
        })
        self.obj_bom_line.create({
            "bom_id": self.bom.id,
            "type": "normal",
            "product_id": self.raw_product1.id,
            "product_uom": self.kg.id,
            "product_qty": 1.0,
        })
        self.obj_byproduct.create({
            "bom_id": self.bom.id,
            "subproduct_type": "variable",
            "product_id": self.byproduct1.id,
            "product_uom": self.kg.id,
            "product_qty": 0.1,
        })
        self.obj_byproduct.create({
            "bom_id": self.bom.id,
            "subproduct_type": "variable",
            "product_id": self.byproduct2.id,
            "product_uom": self.kg.id,
            "product_qty": 0.1,
        })
        self.obj_byproduct.create({
            "bom_id": self.bom.id,
            "subproduct_type": "variable",
            "product_id": self.byproduct3.id,
            "product_uom": self.kg.id,
            "product_qty": 0.1,
        })
        self.journal1 = self.env.ref(
            "mrp.analytic_journal_materials")
        self.journal2 = self.env.ref(
            "mrp.analytic_journal_operators")
        self.journal3 = self.env[
            "account.analytic.journal"].create({
                "name": "FOH Journal",
                "type": "general"})
        self.company = self.env.ref("base.main_company")
        self.company.write({
            "raw_material_journal_ids": [(6, 0, [self.journal1.id])],
            "direct_labour_journal_ids": [(6, 0, [self.journal2.id])],
            "foh_journal_ids": [(6, 0, [self.journal3.id])],
        })

    def test_1(self):
        mo = self.obj_mo.create({
            "bom_id": self.bom.id,
            "product_id": self.main_product.id,
            "product_uom": self.kg.id,
            "product_qty": 100.00,
        })
        onchange = mo.bom_id_change(
            self.bom.id)
        mo.write({
            "byproduct_calculation_ids": onchange[
                "value"]["byproduct_calculation_ids"],
        })
        const = 1
        for byproduct in mo.byproduct_calculation_ids:
            byproduct.multiplier = 0.01 * const
            const += 1
        self._create_direct_labour_cost(
            mo, amount=20000.0)
        self._create_foh_cost(
            mo, amount=3000.0)
        mo.signal_workflow("button_confirm")
        self.assertEqual(
            len(mo.byproduct_calculation_ids),
            3)
        mo.action_open_raw_material_cost()
        mo.action_open_direct_labour_cost()
        mo.action_open_foh_cost()
        for consu in mo.move_lines:
            consu.action_done()
        self.assertEqual(
            mo.raw_material_cost,
            150000.0)
        for byproduct in mo.byproduct_calculation_ids:
            self.assertEqual(
                byproduct.byproduct_cost,
                byproduct.multiplier * 150000.00)
        self.assertEqual(
            mo.byproduct_cost,
            9000.0)
        self.assertEqual(
            mo.main_product_cost,
            164000.0)

    def _create_product(self, name, cost=0.0):
        return self.obj_product.create({
            "name": name,
            "uom_id": self.kg.id,
            "uom_po_id": self.kg.id,
            "cost_method": "real",
            "standard_price": cost,
        })

    def _create_cost(
            self, mo, name, journal, product=False, amount=0.0):
        account = False
        if product:
            name = product.name
            if product.property_account_expense:
                account = product.property_account_expense.id
            else:
                categ = product.categ_id
                account = categ.property_account_expense_categ.id
        if not account:
            account = self.env["ir.property"].with_context(
                force_company=self.company.id).get(
                    "property_account_expense_categ", "product.category")

        if not mo.analytic_account_id:
            analytic = self.env["account.analytic.account"].search([
                ("type", "=", "normal"),
            ], limit=1)
        else:
            analytic = mo.analytic_account_id

        return self.obj_analytic_line.create({
            "name": name,
            "product_id": product and product.id or False,
            "amount": -1.0 * amount,
            "journal_id": journal.id,
            "account_id": analytic.id,
            "general_account_id": account.id,
            "mrp_production_id": mo.id,
        })

    def _create_direct_labour_cost(
            self, mo, product=False, amount=0.0):
        name = "Direct Labour Cost Example"
        self._create_cost(
            mo, name, self.journal2, product, amount)

    def _create_foh_cost(
            self, mo, product=False, amount=0.0):
        name = "FOH Cost Example"
        self._create_cost(
            mo, name, self.journal3, product, amount)
