frappe.listview_settings['Utility Bill'] = {
	add_fields: ["name", "workflow_state", "payment_status", "docstatus"],
	get_indicator: function (doc) {
		if(doc.workflow_state == "Paid") {
			//Display
		}
	},
    onload: function (listview) {

	}
};
