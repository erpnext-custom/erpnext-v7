frappe.listview_settings['Payment Entry'] = {
	add_fields: ["payment_type"],
	filters: [["status", "=", "Draft"]],
	get_indicator: function(doc) {
		//return [__(doc.payment_type), (doc.docstatus==0 ? 'red' : 'blue'), 'status=' + doc.payment_type]
		if(doc.payment_type == "Pay") {
			return [__("Paid"), "blue", 'status,=,' + doc.payment_type];
		}
		else if(doc.payment_type == "Receive") {
			return [__("Received"), "blue", 'status,=,' + doc.payment_type];
		}
		else {
			return [__(doc.payment_type), (doc.docstatus==0 ? 'red' : 'blue'), 'status,=,' + doc.payment_type]
		}
	}
}
