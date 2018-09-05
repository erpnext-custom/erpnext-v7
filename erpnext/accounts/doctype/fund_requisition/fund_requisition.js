// Copyright (c) 2016, Firappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

//cur_frm.add_fetch("cost_center", "branch", "branch")

frappe.ui.form.on('Fund Requisition', {

	refresh: function(frm){
		/*cur_frm.set_df_property("issuing_cost_center", "hidden", 1)
		cur_frm.set_df_property("bank_account", "hidden", 1)
		cur_frm.set_df_property("issuing_branch", "hidden", 1)
	
		if (in_list(user_roles, "Accounts User") && (frm.doc.workflow_state == "Approved")){
			cur_frm.set_df_property("issuing_cost_center", "hidden",  0)
			cur_frm.set_df_property("issuing_branch", "hidden", 0)
			cur_frm.set_df_property("bank_account", "hidden", 0)
			}	*/
		if (frm.doc.docstatus == 1){
			/*cur_frm.set_df_property("issuing_cost_center", "hidden", 0)
			cur_frm.set_df_property("issuing_branch", "hidden", 0)  
			cur_frm.set_df_property("bank_account", "hidden", 0)
			*/	
			
				 if (frappe.model.can_read("Journal Entry")){
        	                        cur_frm.add_custom_button(__('Bank Entries'), function(){
                	                frappe.route_options = {
                        	                "name": me.frm.doc.reference,
                                	};
                                frappe.set_route("List", "Journal Entry");
                }, __("View"));
        }
			}
		
		//frm.toggle_reqd("bank_account", 1)
         },
	
	"posting_date" : function(frm){
		if (frm.doc.posting_date > get_today()){
			frappe.msgprint("Future dates not allowed");
			frm.set_value("posting_date", get_today());
		}
	},

	"issuing_cost_center": function(frm){
		frm.toggle_reqd("issuing_cost_center", 1)
	},

	"bank_account" : function(frm){
		frm.toggle_reqd("bank_account", 1)	
	},
	
	"branch": function(frm) {
		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Branch", 
				fieldname:"expense_bank_account",
				filters: {
					"branch": frm.doc.branch
				}
			},
			callback: function(r) {
				console.log(r.message);
				if(r.message.expense_bank_account) {
					cur_frm.set_value("bank", r.message.expense_bank_account)
					console.log(r.message.expense_bank_account)
				}
				else {
					frappe.throw("Setup an Expense Bank Account in the Branch")
				}
			}
		});
	},
	
});
//	"branch": function(frm){
//		return frappe.call({
//			method: "erpnext.custom_utils.get_branch_cc",
//			args: {
//				"branch": frm.doc.branch
//			},
//			callback: function(r) {
//			cur_frm.set_value("cost_center", r.message)
			//console.log(r)
//			cur_frm.refresh_fields()
//			}
//		});
	
//	},
	/*"issuing_branch": function(frm){
                return frappe.call({
                        method: "erpnext.custom_utils.get_branch_cc",
                        args: {
                                "branch": frm.doc.issuing_branch
                        },
                        callback: function(r) {
                        cur_frm.set_value("issuing_cost_center", r.message)
                        cur_frm.refresh_fields()
_dd_fetch('item_code','soi_size','soi_size')icur_frm.add_fetch('item_code','soi_size','soi_size')                       }
                });
	}*/


	
//});
