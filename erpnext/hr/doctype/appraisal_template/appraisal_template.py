# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint
from frappe import _

from frappe.model.document import Document

class AppraisalTemplate(Document):
	def validate(self):
		self.check_total_points()
		
	def check_total_points(self):	
		total_points = 0
		for d in self.get("goals"):
			total_points += int(d.per_weightage or 0)

		if cint(total_points) not in (50, 70, 30):
			frappe.throw(_("Sum of points for all goals should be 50(if it's Evalution of competencies  for Group B) and (if it's Group A than it's 30 and 70 ) . It is {0}").format(total_points))