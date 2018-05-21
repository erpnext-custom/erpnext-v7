// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/*
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
  2.0		      SHIV           05/09/2017                          Original Version
--------------------------------------------------------------------------------------------------------------------------                                                                          
*/

cur_frm.add_fetch("project", "branch", "branch");
cur_frm.add_fetch("project", "cost_center", "cost_center");
cur_frm.add_fetch("project", "customer", "pay_to_recd_from");
cur_frm.add_fetch("branch","revenue_bank_account","revenue_bank_account");

frappe.ui.form.on('Project Payment', {
	onload: function(frm, cdt, cdn){
		if(frm.doc.project && frm.doc.__islocal){
			if(frm.doc.docstatus === 0){
				get_invoice_list(frm);
				get_advance_list(frm);
				assign_items(frm, cdt, cdn);
			}
		}
	},

	setup: function(frm) {
		frm.get_field('references').grid.editable_fields = [
			{fieldname: 'reference_doctype', columns: 2},
			{fieldname: 'reference_name', columns: 2},
			{fieldname: 'total_amount', columns: 2},
			{fieldname: 'allocated_amount', columns: 2}
		];
		frm.get_field('advances').grid.editable_fields = [
			{fieldname: 'reference_doctype', columns: 2},
			{fieldname: 'reference_name', columns: 2},
			{fieldname: 'total_amount', columns: 2},
			{fieldname: 'allocated_amount', columns: 2}
		];
		frm.get_field('deductions').grid.editable_fields = [
			{fieldname: 'account', columns: 3},
			{fieldname: 'cost_center', columns: 2},
			{fieldname: 'amount', columns: 2}
		];		
	},
	
	refresh: function(frm, cdt, cdn) {
		enable_disable(frm);
		if(frm.doc.docstatus===1){
			frm.add_custom_button(__('Accounting Ledger'), function(){
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: frm.doc.posting_date,
					company: frm.doc.company,
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
		} else {
			if(frm.doc.docstatus != 2){
				assign_items(frm, cdt, cdn);
			}
		}
	},
	
	get_invoices_dummy: function(frm){

	},
	
	get_advances_dummy: function(frm){

	},
	
	get_invoices: function(frm, cdt, cdn){
		get_invoice_list(frm);
		//assign_items(frm, cdt, cdn);
	},
	
	get_advances: function(frm, cdt, cdn){
		get_advance_list(frm);
		//assign_items(frm, cdt, cdn);
	},
	
	project: function(frm, cdt, cdn){
		get_invoice_list(frm);
		get_advance_list(frm);
		assign_items(frm, cdt, cdn);
	},
	
	paid_amount: function(frm, cdt, cdn){
		assign_items(frm, cdt, cdn);
	},
	
	tds_amount: function(frm, cdt, cdn){
		assign_items(frm, cdt, cdn);
		if(!self.tds_account){
			set_tds_account(frm);
		}
	},

	get_series: function(frm) {
		return frappe.call({
			method: "get_series",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.reload_doc();
			}
		});
	},
	
	select_cheque_lot: function(frm){
		if(frm.doc.select_cheque_lot){
			frappe.call({
				method: "erpnext.accounts.doctype.cheque_lot.cheque_lot.get_cheque_no_and_date",
				args: {
				'name': frm.doc.select_cheque_lot
				},
				callback: function(r){
				   if (r.message) {
					   cur_frm.set_value("cheque_no", r.message[0].reference_no);
					   cur_frm.set_value("cheque_date", r.message[1].reference_date);
				   }
				   }
			});
		}
	},
	
	branch: function(frm) {
		set_revenue_bank_account(frm);
    },
	
	payment_type: function(){
		enable_disable(frm);
	},
});

frappe.ui.form.on("Project Payment Advance",{
	allocated_amount: function(frm, cdt, cdn){
		assign_items(frm, cdt, cdn);
	},
	
	advances_remove: function(frm, cdt, cdn){
		assign_items(frm, cdt, cdn);
	},
})

frappe.ui.form.on("Project Payment Deduction",{
	amount: function(frm, cdt, cdn){
		assign_items(frm, cdt, cdn);
	},
	
	deductions_remove: function(frm, cdt, cdn){
		assign_items(frm, cdt, cdn);
	},
	
	deductions_add: function(frm, cdt, cdn){
		child = locals[cdt][cdn];
		
		frappe.model.set_value(cdt, cdn, 'cost_center', frm.doc.cost_center);
	},
})

var set_tds_account = function(frm){
	frappe.model.get_value('Sales Accounts Settings',{'name': 'Sales Accounts Settings'}, 'tds_account', 
		function(r){
			cur_frm.set_value("tds_account", r.tds_account);
		});
}

var assign_items = function(frm, cdt, cdn){
	var pr = frm.doc.references || [];
	var pa = frm.doc.advances || [];
	var pd = frm.doc.deductions || [];
	var paid_amount = parseFloat(frm.doc.paid_amount || 0.0);
	
	//Advances
	for(var id in pa){
		paid_amount += parseFloat(pa[id].allocated_amount || 0.0);
	}	
	
	//Other Deductions
	for(var id in pd){
		paid_amount += parseFloat(pd[id].amount || 0.0);
	}	
	
	//TDS 
	paid_amount += parseFloat(frm.doc.tds_amount || 0.0);
	
	cur_frm.set_value("total_amount",parseFloat(paid_amount));
	
	for(var id in pr){
		if(paid_amount > 0){
			if(pr[id].total_amount <= paid_amount){
				frappe.model.set_value("Project Payment Reference", pr[id].name, "allocated_amount", parseFloat(pr[id].total_amount));
				paid_amount -= parseFloat(pr[id].total_amount);
			}
			else{
				frappe.model.set_value("Project Payment Reference", pr[id].name, "allocated_amount", parseFloat(paid_amount));
				paid_amount = 0.0;
			}
		}
		else {
			frappe.model.set_value("Project Payment Reference", pr[id].name, "allocated_amount", 0.0);
		}
	}			
}


var get_invoice_list = function(frm){
	frappe.call({
		method: "erpnext.accounts.doctype.project_payment.project_payment.get_invoice_list",
		args: {
			"project": frm.doc.project,
			"reference_name": frm.doc.reference_name || "dummy"
		},
		callback: function(r){
			if(r.message){
				cur_frm.clear_table("references");
				r.message.forEach(function(inv){
					var row = frappe.model.add_child(frm.doc, "Project Payment Reference", "references");
					row.reference_doctype = "Project Invoice";
					row.reference_name    = inv['name'];
					row.invoice_type	  = inv['invoice_type'];
					row.total_amount      = parseFloat(inv['total_balance_amount']);
					row.allocated_amount  = 0.00;
				});
				cur_frm.refresh();
			}
			else {
				cur_frm.clear_table("references");
				cur_frm.refresh();
			}
		}
	});
}

var get_advance_list = function(frm){
	frappe.call({
		method: "erpnext.accounts.doctype.project_payment.project_payment.get_advance_list",
		args: {
			"project": frm.doc.project,
		},
		callback: function(r){
			if(r.message){
				cur_frm.clear_table("advances");
				r.message.forEach(function(adv){
					var row = frappe.model.add_child(frm.doc, "Project Payment Advance", "advances");
					row.reference_doctype = "Project Advance";
					row.reference_name    = adv['name'];
					row.total_amount      = parseFloat(adv['balance_amount']);
					row.allocated_amount  = 0.00;
				});
				cur_frm.refresh();
			}
			else {
				cur_frm.clear_table("advances");
				cur_frm.refresh();
			}
		}
	});
}

function enable_disable(frm){
	var toggle_fields = ["revenue_bank_account","pay_to_recd_from", "use_cheque_lot","select_cheque_lot","cheque_no", "cheque_date"];
	
	toggle_fields.forEach(function(field_name){
		frm.set_df_property(field_name,"read_only",1);
	});
		
	if(in_list(user_roles, "Accounts Manager") || in_list(user_roles, "Accounts User")){
		toggle_fields.forEach(function(field_name){
				frm.set_df_property(field_name,"read_only",0);
		});
		frm.toggle_reqd(["revenue_bank_account","pay_to_recd_from", "cheque_no", "cheque_date"], 1);
	}
	
	if(frm.doc.branch && !frm.doc.revenue_bank_account){
		set_revenue_bank_account(frm);
	}
}

function set_revenue_bank_account(frm){
	frappe.call({
		method: "frappe.client.get_value",
		args: {
				doctype: "Branch",
				fieldname:"revenue_bank_account",
				filters: {
						name: frm.doc.branch
				}
		},
		callback: function(r) {
				if(r.message.revenue_bank_account) {
						cur_frm.set_value("revenue_bank_account", r.message.revenue_bank_account)
				}
				else {
						frappe.throw("Setup an Revenue Bank Account in the Branch")
				}
		}
	});
}