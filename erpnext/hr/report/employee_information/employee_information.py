# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
# --------------------------------------------------------------------
# CREATED BY BIREN AND MOVED TO PRODUCTION ON DECEMBER 14. 
# --------------------------------------------------------------------

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_data(filters):

	conditions = get_conditions(filters)

	data = frappe.db.sql("""
		SELECT 
			employee_name,
			gender,
			company,
			status,
			date_of_joining,
			employment_type,
			employee_group,
			employee_subgroup,
			branch,
			department,
			division,
			bank_name,
			bank_ac_no
		FROM 
			`tabEmployee` 
			{}
		""".format(conditions))
	return data

def get_conditions(filters):

	conditions = ""

	if filters.get("company"): conditions += "WHERE company = '{}'".format(filters.get("company"))

	if filters.get("employment_type"):
		if conditions: conditions += "AND "
		else: conditions += "WHERE "
		conditions += "employment_type = '{}'".format(filters.get("employment_type"))
		

	if filters.get("status") and filters.get("status") != "All":
		if conditions :	conditions += "AND "
		else: conditions += "WHERE "
		conditions += "status = '{}'".format(filters.get("status"))

	return conditions


def get_columns(filters):

	columns = [
		{
            "fieldname":"empolyee_name",
            "label":"Full Name",
            "fieldtype":"Data",
            "width":200
	    },
		{
            "fieldname":"gender",
            "label":"Gender",
            "fieldtype":"Data",
            "width":50
	    },
		{
            "fieldname":"company",
            "label":"Company",
            "fieldtype":"Data",
            "width":250
	    },
		{
            "fieldname":"status",
            "label":"Status",
            "fieldtype":"Data",
            "width":50
	    },
		{
            "fieldname":"date_of_joining",
            "label":"Date Of Joining",
            "fieldtype":"Data",
            "width":150
	    },
		{
            "fieldname":"employment_type",
            "label":"Employment Type",
            "fieldtype":"Data",
            "width":150
	    },
		{
            "fieldname":"employee_group",
            "label":"Employee Group",
            "fieldtype":"Data",
            "width":150
	    },
		{
            "fieldname":"employee_subgroup",
            "label":"Grade",
            "fieldtype":"Data",
            "width":50
	    },
		{
            "fieldname":"branch",
            "label":"Branch",
            "fieldtype":"Data",
            "width":150
	    },
		{
            "fieldname":"department",
            "label":"Department",
            "fieldtype":"Data",
            "width":200
	    },
		{
            "fieldname":"division",
            "label":"Division",
            "fieldtype":"Data",
            "width":150
	    },
		{
            "fieldname":"bank_name",
            "label":"Bank Name",
            "fieldtype":"Data",
            "width":100
	    },
		{
            "fieldname":"bank_ac_no",
            "label":"Bank Account Number",
            "fieldtype":"Data",
            "width":150
	    }
	]
	return columns