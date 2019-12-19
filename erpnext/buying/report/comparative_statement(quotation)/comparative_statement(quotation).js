// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Comparative Statement(Quotation)"] = {
	"filters": [
		{
			fieldname: "rfq",
			label: __("RFQ"),
			fieldtype: "Link",
			options: "Request for Quotation",
			reqd: 1,
			"get_query": function() {
                                return {"doctype": "Request for Quotation", "filters": {"docstatus": 1}}
                                }
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.defaults.get_user_default("year_start_date")
		},
		{
                        fieldname: "to_date",
                        label: __("To Date"),
                        fieldtype: "Date",
                        default: frappe.defaults.get_user_default("year_end_date")
                },
		{
			fieldname: "supplier",
			label: __("Supplier"),
			fieldtype: "Link",
			options: "Supplier"
		},

	]
}
