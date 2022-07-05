// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Indent"] = {
	"filters": [
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
                        "options": "January\nFebruary\nMarch\nApril\nMay\nJune\nJuly\nAugust\nSeptember\nOctober\nNovember\nDecember",
                        "default": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
                                "December"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
                },

	]
}
