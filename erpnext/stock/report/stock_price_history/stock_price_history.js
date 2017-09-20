// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Price History"] = {
	"filters": [
		{
			"fieldname":"uinput",
			"label":("Type"),
			"fieldtype": "Select",
			"width": "120",
			"options": [" ", "COP", "Sales"]
			
	},
	
	]
}
