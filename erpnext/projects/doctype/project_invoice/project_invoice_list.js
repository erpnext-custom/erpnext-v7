frappe.listview_settings['Project Invoice']={
	add_fields: ["status","docstatus","total_balance_amount"],
	filters: [["status", "=", "Unpaid"]],
	get_indicator: function(doc){
		var colors = {
			"Draft": "red",
			"Unpaid": "orange",
			"Paid": "green",
			"Cancelled": "darkgrey"
		};		

		//console.log(cur_list);
		//return [__(doc.status), colors[doc.status], "status,=," + doc.status];

		if(doc.status == "Draft"){
			return [__("Draft"), "orange", "status,=," + doc.status];
		}
		else if(parseFloat(doc.total_balance_amount) > 0.0 || doc.status == "Unpaid"){
			return [__("Unpaid"), "red", "status,=," + doc.status];
		}
		else if(parseFloat(doc.total_balance_amount) == 0.0 || doc.status == "Paid"){
			return [__("Paid"), "green", "status,=," + doc.status];
		}
		else if(doc.docstatus==2 || doc.status == "Cancelled"){
			return [__("Cancelled"), "darkgrey", "status,=," + doc.status];
		}
	}
};