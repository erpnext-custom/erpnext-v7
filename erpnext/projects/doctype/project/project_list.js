frappe.listview_settings['Project'] = {
	add_fields: ["priority", "is_active", "tot_wq_percent_complete", "tot_wq_percent", "expected_end_date"],
	filters:[["status","=", "Ongoing"]],
	colwidths: {"name":2, "status":2, "expected_start_date":2},
	get_indicator: function(doc) {
		if(parseFloat(doc.tot_wq_percent_complete) < parseFloat(doc.tot_wq_percent)){
			return [__("{0}% Complete", [Math.round(doc.tot_wq_percent_complete)]), "orange", "tot_wq_percent_complete,>=,0|status,=,Ongoing"];
		} else if(parseFloat(doc.tot_wq_percent_complete) >= parseFloat(doc.tot_wq_percent)){
			return [__("{0}% Complete", [Math.round(doc.tot_wq_percent_complete)]), "green", "tot_wq_percent_complete,>=,0|status,=,Ongoing"];
		} else {
			return [__(doc.status), frappe.utils.guess_colour(doc.status), "status,=," + doc.status];
		}
	},
};
