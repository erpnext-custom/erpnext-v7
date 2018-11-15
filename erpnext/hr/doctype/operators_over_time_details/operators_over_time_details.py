# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate
from frappe.model.document import Document

class OperatorsOverTimeDetails(Document):
        def validate(self):
                for d in self.get('ehf_details'):
                        result = frappe.db.sql("SELECT o.start_date as start_date, o.end_date as end_date FROM `tabEquipment` e \
                                INNER JOIN `tabEquipment Operator` o on e.name= o.parent \
                                WHERE o.operator = \'"+str(self.operator)+"\' and e.name = \'" + str(d.equipment)+ "\'", as_dict=True)
                        if len(result):                                                        
                                for a in result:
                                        if a.end_date and getdate(a.end_date) < getdate(d.hiring_date):
                                                frappe.throw("\'"+str(self.operator_name)+" \' was operator to equipment \'" + str(d.equipment_no)+ "\' untill \'" + str(a.end_date)+ "\'. Please cross check!")
                        else:
                                frappe.throw("\'"+str(self.operator_name)+" \' is not assigned as an operator to Equipment \'" + str(d.equipment_no)+ "\'")                
                                                                             

@frappe.whitelist()
def getoperatordtl(employee_type, operator):
        if employee_type == "Employee":
                query = "select employee_name as operator_name from  `tabEmployee` where name = \'" + str(operator) + "\'"
        else:
                query = "select person_name as operator_name from `tabMuster Roll Employee` where name = \'" + str(operator) + "\'"

        for a in frappe.db.sql(query, as_dict=True):
                #data.append(a.operator_name)
                return a.operator_name
                        
        
