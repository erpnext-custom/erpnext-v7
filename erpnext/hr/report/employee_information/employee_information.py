# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
# --------------------------------------------------------------------
# CREATED BY BIREN AND MOVED TO PRODUCTION ON DECEMBER 14. 
# --------------------------------------------------------------------

from __future__ import unicode_literals
import frappe

def execute(filters=None):
    if filters.accumulate_data == "Accumulated Data":
        columns, data = get_all_column(filters), get_all_data(filters)
    else:
        columns, data = get_columns(filters), get_data(filters)
    return columns, data

def get_all_column(filters):
    columns = [
        "Type and Accumulated data" + "::600"
    ]
    return columns

def get_all_data(filters):
    data = []
    data0 = frappe.db.sql("select '<b>GENDER</b>' FROM `tabEmployee`")
    data1 = frappe.db.sql("select 'Male', count(gender) from `tabEmployee` where status='Active' and gender='Male' group by gender")
    data2 = frappe.db.sql("select 'Female', count(gender) from `tabEmployee` where status='Active' and gender='Female' group by gender")
    data32 = frappe.db.sql("select '<b>STATUS</b>' FROM `tabEmployee`")
    data3 = frappe.db.sql("select 'Active', count(status) from `tabEmployee` where status='Active'")
    data4 = frappe.db.sql("select 'Left', count(status) from `tabEmployee` where status='Left'")
    data33 = frappe.db.sql("select '<b>EMPLOYMENT TYPE</b>' FROM `tabEmployee`")
    data5 = frappe.db.sql("select 'Contract', count(employment_type) from `tabEmployee` where employment_type='Contract' and status='Active'")
    data6 = frappe.db.sql("select 'Deputation', count(employment_type) from `tabEmployee` where employment_type='Deputation' and status='Active'")
    data7 = frappe.db.sql("select 'Regular', count(employment_type) from `tabEmployee` where employment_type='Regular' and status='Active'")
    data34 = frappe.db.sql("select '<b>EMPLOYEE GROUP</b>' FROM `tabEmployee`")
    data8 = frappe.db.sql("select 'Chief Executive Officer', count(employee_group) from `tabEmployee` where employee_group='Chief Executive Officer' and status='Active'")
    data9 = frappe.db.sql("select 'Executive', count(employee_group) from `tabEmployee` where employee_group='Executive' and status='Active'")
    data10 = frappe.db.sql("select 'GSC', count(employee_group) from `tabEmployee` where employee_group='GSC' and status='Active'")
    data11 = frappe.db.sql("select 'Managerial', count(employee_group) from `tabEmployee` where employee_group='Managerial' and status='Active'")
    data12 = frappe.db.sql("select 'Operational', count(employee_group) from `tabEmployee` where employee_group='Operational' and status='Active'")
    data13 = frappe.db.sql("select 'Supervisory', count(employee_group) from `tabEmployee` where employee_group='Supervisory' and status='Active'")
    data35 = frappe.db.sql("select '<b>EMPLOYEE GRADE</b>' FROM `tabEmployee`")
    data14 = frappe.db.sql("select 'CEO', count(employee_subgroup) from `tabEmployee` where employee_subgroup='CEO' and status='Active'")
    data15 = frappe.db.sql("select 'E2', count(employee_subgroup) from `tabEmployee` where employee_subgroup='E2' and status='Active'")
    data16 = frappe.db.sql("select 'E3', count(employee_subgroup) from `tabEmployee` where employee_subgroup='E3' and status='Active'")
    data17 = frappe.db.sql("select 'GSC II', count(employee_subgroup) from `tabEmployee` where employee_subgroup='GSC II' and status='Active'")
    data18 = frappe.db.sql("select 'M1', count(employee_subgroup) from `tabEmployee` where employee_subgroup='M1' and status='Active'")
    data19 = frappe.db.sql("select 'M2', count(employee_subgroup) from `tabEmployee` where employee_subgroup='M2' and status='Active'")
    data20 = frappe.db.sql("select 'M3', count(employee_subgroup) from `tabEmployee` where employee_subgroup='M3' and status='Active'")
    data21 = frappe.db.sql("select 'M4', count(employee_subgroup) from `tabEmployee` where employee_subgroup='M4' and status='Active'")
    data22 = frappe.db.sql("select 'O1', count(employee_subgroup) from `tabEmployee` where employee_subgroup='O1' and status='Active'")
    data23 = frappe.db.sql("select 'O2', count(employee_subgroup) from `tabEmployee` where employee_subgroup='O2' and status='Active'")
    data24 = frappe.db.sql("select 'O3', count(employee_subgroup) from `tabEmployee` where employee_subgroup='O3' and status='Active'")
    data25 = frappe.db.sql("select 'O4', count(employee_subgroup) from `tabEmployee` where employee_subgroup='O4' and status='Active'")
    data26 = frappe.db.sql("select 'O5', count(employee_subgroup) from `tabEmployee` where employee_subgroup='O5' and status='Active'")
    data27 = frappe.db.sql("select 'O6', count(employee_subgroup) from `tabEmployee` where employee_subgroup='O6' and status='Active'")
    data28 = frappe.db.sql("select 'O7', count(employee_subgroup) from `tabEmployee` where employee_subgroup='O7' and status='Active'")
    data29 = frappe.db.sql("select 'S1', count(employee_subgroup) from `tabEmployee` where employee_subgroup='S1' and status='Active'")
    data30 = frappe.db.sql("select 'S2', count(employee_subgroup) from `tabEmployee` where employee_subgroup='S2' and status='Active'")
    data31 = frappe.db.sql("select 'S3', count(employee_subgroup) from `tabEmployee` where employee_subgroup='S3' and status='Active'")
    data.append(data0)
    data.append(data1)
    data.append(data2)
    data.append(data32)
    data.append(data3)
    data.append(data4)
    data.append(data33)
    data.append(data5)
    data.append(data6)
    data.append(data7)
    data.append(data34)
    data.append(data8)
    data.append(data9)
    data.append(data10)
    data.append(data11)
    data.append(data12)
    data.append(data13)
    data.append(data35)
    data.append(data14)
    data.append(data15)
    data.append(data16)
    data.append(data17)
    data.append(data18)
    data.append(data19)
    data.append(data20)
    data.append(data21)
    data.append(data22)
    data.append(data23)
    data.append(data24)
    data.append(data25)
    data.append(data26)
    data.append(data27)
    data.append(data28)
    data.append(data29)
    data.append(data30)
    data.append(data31)
    return data

