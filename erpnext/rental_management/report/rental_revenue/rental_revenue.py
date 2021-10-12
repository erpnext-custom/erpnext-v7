# For license information, please see license.txt
# Frappe Technologiss Pvt. Ltd. and contributors

# Created by Phuntsho on June 03 2021

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
			"fieldname": "year",
			"label": _("Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year"
		},
        {
			"fieldname": "month",
			"label": _("Month"),
			"fieldtype": "Data",
		},
        {
			"fieldname": "opening_balance",
			"label": _("Opening Balance"),
			"fieldtype": "Currency",
		},
        {
			"fieldname": "bill_amount",
			"label": _("Bill Amount"),
			"fieldtype": "Currency",
		},
        {
			"fieldname": "amount_received",
			"label": _("Amount Received"),
			"fieldtype": "Currency",
		},
        {
			"fieldname": "discount_amount",
			"label": _("Discount Amount"),
			"fieldtype": "Currency",
		},
        {
			"fieldname": "balance",
			"label": _("Balance"),
			"fieldtype": "Currency",
		},
        {
			"fieldname": "penalty",
			"label": _("Penalty"),
			"fieldtype": "Currency",
		},
        {
			"fieldname": "dzongkhag",
			"label": _("Dzongkhag"),
			"fieldtype": "Link",
			"options": "Dzongkhags"
		},
        {
			"fieldname": "building_category",
			"label": _("Building Category"),
			"fieldtype": "Data",
		},
        {
			"fieldname": "closing_balance",
			"label": _("Closing Balance"),
			"fieldtype": "Currency",
		},
    ]
    # return [
    # ("Year") + ":Data:80",
    # ("Month") + " :Data:80",
    # ("Opening Balance") + ":Currency:120",
    # ("Bill Amount") + ":Currency:120",
    # ("Amount Received") + ":Currency:120",
    # ("Discount Amount") + ":Currency:120",
    # ("Balance") + ":Currency:120",
    # ("Penalty")+ ":Currency:120",
    # ("Dzongkhag") +":Data:100",
    # ("Building Category") +":Data:100",
    # ("Closing Balance") + ":Currency:120"
    
    # ]
    # {u'closing_balance': -604.0, 
    # u'amount_received': 3153938.0, 
    # u'month': u'01', 
    # u'penalty': 0.0, 
    # u'amount': 3436725.0, 
    # u'dzongkhag': u'Thimphu', 
    # u'year': u'2021', 
    # u'balance': -604.0, 
    # u'opening_balance': 0, 
    # u'discount_amount': 283391.0}

def get_data(filters):
    status = ""
    if filters.get("status") == "Draft":
        status = "rpi_parent.docstatus = 0"
    if filters.get("status") == "Submitted":
        status = "rpi_parent.docstatus = 1"

    query = """
        SELECT
            rpi_parent.fiscal_year as year,
            rpi_parent.month as month,
            "",
            sum(rpi.amount) as bill_amount,
            sum(rpi.amount_received) as amount_received,
            sum(rpi.discount_amount) as discount_amount,
            (sum(rpi.amount)-(sum(rpi.amount_received)+sum(rpi.discount_amount))) as balance,
			sum(rpi.penalty) as penalty,
            rpi_parent.dzongkhag as dzongkhag,
            rpi_parent.building_category as building_category,
            ""
        FROM
            `tabRental Payment` as rpi_parent
		LEFT JOIN 
			 `tabRental Payment Item` as rpi
        ON 
            rpi_parent.name = rpi.parent
        WHERE
            rpi.docstatus = 1 and 
            {status}
            """.format(
                status = status
            )
    if filters.get("dzongkhag"):
        query += " and rpi_parent.dzongkhag = \'" + str(filters.dzongkhag) + "\'"
    if filters.get("building_category"):
        query += " and rpi_parent.building_category = \'" + str(filters.building_category) + "\' "

    if filters.get("fiscal_year"):
        query += " and rpi_parent.fiscal_year ={0}".format(filters.get("fiscal_year"))

    if filters.get("from_month") == filters.get("to_month"): 
        query += " and rpi_parent.month = '{0}'".format(filters.get("from_month"))

    if filters.get("from_month") != filters.get("to_month"): 
        query += " and rpi_parent.month between '{0}' and '{1}'".format(filters.get("from_month"),filters.get("to_month"))

    query += "GROUP BY rpi_parent.building_category DESC, rpi_parent.dzongkhag DESC,rpi_parent.month ASC"
    info = frappe.db.sql(query,as_dict =1)
    previous_year_closing_amount = get_previous_year_closing(filters)


    # # calculate the opening and closing for each month below
    data = []
    temp_opening_balance = opening_balance = closing_balance = 0 
    for item in info:
        if  item.month == "01": 
            opening_balance = 0
            closing_balance = opening_balance + item.bill_amount - item.amount_received - item.discount_amount
            temp_opening_balance = closing_balance
        else:  
            opening_balance = temp_opening_balance
            closing_balance = opening_balance + item.bill_amount - item.amount_received - item.discount_amount
            temp_opening_balance = closing_balance

        temp_obj = [ 
            item.year, 
            item.month, 
            opening_balance, 
            item.bill_amount, 
            item.amount_received,  
            item.discount_amount,
            item.balance,
            item.penalty,
            item.dzongkhag, 
            item.building_category, 
            closing_balance 
        ]

        data.append(temp_obj)
    frappe.msgprint(str(data))
    return (data)


	
def get_previous_year_closing(filters): 
    year = int(filters.get("fiscal_year")) - 1
    if year == 2020: 
        return 0

