// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Benefits', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 1 && frm.doc.journal){
			cur_frm.add_custom_button(__('Bank Entries'), function() {
				frappe.route_options = {
					"Journal Entry Account.reference_type": me.frm.doc.doctype,
					"Journal Entry Account.reference_name": me.frm.doc.name,
				};
				frappe.set_route("List", "Journal Entry");
			}, __("View"));
		}
		
		if(frm.doc.workflow_state == "Draft" || frm.doc.workflow_state == "Rejected"){
                        frm.set_df_property("benefit_approver", "hidden", 1);
                        frm.set_df_property("benefit_approver_name", "hidden",1);
                }

		if(!frm.doc.__islocal && frm.doc.workflow_state != "Draft"){
			console.log("testing : purpose:" + frm.doc.workflow_state);
                        frm.set_df_property("purpose", "read_only", 1);
		}


	},
	onload: function(frm) {
		if(!frm.doc.posting_date) {
			cur_frm.set_value("posting_date", get_today())
		}
	},
	"total_amount": function(frm) {
				var total_amount = 0;
				for (var i in cur_frm.doc.items) {
					var item = cur_frm.doc.items[i];
					total_amount += item.amount;
				}
				console.log("testing..." + total_amount);
				frm.set_value("total_amount",total_amount);
		        }
		
});

frappe.ui.form.on("Separation Item", {
        "benefit_type": function(frm, cdt, cdn) {
        	var item = locals[cdt][cdn]
		if(item.benefit_type == "Transfer Grant"){
			return frappe.call({
				method: "erpnext.hr.doctype.employee_benefits.employee_benefits.get_basic_salary",
				args: {"employee": frm.doc.employee},
				callback: function(r) {
					console.log(r.message);
					if(r.message) {
						frappe.model.set_value(cdt, cdn,"amount", r.message);
					}
					cur_frm.refresh_fields()
				}
			});
		}	
	},

	"amount": function(frm, cdt, cdn) {
		var total_amount = 0;
		for (var i in cur_frm.doc.items) {
			var item = cur_frm.doc.items[i];
			total_amount += item.amount;
		}
		console.log("testing..." + total_amount);
		frm.set_value("total_amount",total_amount);
	},

});

