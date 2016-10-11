# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    raw_material_journal_ids = fields.Many2many(
        string="Analytic Journal for Raw Materials",
        comodel_name="account.analytic.journal",
        relation="rel_raw_material_journals_2_company",
        column1="company_id",
        column2="journal_id",
    )
    direct_labour_journal_ids = fields.Many2many(
        string="Analytic Journal for Direcy Labour",
        comodel_name="account.analytic.journal",
        relation="rel_direct_labour_journals_2_company",
        column1="company_id",
        column2="journal_id",
    )
    foh_journal_ids = fields.Many2many(
        string="Analytic Journal for FOH",
        comodel_name="account.analytic.journal",
        relation="rel_foh_journals_2_company",
        column1="company_id",
        column2="journal_id",
    )
