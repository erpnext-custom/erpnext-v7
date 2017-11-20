# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
        columns = get_columns()
        data = get_data(filters)

        return columns, data

def get_columns():
        return [
                ("Project name ") + ":Link/project:120",
		("Branch")+ ":Data:120",
		("Cost Center ") + ":Data: 140",
                ("Equipment No.") + ":Data:100",
                ("Equipment")+ ":Data:100",
                ("From Date")+ ":Date:80",
                ("To Date")+ ":Date:80"
        ]

def get_data(filters):

        query =  """
			select 
				p.project_name, 
				p.branch,
				p.cost_center,
				hd.equipment_number, 
				hd.equipment,
				hd.from_date, 
				hd.to_date
			from 
				`tabProject` as p, 
				`tabEquipment Hiring Form` as h, 			
				`tabHiring Approval Details` hd
			where h.name= hd.parent
			and   p.branch = h.branch """

        if filters.get("branch"):

                query += " and p.branch = \'" + str(filters.branch) + "\'"

        if filters.get("from_date") and filters.get("to_date"):

                query += " and hd.from_date between \'" + str(filters.from_date) + "\' and \'"+ str(filters.to_date) +  "\'"

        query += " order by p.project_name"

        return frappe.db.sql(query)

