// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Rental Collection"] = {
	"filters": [
		// {
		// 	"fieldname":"from_date",
		// 	"label": ("From Date"),
		// 	"fieldtype": "Date",
		// 	"width": "80",
		// 	"reqd": 1
		// },
		// {
		// 	fieldname:"to_date",
		// 	label: ("To Date"),
		// 	fieldtype: "Date",
		// 	width: "80",
		// 	reqd: 1
		// },
		{
			fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			default: frappe.defaults.get_user_default("fiscal_year"),
			reqd: 1,
		},
		{
			fieldname: "month",
			label: __("Month"),
			fieldtype: "Select",
			options: ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
			default: "01",
		},
		// {
		// 	fieldname: "status",
		// 	label: "Status",
		// 	fieldtype: "Select",
		// 	width: "80",
		// 	options: ["Draft", "Submitted"],
		// 	reqd: 1
		// },
		{
			fieldname:"dzongkhag",
			label: ("Dzongkhag"),
			fieldtype: "Link",
			width: "80",
			options:"Dzongkhags",
			reqd: 1
		},
		{
			fieldname:"location",
			label:("Location"),
			fieldtype:"Link",
			width:"80",
			options:"Locations"
		},
		{
			fieldname:"building_category",
			label:("Building Category"),
			fieldtype:"Link",
			width:"80",
			options:"Building Category"
		},
		{
			fieldtype:"Break"
		},
		{
			fieldname:"ministry_agency",
			label:("Ministry/Agency"),
			fieldtype:"Link",
			width:"80",
			options:"Ministry and Agency"
		},
		
		{
			fieldname:"department",
			label:("Department"),
			fieldtype:"Link",
			width:"80",
			options:"Tenant Department"
		},
		{
			fieldname: "payment_mode",
			label: __("Payment Mode"),
			fieldtype: "Select",
			width: "80",
			options: ["", "Cash", "Cheque", "ePMS", "mBOB", "mPay", "TPay", "NHDCL Office"],
			default: "",
		},
		{
			fieldname:"building_classification",
			label:("Building Classification"),
			fieldtype:"Link",
			width:"100",
			options:"Building Classification"
		}
	]
}
