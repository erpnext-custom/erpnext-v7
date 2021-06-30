frappe.listview_settings['Payment Entry'] = {
	add_fields: ["payment_type"],
	filters: [["status", "=", "Draft"]],
	get_indicator: function(doc) {
		/* ePayment Begins */
		var status = {"Payment Under Process": "orange",
			"Payment Successful": "green",
			"Payment Failed": "red",
			"Payment Cancelled": "black",
		};

		if(doc.payment_status){
			return [__(doc.payment_status), status[doc.payment_status], "payment_status,=," + doc.payment_status];
		}
		/* ePayment Ends */
		
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
