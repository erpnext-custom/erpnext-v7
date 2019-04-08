// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Hall Booking Report"] = {
	"filters": [
		{
                        "fieldname": "hall_type",
                        "label":("Hall Type"),
                        "fieldtype" : "Select",
                        "width" :"80",
                        "options": ["Large Hall","Medium Hall","Small/Board Room","Open space"],
                },
		{
                        "fieldname": "customer",
                        "label": ("Customer"),
                        "fieldtype": "Link",
                        "options": "Customer",
                },
		{
                        "fieldname":"from_date",
                        "label": ("From Date"),
                        "fieldtype": "Date",
                        "width": "80",
			"default": frappe.datetime.year_start()
                },
                {
                        "fieldname":"to_date",
                        "label": ("To Date"),
                        "fieldtype": "Date",
                        "width": "80",
                	"default": frappe.datetime.year_end()
		}
	]
}
