frappe.listview_settings['Overtime Payment'] = {
	add_fields: ["payment_status", "docstatus"],
	// filters:[["status","=", "Pending"]],
	// colwidths: {"name":2, "status":2, "expected_start_date":2},
	get_indicator: function(doc) {
        var status = {"Payment Under Process": "orange",
                        "Payment Successful": "green",
                        "Payment Failed": "red",
                        "Payment Cancelled": "black",
                        };
        
        if(doc.payment_status){
            return [__(doc.payment_status), status[doc.payment_status], "payment_status,=," + doc.payment_status];
        }
	},
};
