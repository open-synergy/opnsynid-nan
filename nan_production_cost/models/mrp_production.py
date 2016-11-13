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
        for mo in self:
            mo.byproduct_cost = mo.raw_material_cost = \
                mo.direct_labour_cost = mo.foh_cost = \
                0.0
            mo.raw_material_cost_ids = obj_line.search([
                ("journal_id", "in", mo.raw_material_journal_ids.ids),
                ("mrp_production_id", "=", mo.id),
            ])
            mo.direct_labour_cost_ids = obj_line.search([
                ("journal_id", "in", mo.direct_labour_journal_ids.ids),
                ("mrp_production_id", "=", mo.id),
            ])
            mo.foh_cost_ids = obj_line.search([
                ("journal_id", "in", mo.foh_journal_ids.ids),
                ("mrp_production_id", "=", mo.id),
            ])
            for cost1 in mo.raw_material_cost_ids:
                mo.raw_material_cost += (-1.0 * cost1.amount)
                mo.std_raw_material_cost += (-1.0 *
                                             cost1.estim_std_cost)
                mo.avg_raw_material_cost += (-1.0 *
                                             cost1.estim_avg_cost)
            for cost2 in mo.direct_labour_cost_ids:
                mo.direct_labour_cost += (-1.0 * cost2.amount)
                mo.std_direct_labour_cost += (-1.0 *
                                              cost2.estim_std_cost)
                mo.avg_direct_labour_cost += (-1.0 *
                                              cost2.estim_avg_cost)
            for cost3 in mo.foh_cost_ids:
                mo.foh_cost += (-1.0 * cost3.amount)
                mo.std_foh_cost += (-1.0 * cost3.estim_std_cost)
                mo.avg_foh_cost += (-1.0 * cost3.estim_avg_cost)
            for byproduct in mo.byproduct_calculation_ids:
                mo.byproduct_cost += byproduct.byproduct_cost
                mo.avg_byproduct_cost += byproduct.avg_byproduct_cost
                mo.std_byproduct_cost += byproduct.std_byproduct_cost
            mo.avg_cost = mo.avg_raw_material_cost - \
                mo.avg_byproduct_cost + \
                mo.avg_direct_labour_cost + \
                mo.avg_foh_cost
            mo.std_cost = mo.std_raw_material_cost - \
                mo.std_byproduct_cost + \
                mo.std_direct_labour_cost + \
                mo.std_foh_cost
            mo.main_product_cost = mo.raw_material_cost - \
                mo.byproduct_cost + mo.direct_labour_cost + \
                mo.foh_cost
            mo.diff_avg_raw_material_cost = mo.raw_material_cost - \
                mo.avg_raw_material_cost
            mo.diff_std_raw_material_cost = mo.raw_material_cost - \
                mo.std_raw_material_cost
            mo.diff_avg_direct_labour_cost = mo.direct_labour_cost - \
                mo.avg_direct_labour_cost
            mo.diff_std_direct_labour_cost = mo.direct_labour_cost - \
                mo.std_direct_labour_cost
            mo.diff_avg_foh_cost = mo.foh_cost - \
                mo.avg_foh_cost
            mo.diff_std_foh_cost = mo.foh_cost - \
                mo.std_foh_cost
            mo.diff_avg_byproduct_cost = mo.byproduct_cost - \
                mo.avg_byproduct_cost
            mo.diff_std_byproduct_cost = mo.byproduct_cost - \
                mo.std_byproduct_cost
            mo.diff_avg_main_product_cost = mo.main_product_cost - \
                mo.avg_cost
            mo.diff_std_main_product_cost = mo.main_product_cost - \
                mo.std_cost

    @api.multi
    def _inverse_raw_material_cost(self):
        for mo in self:
            pass

    @api.multi
    def _inverse_direct_labour_cost(self):
        obj_line = self.env["account.analytic.line"]
        for mo in self:
            criteria = [
                ("mrp_production_id", "=", mo.id),
                ("id", "not in", mo.direct_labour_cost_ids.ids),
                ("journal_id", "in", mo.direct_labour_journal_ids.ids),
            ]
            del_lines = obj_line.search(criteria)
            del_lines.unlink()
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

    @api.multi
    def _inverse_foh_cost(self):
        obj_line = self.env["account.analytic.line"]
        for mo in self:
            criteria = [
                ("mrp_production_id", "=", mo.id),
                ("id", "not in", mo.foh_cost_ids.ids),
                ("journal_id", "in", mo.foh_journal_ids.ids),
            ]
            del_lines = obj_line.search(criteria)
            del_lines.unlink()
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
    diff_avg_raw_material_cost = fields.Float(
        string="Raw Material Cost Diff Vs. Avg.",
        compute="_compute_cost",
    )
    diff_std_raw_material_cost = fields.Float(
        string="Raw Material Cost Diff Vs. Std.",
        compute="_compute_cost",
    )
    diff_avg_direct_labour_cost = fields.Float(
        string="Direct Labour Cost Diff Vs. Avg.",
        compute="_compute_cost",
    )
    diff_std_direct_labour_cost = fields.Float(
        string="Direct Labour Cost Diff Vs. Std.",
        compute="_compute_cost",
    )
    diff_avg_foh_cost = fields.Float(
        string="FoH Cost Diff Vs. Avg.",
        compute="_compute_cost",
    )
    diff_std_foh_cost = fields.Float(
        string="FoH Cost Diff Vs. Std.",
        compute="_compute_cost",
    )
    diff_avg_byproduct_cost = fields.Float(
        string="Byproduct Cost Diff Vs. Avg.",
        compute="_compute_cost",
    )
    diff_std_byproduct_cost = fields.Float(
        string="Byproduct Cost Diff Vs. Std.",
        compute="_compute_cost",
    )
    diff_avg_main_product_cost = fields.Float(
        string="Main Product Cost Diff Vs. Avg.",
        compute="_compute_cost",
    )
    diff_std_main_product_cost = fields.Float(
        string="Main Product Cost Diff Vs. Std.",
        compute="_compute_cost",
    )

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

    @api.multi
    def calculate_production_estimated_cost(self):
        pass
