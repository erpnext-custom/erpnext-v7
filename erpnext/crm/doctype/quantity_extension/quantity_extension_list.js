frappe.listview_settings['Quantity Extension'] = {
	add_fields: ["docstatus", "approval_status"],
	get_indicator: function(doc) {
        if(doc.docstatus===1){
            if(doc.approval_status === "Approved"){
        	    return [__("Approved"), "green", "approval_status,=,Approved"];
            }
            else if(doc.approval_status === "Rejected"){
        	    return [__("Rejected"), "red", "approval_status,=,Rejected"];
            }
        } else if ( doc.docstatus === 0 ) {
			// to bill & overdue
			return [__("Draft"), "red", "docstatus,=,0"];

		} else if (doc.docstatus === 2) {
			return [__("Cancelled"), "red", "docstatus,=,2s"];
		}
	},
	// onload: function(listview) {
	// 	var method = "erpnext.selling.doctype.sales_order.sales_order.close_or_unclose_sales_orders";

	// 	listview.page.add_menu_item(__("Close"), function() {
	// 		listview.call_for_selected_items(method, {"status": "Closed"});
	// 	});

	// 	listview.page.add_menu_item(__("Re-open"), function() {
	// 		listview.call_for_selected_items(method, {"status": "Submitted"});
	// 	});

	// }
};
