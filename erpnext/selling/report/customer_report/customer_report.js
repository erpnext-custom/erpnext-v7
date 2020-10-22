// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
frappe.query_reports["Customer Report"] = {
	"filters": [
		{
                        "fieldname": "dzongkhag",
                        "label": ("Dzongkhag"),
                        "fieldtype": "Link",
                        "width": "80",
                        "options": "Dzongkhags",
                },
                {
                        "fieldname": "customer",
                        "label": ("Customer"),
                        "fieldtype": "Link",
                        "width": "80",
                        "options": "Customer",
                },
                {
                        "fieldname": "customer_group",
                        "label": ("Customer Group"),
                        "fieldtype": "Link",
                        "width": "80",
                        "options": "Customer Group",
                },
                {
                        "fieldname": "construction_type",
                        "label": ("Construction Type"),
                        "fieldtype": "Link",
                        "width": "80",
                        "options": "Construction Type",
                },
                {
                        "fieldname": "branch",
                        "label": ("Branch"),
                        "fieldtype": "Link",
                        "width": "80",
                        "options": "Branch",
                },
                {
                        "fieldname": "territory",
                        "label": ("Region"),
                        "fieldtype": "Link",
                        "width": "80",
                        "options": "Territory",
                },
                {
                        "fieldname": "item_group",
                        "label": ("Material Group"),
                        "fieldtype": "Link",
                        "options": "Item Group",
                        "get_query": function() {
                                return {"doctype": "Item Group", "filters": {"is_group": 0, "is_production_group": 1}}
                        },
                },
                {
                        "fieldname": "item_sub_group",
                        "label": ("Material Sub Group"),
                        "fieldtype": "Link",
                        "options": "Item Sub Group",
                        "get_query": function() {
                                var item_group = frappe.query_report.filters_by_name.item_group.get_value();
                                return {"doctype": "Item Sub Group", "filters": {"item_group": item_group}}
                        }
                },
                {
                        "fieldname": "item",
                        "label": ("Material"),
                        "fieldtype": "Link",
                        "options": "Item",
                        "get_query": function() {
                                var sub_group = frappe.query_report.filters_by_name.item_sub_group.get_value();
                                return {"doctype": "Item", "filters": {"item_sub_group": sub_group, "is_production_item": 1}}
                        }
                },
                {
			"fieldname": "warehouse",
			"label": __("Warehouse"),
			"fieldtype": "Link",
			"width": "80",
                        "options":"Warehouse"
                },
                {
                        "fieldname":"from_date",
                        "label": ("From Date"),
                        "fieldtype": "Date",
                        "width": "80",
                        "default": sys_defaults.year_start_date,
                },
                {
                        "fieldname":"to_date",
                        "label": ("To Date"),
                        "fieldtype": "Date",
                        "width": "80",
                        "default": frappe.datetime.get_today()
                },
                {
                        "fieldname":"aggregate",
                        "label": ("Show Aggregate"),
                        "fieldtype": "Check",
                        "default": 0
                }
	]
}
