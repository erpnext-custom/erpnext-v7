# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import flt, time_diff_in_hours, get_datetime, getdate, cint, get_datetime_str, date_diff, today
# Autonaming is changed, SHIV on 23/10/2017
from frappe.model.naming import make_autoname

class TimesheetDetail(Document):
        def autoname(self):
                cur_year  = str(today())[0:4]
                cur_month = str(today())[5:7]
                if self.project:
                        serialno  = make_autoname("TSI" + self.project[-4:] + ".####")
                        #self.name = serialno[0:3] + cur_year + cur_month + serialno[3:]
                else:
                        serialno  = make_autoname("TSI.YY.MM.####")

                self.name = serialno
