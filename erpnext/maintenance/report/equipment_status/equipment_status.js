// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Equipment Status"] = {
	"filters": [
		{
			"fieldname":"branch",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options": "Branch",
			"reqd": 1
		},
		{
			"fieldname":"year",
			"label": __("Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"reqd": 1
		},
		{
			"fieldname":"month",
			"label": __("Month"),
			"fieldtype": "Select",
			"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
			"default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
				"Dec"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
		},
		{
			"fieldname":"equipment_type",
			"label": __("Equipment Type"),
			"fieldtype": "Link",
			"options": "Equipment Type",
		},
		{
                        "fieldname": "not_cdcl",
                        "label": ("Include Only CDCL Equipments"),
                        "fieldtype": "Check",
                        "default": 1
                },
		{
                        "fieldname": "include_disabled",
                        "label": ("Include Disbaled Equipments"),
                        "fieldtype": "Check",
                        "default": 0
                }


	]
}
