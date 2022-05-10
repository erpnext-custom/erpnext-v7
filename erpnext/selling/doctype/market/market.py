# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe import _
from frappe.utils.nestedset import NestedSet

class Market(NestedSet):
        nsm_parent_field = 'parent_market'

        def on_update(self):
                super(Market, self).on_update()
                self.validate_one_root()
