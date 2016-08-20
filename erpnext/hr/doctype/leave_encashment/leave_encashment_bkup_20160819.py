# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, \
	comma_or, get_fullname
from frappe import msgprint, _

class LeaveEncashment(Document):
        pass

def get_employee_cost_center(division):
        msgprint(division)
        cost_center = frappe.db.get_value("Division", division, "cost_center")
        return cost_center
                        
