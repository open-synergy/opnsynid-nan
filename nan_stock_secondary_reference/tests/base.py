# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class Base(TransactionCase):
    def setUp(self):
        super(Base, self).setUp()
        # Object
        self.obj_res_partner = self.env['res.partner']
        self.obj_ir_sequence = self.env['ir.sequence']
        self.obj_ir_sequence_type = self.env['ir.sequence.type']
        self.obj_picking =\
            self.env['stock.picking']
        self.obj_picking_type =\
            self.env['stock.picking.type']

        # Data
        self.picking_type_1 =\
            self.env.ref('stock.picking_type_in')
        self.picking_type_2 =\
            self.env.ref('stock.picking_type_out')
        self.sequence = self.create_sequence()

        # Data Partner
        self.partner_1 = self.env.ref(
            'base.res_partner_1')
        self.partner_2 = self.env.ref(
            'base.res_partner_2')

    def _get_next_code(self, sequence):
        d = self.obj_ir_sequence._interpolation_dict()
        prefix = self.obj_ir_sequence._interpolate(
            sequence.prefix, d)
        suffix = self.obj_ir_sequence._interpolate(
            sequence.suffix, d)
        code = (prefix + ('%%0%sd' % sequence.padding %
                          sequence.number_next_actual) + suffix)
        return code

    def create_sequence(self):
        val_type = {
            'name': 'Secondary Ref Sequence',
            'code': 'stock.picking.second.ref',
        }
        self.obj_ir_sequence_type.create(val_type)

        val = {
            'name': 'Secondary Ref Sequence',
            'code': 'stock.picking.second.ref',
            'prefix': 'SRS',
            'padding': 5
        }
        sequence_id = self.obj_ir_sequence.create(val)

        return sequence_id

    def _prepare_picking_data(self, picking_type_id):
        partnerA = self.obj_res_partner.create({'name': 'Partner A'})

        data_picking = {
            'partner_id': partnerA.id,
            'picking_type_id': picking_type_id
        }

        return data_picking

    def _create_picking(self, picking_type_id):
        data = self._prepare_picking_data(picking_type_id)
        picking = self.obj_picking.create(data)

        return picking
