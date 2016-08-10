// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.hr");

erpnext.hr.ExpenseClaimController = frappe.ui.form.Controller.extend({
	make_bank_entry: function() {
		var me = this;
		return frappe.call({
			method: "erpnext.hr.doctype.expense_claim.expense_claim.make_bank_entry",
			args: {
				"docname": cur_frm.doc.name,
			},
			callback: function(r) {
				var doc = frappe.model.sync(r.message);
				frappe.set_route('Form', 'Journal Entry', r.message.name);
			}
		});
	},
	
	expense_type: function(frm, cdt, cdn) {
		var d = locals[cdt][cdn];

		return frappe.call({
			method: "erpnext.hr.doctype.expense_claim.expense_claim.get_expense_claim_account",
			args: {
				"expense_claim_type": d.expense_type,
				"company": frm.company
			},
			callback: function(r) {
				if (r.message) {
					d.default_account = r.message.account;
				}
			}
		});
	}
})

$.extend(cur_frm.cscript, new erpnext.hr.ExpenseClaimController({frm: cur_frm}));

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('employee','employee_name','employee_name');

cur_frm.cscript.onload = function(doc,cdt,cdn) {
	if(!doc.approval_status)
		cur_frm.set_value("approval_status", "Draft")

	if (doc.__islocal) {
		cur_frm.set_value("posting_date", dateutil.get_today());
		if(doc.amended_from)
			cur_frm.set_value("approval_status", "Draft");
		cur_frm.cscript.clear_sanctioned(doc);
	}

	cur_frm.fields_dict.employee.get_query = function(doc,cdt,cdn) {
		return{
			query: "erpnext.controllers.queries.employee_query"
		}
	};

	cur_frm.set_query("exp_approver", function() {
		return {
			query: "erpnext.hr.doctype.expense_claim.expense_claim.get_expense_approver"
		};
	});
}

cur_frm.cscript.clear_sanctioned = function(doc) {
	var val = doc.expenses || [];
	for(var i = 0; i<val.length; i++){
		val[i].sanctioned_amount ='';
	}

	doc.total_sanctioned_amount = '';
	refresh_many(['sanctioned_amount', 'total_sanctioned_amount']);
}

cur_frm.cscript.refresh = function(doc,cdt,cdn){
	cur_frm.cscript.set_help(doc);

	if(!doc.__islocal) {
		cur_frm.toggle_enable("exp_approver", doc.approval_status=="Draft");
		cur_frm.toggle_enable("approval_status", (doc.exp_approver==user && doc.docstatus==0));

		if (doc.docstatus==0 && doc.exp_approver==user && doc.approval_status=="Approved")
			 cur_frm.savesubmit();

		if (doc.docstatus===1 && doc.approval_status=="Approved") {
			if (cint(doc.total_amount_reimbursed) < cint(doc.total_sanctioned_amount) && frappe.model.can_create("Journal Entry")) {
				cur_frm.add_custom_button(__("Bank Entry"), cur_frm.cscript.make_bank_entry, __("Make"));
				cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
			}

			if (cint(doc.total_amount_reimbursed) > 0 && frappe.model.can_read("Journal Entry")) {
				cur_frm.add_custom_button(__('Bank Entries'), function() {
					frappe.route_options = {
						"Journal Entry Account.reference_type": me.frm.doc.doctype,
						"Journal Entry Account.reference_name": me.frm.doc.name,
						company: me.frm.doc.company
					};
					frappe.set_route("List", "Journal Entry");
				}, __("View"));
			}
		}
	}
}

cur_frm.cscript.set_help = function(doc) {
	cur_frm.set_intro("");
	if(doc.__islocal && !in_list(user_roles, "HR User")) {
		cur_frm.set_intro(__("Fill the form and save it"))
	} else {
		if(doc.docstatus==0 && doc.approval_status=="Draft") {
			if(user==doc.exp_approver) {
				cur_frm.set_intro(__("You are the Expense Approver for this record. Please Update the 'Status' and Save"));
			} else {
				cur_frm.set_intro(__("Expense Claim is pending approval. Only the Expense Approver can update status."));
			}
		}
	}
}

