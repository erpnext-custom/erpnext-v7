frappe.listview_settings['Project'] = {
	add_fields: ["priority", "status", "physical_progress_weightage", "physical_progress", "percent_completed", "expected_end_date", "status"],
	filters:[["status","=", "Ongoing"]],
	get_indicator: function(doc) {
			return [__(doc.status), frappe.utils.guess_colour(doc.status), "status,=," + doc.status];
		}
	}
