frappe.listview_settings['Monthly Indent'] = {
	add_fields: ["name",  "indent_for_month", 'status'],
	get_indicator: function(doc) {
		color = {
			'Open': 'red',
			'Completed': 'green',
			'In Progress': 'darkgrey'
		}
		return [__(doc.status), color[doc.status], "status,=," + doc.status];
	}

};
