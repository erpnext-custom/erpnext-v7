frappe.listview_settings['Project Invoice']={
	add_fields: ["invoice_title", "status", "invoice_date", "net_invoice_amount"],
	filters: [["status", "=", "Unpaid"]],
	get_indicator: function(doc){
		var colors = {
			"Open": "orange",
			"Overdue": "red",
			"Pending Review": "orange",
			"Working": "orange",
			"Closed": "green",
			"Cancelled": "dark grey",
			"Unpaid": "red",
			"Paid": "green",
			"Cancelled": "dark grey"
		}		
		
		if(parseFloat(doc.total_balance_amount) > 0.0 || doc.status == "Unpaid"){
			//return [__(doc.status), colors[doc.status], "status,=," + doc.status];
			return [__("Unpaid"), "red", "status,=," + doc.status];
		}
		else if(parseFloat(doc.total_balance_amount) == 0.0 || doc.status == "Paid"){
			return [__("Paid"), "green", "status,=," + doc.status];
		}
		else if(doc.docstatus==2 || doc.status == "Cancelled"){
			return [__("Cancelled"), "dark grey", "status,=," + doc.status];
		}
	}
};