def get_data(filters):

    conditions = get_conditions(filters)
    data = frappe.db.sql("""
        SELECT 
            e.name,
            e.employee_name,
            e.gender,
            e.company,
            e.status,
            e.date_of_joining,
            e.employment_type,
            e.employee_group,
            e.employee_subgroup,
            e.branch,
            e.department,
            e.division,
            e.bank_name,
            e.bank_ac_no,
            e.increment_and_promotion_cycle,
            e.cost_center,
            ee.qualification,
            ee.trade,
            ee.level
            
        FROM 
            `tabEmployee` e, `tabEmployee Education` ee where e.name=ee.parent
            {}
        """.format(conditions))
    return data

def get_conditions(filters):
    conditions = ""
    if filters.company:
         conditions += "and e.company='{}'".format(filters.company)
    # if filters.employment_type:
    #     conditions += "and e.employment_type='{}'".format(filters.employment_type)
    # if filters.status:
    #     conditions += "and e.status='{}'".format(filters.status)
    # if filters.get("company"): 
    #     conditions += "WHERE e.company = '{}'".format(filters.get("company"))

    if filters.get("employment_type"):
        if conditions: 
            conditions += "AND "
        else: conditions += "WHERE "
        conditions += "e.employment_type = '{}'".format(filters.get("employment_type"))
        
    if filters.get("status") and filters.get("status") != "All":
        if conditions :	
            conditions += "AND "
        else: 
            conditions += "WHERE "
        conditions += "e.status = '{}'".format(filters.get("status"))

    return conditions


