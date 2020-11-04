frappe.listview_settings['Leave Application'] = {
	add_fields: ["status", "leave_type", "cost_center", "employee_name",  "employee","from_date"],
	filters:[["status","!=", "Rejected"]],
	get_indicator: function(doc) {
		return [__(doc.status), frappe.utils.guess_colour(doc.status),
			"status,=," + doc.status];
	}
};
