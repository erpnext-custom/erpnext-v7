// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Change Status', {
	refresh: function(frm) {

	},
	"transaction_type": function(frm) {
		frm.set_query("transaction_no", function() {
			if(frm.doc.transaction_type == "Load Request"){
				return {
					"filters": {
						"crm_branch":frm.doc.branch,
						"load_status": "Queued",
					}
				}
			}else{
				return {
                                        "filters": {
                                                "branch":frm.doc.branch,
						"confirmation_status": "In Transit"
                                        }
                                }
			}
		});
		frm.set_value("vehicle","");
		frm.set_value("delivery_note","");
		frm.set_value("customer","");
		frm.set_value("capacity","");
		frm.set_value("transaction_no","");
		frm.set_value("status_to","");
	},
	"transaction_no": function(frm) {
/*		if(frm.doc.transaction_type == "Load Request"){ 
			frm.set_value("status_to","Remove From Queue")
		}else{
			frm.set_value("status_to","Confirm Delivery")
		}		*/
	}
});