def get_columns(filters):

    columns = [
            ("Employee ID") + ":Link/Employee:120",
            ("Employee Name") + ":Data:200",
            ("Gender") + ":Data:50",
            ("Comapany") + ":Data:250",
            ("Status") + ":Data:50",
            ("Date of Joining") + ":Data:150",
            ("Employment Type") + ":Data:150",
            ("Employee Group") + ":Data:200",
            ("Employee Sub Group") + ":Data:200",
            ("Branch") + ":Data:250",
            ("Department") + ":Data:250",
            ("Division") + ":Data:250",
            ("Bank Name") + ":Data:150",
            ("bank Acc No") + ":Data:120",
            ("Increment Cycle") + ":Data:110",
            ("Cost Center") + ":Data:200",
            ("Qualification") + ":Data:120",
            ("Trade") + ":Data:120",
            ("Level") + ":Data:120"
        #  {
        #     "fieldname":"name",
        #     "label":"Employee ID",
        #     "fieldtype":"Data",
        #     "width":200
        # },
        # {
        #     "fieldname":"empolyee_name",
        #     "label":"Full Name",
        #     "fieldtype":"Data",
        #     "width":200
        # },
        # {
        #     "fieldname":"gender",
        #     "label":"Gender",
        #     "fieldtype":"Data",
        #     "width":50
        # },
        # {
        #     "fieldname":"company",
        #     "label":"Company",
        #     "fieldtype":"Data",
        #     "width":250
        # },
        # {
        #     "fieldname":"status",
        #     "label":"Status",
        #     "fieldtype":"Data",
        #     "width":50
        # },
        # {
        #     "fieldname":"date_of_joining",
        #     "label":"Date Of Joining",
        #     "fieldtype":"Data",
        #     "width":150
        # },
        # {
        #     "fieldname":"employment_type",
        #     "label":"Employment Type",
        #     "fieldtype":"Data",
        #     "width":150
        # },
        # {
        #     "fieldname":"employee_group",
        #     "label":"Employee Group",
        #     "fieldtype":"Data",
        #     "width":150
        # },
        # {
        #     "fieldname":"employee_subgroup",
        #     "label":"Grade",
        #     "fieldtype":"Data",
        #     "width":50
        # },
        # {
        #     "fieldname":"branch",
        #     "label":"Branch",
        #     "fieldtype":"Data",
        #     "width":150
        # },
        # {
        #     "fieldname":"department",
        #     "label":"Department",
        #     "fieldtype":"Data",
        #     "width":200
        # },
        # {
        #     "fieldname":"division",
        #     "label":"Division",
        #     "fieldtype":"Data",
        #     "width":150
        # },
        # {
        #     "fieldname":"bank_name",
        #     "label":"Bank Name",
        #     "fieldtype":"Data",
        #     "width":100
        # },
        # {
        #     "fieldname":"bank_ac_no",
        #     "label":"Bank Account Number",
        #     "fieldtype":"Data",
        #     "width":150
        # },
        # {
        #     "fieldname": "increment_and_promotion_cycle",
        #     "label": "Increment Cycle",
        #     "fieldtype": "Data",
        #     "width": 150
        # },
        # {
        #     "fieldname": "cost_center",
        #     "label": "Cost Center",
        #     "fieldtype": "Data",
        #     "width": 200
        # },
        # {
        #     "fieldname": "qualification",
        #     "label": "Qualification",
        #     "fieldtype": "Data",
        #     "width": 200
        # },
        # {
        #     "fieldname": "trade",
        #     "label": "Trade",
        #     "fieldtype": "Data",
        #     "width": 200
        # },
        # {
        #     "fieldname": "level",
        #     "label": "Level",
        #     "fieldtype": "Data",
        #     "width": 200
        # }
    ]
    return columns