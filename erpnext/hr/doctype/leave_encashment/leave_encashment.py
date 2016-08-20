# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, \
	comma_or, get_fullname
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from erpnext.custom_autoname import get_auto_name
from datetime import *
from dateutil.relativedelta import *


class LeaveEncashment(Document):
        def autoname(self):
                today = datetime.today()
                #self.name = make_autoname(get_auto_name(self) + "/.#####")
                monthyear = str(today.year)
                if len(str(today.month)) < 2:
                        monthyear += "0"+str(today.month)

                self.name = make_autoname(self.employee+"/LE/"+monthyear+"/.#####")
        
        def validate(self):
                self.my_validates()
                msgprint(_("validate is triggered...!!!"))
                #msgprint(self.balance_after)

        def on_submit(self):
                msgprint(_("On-Submit is triggered...!!!"))

        def my_validates(self):
                msgprint(self.employee)

@frappe.whitelist()
def get_employee_cost_center(division):
        #cost_center = frappe.db.get_value("Division", division, "cost_center")
        division = frappe.get_doc("Division", division)
        return division.cost_center
                        
