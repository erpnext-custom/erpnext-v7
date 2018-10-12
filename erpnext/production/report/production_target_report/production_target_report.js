// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Production Target Report"] = {
	"filters": [
		{
                        "fieldname": "cost_center",
                        "label": ("Cost Center"),
                        "fieldtype": "Link",
                        "options": "Cost Center"
                 },
		 {
                        "fieldname": "location",
                        "label": ("Location"),
                        "fieldtype": "Link",
                        "options": "Location",
                       
                },
		{
                        "fieldname": "item_sub_group",
                        "label": ("Material Sub Group"),
                        "fieldtype": "Link",
                        "options": "Item Sub Group",
                 
                },
	]
}
