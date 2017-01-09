# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .base import Base


class TestActionDone(Base):

    def test_action_done(self):
        # CONDITION
        # second_sequence_id == True
        obj_wizard = self.env[
            "stock.transfer_details"]
        self.picking_type_1.second_sequence_id =\
            self.sequence.id

        # Get Next Code
        sequence_id = self.picking_type_1.second_sequence_id
        code = self._get_next_code(sequence_id)

        # Create Picking
        picking_1 = self._create_picking(self.picking_type_1)
        picking_1.action_confirm()
        picking_1.action_assign()
        if picking_1.state == "confirmed":
            picking_1.force_assign()
        wizard_view = picking_1.do_enter_transfer_details()
        wizard = obj_wizard.browse([wizard_view["res_id"]])
        wizard.do_detailed_transfer()

        self.assertEqual(picking_1.secondary_ref, code)

        # CONDITION
        # second_sequence_id == False
        # Create Picking
        picking_2 = self._create_picking(self.picking_type_2)
        picking_2.action_confirm()
        picking_2.action_assign()
        if picking_2.state == "confirmed":
            picking_2.force_assign()
        wizard_view = picking_2.do_enter_transfer_details()
        wizard = obj_wizard.browse([wizard_view["res_id"]])
        wizard.do_detailed_transfer()

        self.assertEqual(picking_2.secondary_ref, False)
