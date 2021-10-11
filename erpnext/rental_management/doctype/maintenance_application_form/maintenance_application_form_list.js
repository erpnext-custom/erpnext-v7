frappe.listview_settings['Maintenance Application Form'] = {
        add_fields: ["name", "owner", "docstatus", "posting_date", "workflow_state"],
        get_indicator: function(doc) {
		if (doc.status ==1 && doc.workflow_state =="Approved"){
               		return [__("Approved"), "green"];
			if(doc.technical_sanction) {
                		return [__("TS Created"), "orange"];
                }
        }}
};

