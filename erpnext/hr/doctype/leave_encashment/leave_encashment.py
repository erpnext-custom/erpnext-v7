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
#from dateutil.relativedelta import *

class OverlapError(frappe.ValidationError): pass

class LeaveEncashment(Document):
        def autoname(self):
                today = datetime.today()
                #self.name = make_autoname(get_auto_name(self) + "/.#####")
                monthyear = str(today.year)
                if len(str(today.month)) < 2:
                        monthyear += "0"+str(today.month)

                self.name = make_autoname(self.employee+"/LE/"+monthyear+"/.#####")
        
        def validate(self):
                self.validate_leave_application()
                msgprint(_("validate is triggered...!!!"))

        def on_submit(self):
                msgprint(_("On-Submit is triggered...!!!"))

        def get_leave_credits(self):
                pass

        def validate_leave_application(self):
                from_date, to_date = self.get_current_year_dates()
                ref_docs = ''
                
                encashed_list = frappe.db.sql("""
                        select name from `tabLeave Encashment`
                        where employee = %s and leave_type = %s and docstatus = 1
                        and application_date between %s and %s
                        """,(self.employee, self.leave_type, from_date, to_date), as_dict=1)

                for row in encashed_list:
                        ref_docs += '<br /><a href="#Form/Leave Encashment/{0}">{0}</a>'.format(row.name)
               
                if ref_docs:
                        ref_docs = "<br />Reference: {0}".format(ref_docs)
                        frappe.throw(_("Employee has already encashed for the current year."), OverlapError)

        def get_current_year_dates(self):
                from_date = date(date.today().year,1,1).strftime('%Y-%m-%d')
                to_date = date(date.today().year,12,31).strftime('%Y-%m-%d')
                return from_date, to_date
                
@frappe.whitelist()
def get_employee_cost_center(division):
        #cost_center = frappe.db.get_value("Division", division, "cost_center")
        division = frappe.get_doc("Division", division)
        return division.cost_center
                        
