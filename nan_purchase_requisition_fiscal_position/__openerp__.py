# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Purchase Requisition Fiscal Position",
    "version": "8.0.1.0.0",
    "category": "Purchase",
    "website": "https://opensynergy-indonesia.com/",
    "author": "Andhitia Rama,OpenSynergy Indonesia",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account_accountant",
        "purchase_requisition",
    ],
    "data": [
        "views/purchase_requisition_views.xml",
    ],
}
