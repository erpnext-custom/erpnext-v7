# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import nowdate

class PMSEvaluation(Document):
    def validate(self):
        self.validate_dates()
        self.validate_fields()
        self.validate_final_score()
        self.calculate_final_score()
        
    def validate_dates(self):
        if self.evaluation_start_date > self.evaluation_end_date:
            frappe.throw(_("<b>The evaluation start date should not be after the evaluation end date</b>"))
        if self.evaluation_start_date < nowdate():
            frappe.throw(_("<b>The evaluation start date should not be before today's date"))
       
    def validate_fields(self):
        for i, t in enumerate(self.items):
            if not t.status:
                frappe.throw(_("<b>Status cannot be blank in TARGET SET UP at Row {}</b>".format(i+1)))
            if t.final_score == 0:
                frappe.throw(_("<b>Final Score cannot be 0 in TARGET SET UP at Row {}</b>".format(i+1)))
    
    def validate_final_score(self):
        for i, t in enumerate(self.items):
            if t.final_score > t.weightage:
                frappe.throw(_("<b>Final Score can not be greater than weightage in TARGET SET UP at Row {}</b>".format(i+1)))
                
    def calculate_final_score(self):
        total_final_score = 0
        for i, t in enumerate(self.items):
            total_final_score += t.final_score 
        self.final_score = total_final_score