cur_frm.cscript.validate = function(doc) {
	cur_frm.cscript.calculate_total(doc);
}

cur_frm.cscript.calculate_total = function(doc,cdt,cdn){
	doc.total_claimed_amount = 0;
	doc.total_sanctioned_amount = 0;
	$.each((doc.expenses || []), function(i, d) {
		doc.total_claimed_amount += d.claim_amount;
		if(d.sanctioned_amount==null) {
			d.sanctioned_amount = d.claim_amount;
		}
		doc.total_sanctioned_amount += d.sanctioned_amount;
	});

	refresh_field("total_claimed_amount");
	refresh_field('total_sanctioned_amount');

}

cur_frm.cscript.calculate_total_amount = function(doc,cdt,cdn){
	cur_frm.cscript.calculate_total(doc,cdt,cdn);
}

cur_frm.cscript.claim_amount = function(doc,cdt,cdn){
	cur_frm.cscript.calculate_total(doc,cdt,cdn);

	var child = locals[cdt][cdn];
	refresh_field("sanctioned_amount", child.name, child.parentfield);
}

cur_frm.cscript.sanctioned_amount = function(doc,cdt,cdn){
	cur_frm.cscript.calculate_total(doc,cdt,cdn);
}

cur_frm.cscript.on_submit = function(doc, cdt, cdn) {
	if(cint(frappe.boot.notification_settings && frappe.boot.notification_settings.expense_claim)) {
		cur_frm.email_doc(frappe.boot.notification_settings.expense_claim_message);
	}
}

erpnext.expense_claim = {
	set_title :function(frm) {
		if (!frm.doc.task) {
			frm.set_value("title", frm.doc.employee_name);
		}
		else {
			frm.set_value("title", frm.doc.employee_name + " for "+ frm.doc.task);
		}
	}
}

frappe.ui.form.on("Expense Claim", "employee_name", function(frm) {
	erpnext.expense_claim.set_title(frm);
});

frappe.ui.form.on("Expense Claim", "task", function(frm) {
	erpnext.expense_claim.set_title(frm);
});

cur_frm.fields_dict['task'].get_query = function(doc) {
	return {
		filters:{
			'project': doc.project
		}
	}
}

// Ver 1.0 by SSK on 10/08/2016, Following code added 
frappe.ui.form.on("Expense Claim Detail","dsa_rate",function(frm, cdt, cdn){
	var item = frappe.get_doc(cdt, cdn);
	console.log('Something is happening...');
	console.log(frm);
	console.log(cdt);
	console.log(cdn);
	console.log(item.dsa_rate);
	
	frappe.call({
		"method": "frappe.client.get",
		args: {
			doctype: "DSA Rates",
			name: item.dsa_rate
		},
		callback: function(r){
			console.log(r.message.dsa_rate);
		}
	});
});

frappe.ui.form.on("Expense Claim Detail", "dsa_rate_per_day", function(frm, cdt, cdn) {
	calculate_claim(cdt, cdn);	
	frappe.model.set_value(cdt, cdn, "claim_amount", 100);
});

frappe.ui.form.on("Expense Claim Detail", "currency", function(frm, cdt, cdn) {
	calculate_claim(cdt, cdn);
	frappe.model.set_value(cdt, cdn, "claim_amount", 200);
});

frappe.ui.form.on("Expense Claim Detail", "dsa_entitled", function(frm, cdt, cdn) {
	calculate_claim(cdt, cdn);
	console.log(cur_frm.doc);
	console.log(cur_frm.doc.claim_amount);
	console.log(cur_frm.doc.expenses);

	//frappe.model.set_value(cdt, cdn, "claim_amount", frappe.utils.date_diff());
	
	//var child = locals[cdt][cdn];
	//refresh_field("sanctioned_amount", child.name, child.parentfield);
	//console.log(child.claim_amount);
	//frappe.model.set_value(cdt, cdn, "claim_amount", 300);
});

function calculate_claim(cdt, cdn){
	var child = locals[cdt][cdn];
	
	frappe.model.set_value(cdt, cdn, "claim_amount", 5*child.dsa_rate_per_day*child.dsa_entitled*child.exchange_rate*0.01);
}
