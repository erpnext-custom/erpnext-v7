// frappe.listview_settings['Consolidated Invoice']={
// 	add_fields: ["status","docstatus","total_amount","payment_entry"],
// 	filters: [["status", "=", "Unpaid"]],
// 	get_indicator: function(doc){
// 		var colors = {
// 			"Draft": "red",
// 			"Unpaid": "orange",
// 			"Paid": "green",
// 			"Cancelled": "darkgrey"
// 		};		

// 		var balance = 0.0;
		
// 		if(parseFloat(doc.total_received_amount || 0.0) > 0.0){
// 			balance = 100-Math.round(parseFloat(doc.total_received_amount || 0.0)/parseFloat(doc.net_invoice_amount || 1)*100);
// 		}
// 		else{
// 			balance = 100;
// 		}
		
// 		if(doc.payment_entry){
//             return [__("Paid"), "green", "payment_entry,!=,null"];
//         }

// 		// if(doc.status == "Draft"){
// 		// 	return [__("Draft"), "orange", "status,=," + doc.status];
// 		// }
// 		// else if(parseFloat(doc.total_balance_amount) > 0.0 || doc.status == "Unpaid"){
// 		// 	return [__("{0}% Receivable", [balance]), "red", "status,=," + doc.status];
// 		// }
// 		// else if(parseFloat(doc.total_balance_amount) == 0.0 || doc.status == "Paid"){
// 		// 	return [__("Received"), "green", "status,=," + doc.status];
// 		// }
// 		// else if(doc.docstatus==2 || doc.status == "Cancelled"){
// 		// 	return [__("Cancelled"), "darkgrey", "status,=," + doc.status];
// 		// }
// 	}
// };