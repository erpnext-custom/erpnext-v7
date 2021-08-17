frappe.listview_settings['Attendance'] = {
	add_fields: ["status", "att_date", "attendance_time"],
	get_indicator: function(doc) {
		return [__(doc.status), doc.status=="Present" ? "green" : "darkgrey", "status,=," + doc.status];
	}
};
