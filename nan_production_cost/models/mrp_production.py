# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields


class MrpByproductCostCalculation(models.Model):
    _name = "nan.mrp_byproduct_cost_calculation"
    _description = "Byproduct Cost Calculation"

    @api.multi
    def _compute_cost(self):
        for cost in self:
            cost.byproduct_cost = cost.multiplier * \
                cost.production_id.raw_material_cost
            cost.avg_byproduct_cost = cost.multiplier * \
                cost.production_id.avg_raw_material_cost
            cost.std_byproduct_cost = cost.multiplier * \
                cost.production_id.std_raw_material_cost

    production_id = fields.Many2one(
        string="# MO",
        comodel_name="mrp.production",
    )
    product_id = fields.Many2one(
        string="Byproduct",
        comodel_name="product.product",
        required=True,
    )
    multiplier = fields.Float(
        string="Multiplier",
    )
    byproduct_cost = fields.Float(
        string="Byproduct Cost",
        compute="_compute_cost",
    )
    avg_byproduct_cost = fields.Float(
        string="Avg. Byproduct Cost",
        compute="_compute_cost",
    )
    std_byproduct_cost = fields.Float(
        string="Std. Byproduct Cost",
        compute="_compute_cost",
    )


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    @api.depends(
        "analytic_line_ids",
        "analytic_line_ids.amount",
        "analytic_line_ids.estim_std_cost",
        "analytic_line_ids.estim_avg_cost",
        "byproduct_calculation_ids",
        "byproduct_calculation_ids.multiplier")
    @api.multi
    def _compute_cost(self):
        obj_line = self.env["account.analytic.line"]
        for production in self:
            production.byproduct_cost = production.raw_material_cost = \
                production.direct_labour_cost = production.foh_cost = \
                0.0
            production.raw_material_cost_ids = obj_line.search([
                ("journal_id", "in", production.raw_material_journal_ids.ids),
                ("mrp_production_id", "=", production.id),
            ])
            production.direct_labour_cost_ids = obj_line.search([
                ("journal_id", "in", production.direct_labour_journal_ids.ids),
                ("mrp_production_id", "=", production.id),
            ])
            production.foh_cost_ids = obj_line.search([
                ("journal_id", "in", production.foh_journal_ids.ids),
                ("mrp_production_id", "=", production.id),
            ])
            for cost1 in production.raw_material_cost_ids:
                production.raw_material_cost += (-1.0 * cost1.amount)
                production.std_raw_material_cost += (-1.0 *
                                                     cost1.estim_std_cost)
                production.avg_raw_material_cost += (-1.0 *
                                                     cost1.estim_avg_cost)
            for cost2 in production.direct_labour_cost_ids:
                production.direct_labour_cost += (-1.0 * cost2.amount)
                production.std_direct_labour_cost += (-1.0 *
                                                      cost2.estim_std_cost)
                production.avg_direct_labour_cost += (-1.0 *
                                                      cost2.estim_avg_cost)
            for cost3 in production.foh_cost_ids:
                production.foh_cost += (-1.0 * cost3.amount)
                production.std_foh_cost += (-1.0 * cost3.estim_std_cost)
                production.avg_foh_cost += (-1.0 * cost3.estim_avg_cost)
            for byproduct in production.byproduct_calculation_ids:
                production.byproduct_cost += byproduct.byproduct_cost
                production.avg_byproduct_cost += byproduct.avg_byproduct_cost
                production.std_byproduct_cost += byproduct.std_byproduct_cost
            production.avg_cost = production.avg_raw_material_cost - \
                production.avg_byproduct_cost + \
                production.avg_direct_labour_cost + \
                production.avg_foh_cost
            production.std_cost = production.std_raw_material_cost - \
                production.std_byproduct_cost + \
                production.std_direct_labour_cost + \
                production.std_foh_cost
            production.main_product_cost = production.raw_material_cost - \
                production.byproduct_cost + production.direct_labour_cost + \
                production.foh_cost

    @api.multi
    def _inverse_raw_material_cost(self):
        obj_line = self.env["account.analytic.line"]
        for mo in self:
            if not mo.raw_material_cost_ids:
                pass
            for dl in mo.raw_material_cost_ids:
                if isinstance(dl.id, models.NewId):
                    product = dl.product_id and dl.product_id.id or False
                    obj_line.create({
                        "name": dl.name,
                        "account_id": dl.account_id.id,
                        "general_account_id": dl.general_account_id.id,
                        "journal_id": dl.journal_id.id,
                        "product_id": product,
                        "amount": dl.amount,
                        "estim_std_cost": dl.estim_std_cost,
                        "estim_avg_cost": dl.estim_avg_cost,
                        "mrp_production_id": mo.id,
                        "date": dl.date})
            # criteria = [
            #     ("id", "not in", mo.direct_labour_cost_ids.ids),
            #     ("mrp_production_id", "=", mo.id),
            #     ("journal_id", "in", mo.direct_labour_journal_ids.ids),
            #     ]
            # del_lines = obj_line.search(criteria)
            # del_lines.unlink()

    @api.multi
    def _inverse_direct_labour_cost(self):
        obj_line = self.env["account.analytic.line"]
        for mo in self:
            if not mo.direct_labour_cost_ids:
                pass
            for dl in mo.direct_labour_cost_ids:
                if isinstance(dl.id, models.NewId):
                    product = dl.product_id and dl.product_id.id or False
                    obj_line.create({
                        "name": dl.name,
                        "account_id": dl.account_id.id,
                        "general_account_id": dl.general_account_id.id,
                        "journal_id": dl.journal_id.id,
                        "product_id": product,
                        "amount": dl.amount,
                        "estim_std_cost": dl.estim_std_cost,
                        "estim_avg_cost": dl.estim_avg_cost,
                        "mrp_production_id": mo.id,
                        "date": dl.date})
            # criteria = [
            #     ("id", "not in", mo.direct_labour_cost_ids.ids),
            #     ("mrp_production_id", "=", mo.id),
            #     ("journal_id", "in", mo.direct_labour_journal_ids.ids),
            #     ]
            # del_lines = obj_line.search(criteria)
            # del_lines.unlink()

    @api.multi
    def _inverse_foh_cost(self):
        obj_line = self.env["account.analytic.line"]
        for mo in self:
            if not mo.foh_cost_ids:
                pass
            for dl in mo.foh_cost_ids:
                if isinstance(dl.id, models.NewId):
                    product = dl.product_id and dl.product_id.id or False
                    obj_line.create({
                        "name": dl.name,
                        "account_id": dl.account_id.id,
                        "general_account_id": dl.general_account_id.id,
                        "journal_id": dl.journal_id.id,
                        "product_id": product,
                        "amount": dl.amount,
                        "estim_std_cost": dl.estim_std_cost,
                        "estim_avg_cost": dl.estim_avg_cost,
                        "mrp_production_id": mo.id,
                        "date": dl.date})
            # criteria = [
            #     ("id", "not in", mo.foh_cost_ids.ids),
            #     ("mrp_production_id", "=", mo.id),
            #     ("journal_id", "in", mo.foh_journal_ids.ids),
            #     ]
            # del_lines = obj_line.search(criteria)
            # del_lines.unlink()

    raw_material_journal_ids = fields.Many2many(
        string="Raw Material Journals",
        comodel_name="account.analytic.journal",
        related="company_id.raw_material_journal_ids",
        store=False,
        readonly=True,
    )
    direct_labour_journal_ids = fields.Many2many(
        string="Direct Labour Journals",
        comodel_name="account.analytic.journal",
        related="company_id.direct_labour_journal_ids",
        store=False,
        readonly=True,
    )
    foh_journal_ids = fields.Many2many(
        string="FOH Journals",
        comodel_name="account.analytic.journal",
        related="company_id.foh_journal_ids",
        store=False,
        readonly=True,
    )
    raw_material_cost_ids = fields.One2many(
        string="Raw Material Cost",
        comodel_name="account.analytic.line",
        inverse_name="mrp_production_id",
        compute="_compute_cost",
        store=False,
        inverse="_inverse_raw_material_cost",
    )
    raw_material_cost = fields.Float(
        string="Raw Material Cost",
        compute="_compute_cost",
        store=False,
    )
    avg_raw_material_cost = fields.Float(
        string="Avg. Raw Material Cost",
        compute="_compute_cost",
        store=False,
    )
    std_raw_material_cost = fields.Float(
        string="Std. Raw Material Cost",
        compute="_compute_cost",
        store=False,
    )
    direct_labour_cost_ids = fields.One2many(
        string="Direct Labour Cost",
        comodel_name="account.analytic.line",
        inverse_name="mrp_production_id",
        compute="_compute_cost",
        store=False,
        inverse="_inverse_direct_labour_cost",
    )
    direct_labour_cost = fields.Float(
        string="Direct Labour Cost",
        compute="_compute_cost",
        store=False,
    )
    avg_direct_labour_cost = fields.Float(
        string="Avg. Direct Labour Cost",
        compute="_compute_cost",
        store=False,
    )
    std_direct_labour_cost = fields.Float(
        string="Std. Direct Labour Cost",
        compute="_compute_cost",
        store=False,
    )
    foh_cost_ids = fields.One2many(
        string="FOH Cost",
        comodel_name="account.analytic.line",
        inverse_name="mrp_production_id",
        compute="_compute_cost",
        store=False,
        inverse="_inverse_foh_cost",
    )
    foh_cost = fields.Float(
        string="FOH Cost",
        compute="_compute_cost",
        store=False,
    )
    avg_foh_cost = fields.Float(
        string="Avg. FOH Cost",
        compute="_compute_cost",
        store=False,
    )
    std_foh_cost = fields.Float(
        string="Std. FOH Cost",
        compute="_compute_cost",
        store=False,
    )
    byproduct_calculation_ids = fields.One2many(
        string="Byproduct Calculation",
        comodel_name="nan.mrp_byproduct_cost_calculation",
        inverse_name="production_id",
        ondelete="cascade",
    )
    byproduct_cost = fields.Float(
        string="Byproduct Cost",
        compute="_compute_cost",
    )
    avg_byproduct_cost = fields.Float(
        string="Avg. Byproduct Cost",
        compute="_compute_cost",
    )
    std_byproduct_cost = fields.Float(
        string="Std. Byproduct Cost",
        compute="_compute_cost",
    )
    main_product_cost = fields.Float(
        string="Main Product Cost",
        compute="_compute_cost",
    )
    avg_cost = fields.Float(
        compute="_compute_cost",
    )
    std_cost = fields.Float(
        compute="_compute_cost",
    )

    @api.multi
    def _open_cost(self, journals, title=""):
        self.ensure_one()
        journal_ids = journals.ids
        view = self.env.ref(
            "nan_production_cost.account_analytic_line_view_tree")
        domain = [
            ('journal_id', 'in', journal_ids),
            ('mrp_production_id', '=', self.id)
        ]
        context = {
            "default_mrp_production_id": self.id,
            "default_product_id": False,
            "default_general_account_id": False,
            "default_account_id": self.analytic_account_id.id,
        }
        result = {
            "name": title,
            "type": "ir.actions.act_window",
            "res_model": "account.analytic.line",
            "view_type": "form",
            "view_mode": "tree",
            "view_id": view.id,
            "domain": domain,
            "context": context,
        }
        return result

    @api.multi
    def action_open_raw_material_cost(self):
        self.ensure_one()
        result = self._open_cost(
            self.raw_material_journal_ids,
            "Raw Material Cost",
        )
        return result

    @api.multi
    def action_open_direct_labour_cost(self):
        self.ensure_one()
        result = self._open_cost(
            self.direct_labour_journal_ids,
            "Direct Labour Cost",
        )
        return result

    @api.multi
    def action_open_foh_cost(self):
        self.ensure_one()
        result = self._open_cost(
            self.foh_journal_ids,
            "FOH Cost",
        )
        return result

    @api.multi
    def bom_id_change(self, bom_id):
        result = super(MrpProduction, self).bom_id_change(bom_id)
        obj_bom = self.env["mrp.bom"]
        a = []

        if bom_id:
            bom = obj_bom.browse(bom_id)

            if bom.sub_products:
                for product in bom.sub_products:
                    res = {
                        "product_id": product.product_id.id,
                    }
                    a.append((0, 0, res))

        result["value"].update({"byproduct_calculation_ids":  a})
        return result
