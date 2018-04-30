
frappe.query_reports["Material Request Pending for Purchase Order"] = {
	"filters": [
		{
			"fieldname":"filter_by",
			"label": __("Filter By"),
			"fieldtype": "Select",
			"options": "Material Request\nItem",
			"default": "Material Request"
		}
	]
}
