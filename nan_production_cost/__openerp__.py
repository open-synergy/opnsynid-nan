# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Natura - Production Cost Calculation",
    "version": "8.0.2.0.0",
    "category": "MRP",
    "website": "https://opensynergy-indonesia.com",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "mrp_byproduct",
        "mrp_production_real_cost",
        "mrp_production_estimated_cost",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "views/mrp_production_views.xml",
        "views/account_analytic_line_views.xml",
    ],
}
