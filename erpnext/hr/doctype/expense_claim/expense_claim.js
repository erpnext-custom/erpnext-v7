// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

/*
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  		  SSK		                        10/08/2016         Validations for DSA, Mileage, Advance, Other Expense
																		     introducted.
1.0		  		  SSK		                        11/08/2016         Following columns introducted
                                                                          i) total_advance_amount
																		 ii) net_claimed_amount
1.0		  		  SSK		                        02/09/2016         Travel Authorization workflow introduced
1.0               SSK                               07/09/2016         Travel Claim Date field is added
--------------------------------------------------------------------------------------------------------------------------                                                                          
*/
var local_status = '';
frappe.provide("erpnext.hr");

erpnext.hr.ExpenseClaimController = frappe.ui.form.Controller.extend({
	make_bank_entry: function() {
		var me = this;
		return frappe.call({
			method: "erpnext.hr.doctype.expense_claim.expense_claim.make_bank_entry",
			args: {
				"docname": cur_frm.doc.name,
			},
			/*
			callback: function(r) {
				var doc = frappe.model.sync(r.message);
				frappe.set_route('Form', 'Journal Entry', r.message.name);
			}
			*/
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

frappe.ui.form.on("Expense Claim", {
	onload: function(frm) {
		frm.set_query("exp_approver", function() {
			return {
				query: "erpnext.hr.doctype.expense_claim.expense_claim.get_expense_approver",
				filters: {
					employee: frm.doc.employee
				}
			};
		});
	}
});

cur_frm.cscript.onload = function(doc,cdt,cdn) {
	console.log('onload is triggered.');
	
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
			query: "erpnext.hr.doctype.expense_claim.expense_claim.get_expense_approver",
			filters: {
				employee: frm.doc.employee
			}
		};
	});
}

cur_frm.cscript.onload = function(frm,cdt,cdn) {
	local_status = frm.workflow_state;
	// Ver 1.0 Begins, added by SSK on 07/09/2016
	// Following code is added
	if (local_status == 'Travel Claim Draft' && !frm.expense_date){
		cur_frm.set_value("expense_date", dateutil.get_today());
	}
	// Ver 1.0 Ends	
}

frappe.ui.form.on("Expense Claim","expenses_on_form_rendered", function(frm, grid_row, cdt, cdn) {
	var grid_row = cur_frm.open_grid_row();
	
	if (!grid_row.grid_form.fields_dict.currency.value || grid_row.grid_form.fields_dict.currency.value == 'BTN'){
		grid_row.grid_form.fields_dict.currency.set_value('BTN-Nu');
	}
	
	if (!local_status || local_status == 'Travel Request Draft'){
		if (in_list(user_roles, "HR User")) {
			enable_disable(false,false,false);
			grid_row.grid_form.fields_dict.sanctioned_amount.df.hidden = false;
			grid_row.grid_form.fields_dict.sanctioned_amount.refresh()
		}
		else{
			enable_disable(false,true,false);
			grid_row.grid_form.fields_dict.sanctioned_amount.df.hidden = false;
			grid_row.grid_form.fields_dict.sanctioned_amount.refresh()
		}
	}
	else if (local_status == 'Travel Claim Draft'){
		if (!in_list(user_roles, "Expense Approver")) {
			enable_disable(true,false,false);
			grid_row.grid_form.fields_dict.sanctioned_amount.df.hidden = true;
			grid_row.grid_form.fields_dict.sanctioned_amount.refresh()
		}
		else{
			if (in_list(user_roles, "HR User")) {
				enable_disable(false,false,false);
				grid_row.grid_form.fields_dict.sanctioned_amount.df.hidden = false;
				grid_row.grid_form.fields_dict.sanctioned_amount.refresh()
			}
			else{
				enable_disable(false,false,true);
				grid_row.grid_form.fields_dict.sanctioned_amount.df.hidden = false;
				grid_row.grid_form.fields_dict.sanctioned_amount.refresh()
			}
		}
	}
	else if (local_status == 'Travel Claim Approved by Supervisor'){
		if (in_list(user_roles, "HR User")) {
			enable_disable(false,false,false);
			grid_row.grid_form.fields_dict.sanctioned_amount.df.hidden = false;
			grid_row.grid_form.fields_dict.sanctioned_amount.refresh()			
		}
		else if (in_list(user_roles, "Expense Approver")){
			enable_disable(false,false,true);
			grid_row.grid_form.fields_dict.sanctioned_amount.df.hidden = true;
			grid_row.grid_form.fields_dict.sanctioned_amount.refresh()			
		}
		else{
			enable_disable(true,false,true);
		}
	}
	else if (local_status == 'Travel Claim Approved by HR'){
		if (in_list(user_roles, "HR User")) {
			enable_disable(false,false,false);
		}
	}
	
	function enable_disable(req_status, hide_status, read_status){
		// Required 
		grid_row.grid_form.fields_dict.dsa_rate_per_day.df.reqd = req_status;
		//grid_row.grid_form.fields_dict.expense_type.df.reqd = req_status;
		
		// Read-Only
		grid_row.grid_form.fields_dict.dsa_rate_per_day.df.read_only = read_status;
		//grid_row.grid_form.fields_dict.expense_type.df.read_only = read_status;
		//grid_row.grid_form.fields_dict.total_claim.df.read_only = read_status;
		grid_row.grid_form.fields_dict.expense_date.df.read_only = read_status;
		grid_row.grid_form.fields_dict.country_from.df.read_only = read_status;
		grid_row.grid_form.fields_dict.place_from.df.read_only = read_status;
		grid_row.grid_form.fields_dict.to_date.df.read_only = read_status;
		grid_row.grid_form.fields_dict.country_to.df.read_only = read_status;
		grid_row.grid_form.fields_dict.place_to.df.read_only = read_status;
		grid_row.grid_form.fields_dict.expense_type.df.read_only = read_status;
		grid_row.grid_form.fields_dict.modes_of_travel.df.read_only = read_status;
		grid_row.grid_form.fields_dict.currency.df.read_only = read_status;
		//grid_row.grid_form.fields_dict.exchange_rate.df.read_only = read_status;
		grid_row.grid_form.fields_dict.dsa_entitled.df.read_only = read_status;
		grid_row.grid_form.fields_dict.other_expense_amount.df.read_only = read_status;
		grid_row.grid_form.fields_dict.mileage.df.read_only = read_status;
		grid_row.grid_form.fields_dict.other_expense_currency.df.read_only = read_status;
		grid_row.grid_form.fields_dict.mileage_currency.df.read_only = read_status;
		//grid_row.grid_form.fields_dict.other_expense_exchange_rate.df.read_only = read_status;
		grid_row.grid_form.fields_dict.mileage_rate2.df.read_only = read_status;
		//grid_row.grid_form.fields_dict.other_expense_total_amount.df.read_only = read_status;
		//grid_row.grid_form.fields_dict.mileage_total_amount.df.read_only = read_status;
		grid_row.grid_form.fields_dict.advance_amount.df.read_only = read_status;
		grid_row.grid_form.fields_dict.advance_currency.df.read_only = read_status;
		//grid_row.grid_form.fields_dict.advance_exchange_rate.df.read_only = read_status;
		//grid_row.grid_form.fields_dict.advance_total_amount.df.read_only = read_status;
		grid_row.grid_form.fields_dict.description.df.read_only = read_status;
		//grid_row.grid_form.fields_dict.claim_amount.df.read_only = read_status;
		//grid_row.grid_form.fields_dict.sanctioned_amount.df.read_only = read_status;
		if (local_status == 'Travel Claim Approved by Supervisor' && !in_list(user_roles, "HR User")){
			grid_row.grid_form.fields_dict.sanctioned_amount.df.read_only = true;
		}
		
		// Hide
		grid_row.grid_form.fields_dict.dsa_rate_per_day.df.hidden = hide_status;
		//grid_row.grid_form.fields_dict.expense_type.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.total_claim.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.currency.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.exchange_rate.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.dsa_entitled.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.other_expense_amount.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.mileage.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.other_expense_currency.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.mileage_currency.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.other_expense_exchange_rate.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.mileage_rate2.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.other_expense_total_amount.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.mileage_total_amount.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.advance_amount.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.advance_currency.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.advance_exchange_rate.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.advance_total_amount.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.description.df.hidden = hide_status;
		grid_row.grid_form.fields_dict.claim_amount.df.hidden = hide_status;
		//grid_row.grid_form.fields_dict.sanctioned_amount.df.hidden = hide_status;
		
		// Refresh
		grid_row.grid_form.fields_dict.dsa_rate_per_day.refresh()
		grid_row.grid_form.fields_dict.expense_date.refresh()
		grid_row.grid_form.fields_dict.country_from.refresh()
		grid_row.grid_form.fields_dict.place_from.refresh()
		grid_row.grid_form.fields_dict.to_date.refresh()
		grid_row.grid_form.fields_dict.country_to.refresh()
		grid_row.grid_form.fields_dict.place_to.refresh()
		grid_row.grid_form.fields_dict.expense_type.refresh()
		grid_row.grid_form.fields_dict.modes_of_travel.refresh()
		grid_row.grid_form.fields_dict.total_claim.refresh()
		grid_row.grid_form.fields_dict.currency.refresh()
		//grid_row.grid_form.fields_dict.exchange_rate.refresh()
		grid_row.grid_form.fields_dict.dsa_entitled.refresh()
		grid_row.grid_form.fields_dict.other_expense_amount.refresh()
		grid_row.grid_form.fields_dict.mileage.refresh()
		grid_row.grid_form.fields_dict.other_expense_currency.refresh()
		grid_row.grid_form.fields_dict.mileage_currency.refresh()
		//grid_row.grid_form.fields_dict.other_expense_exchange_rate.refresh()
		grid_row.grid_form.fields_dict.mileage_rate2.refresh()
		//grid_row.grid_form.fields_dict.other_expense_total_amount.refresh()
		//grid_row.grid_form.fields_dict.mileage_total_amount.refresh()
		grid_row.grid_form.fields_dict.advance_amount.refresh()
		grid_row.grid_form.fields_dict.advance_currency.refresh()
		//grid_row.grid_form.fields_dict.advance_exchange_rate.refresh()
		//grid_row.grid_form.fields_dict.advance_total_amount.refresh()
		grid_row.grid_form.fields_dict.description.refresh()
		grid_row.grid_form.fields_dict.claim_amount.refresh()
		grid_row.grid_form.fields_dict.sanctioned_amount.refresh()
	}
})

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
	cur_frm.toggle_enable("posting_date", !doc.posting_date);
	cur_frm.toggle_enable("expense_date", (local_status == 'Travel Claim Draft' || in_list(user_roles, "HR User")));
	
	if (local_status == 'Travel Claim Draft' && !doc.expense_date){
		cur_frm.set_value("expense_date", dateutil.get_today());
	}
	
	if (!local_status || local_status == 'Travel Request Draft'){
		cur_frm.fields_dict['expenses'].grid.set_column_disp("other_expenses", false);
		cur_frm.fields_dict['expenses'].grid.set_column_disp("travel_advance", false);
		cur_frm.fields_dict['expenses'].grid.set_column_disp("section_break_4", false);
		cur_frm.fields_dict['expenses'].grid.set_column_disp("section_break_6", false);
	}
	
	if (in_list(user_roles, "HR User")){
		cur_frm.fields_dict['expenses'].grid.set_column_disp("other_expenses", true);
		cur_frm.fields_dict['expenses'].grid.set_column_disp("travel_advance", true);
		cur_frm.fields_dict['expenses'].grid.set_column_disp("section_break_4", true);
		cur_frm.fields_dict['expenses'].grid.set_column_disp("section_break_6", true);
	}
	
	if(!doc.__islocal) {
		cur_frm.toggle_enable("exp_approver", doc.approval_status=="Draft");
		//cur_frm.toggle_enable("approval_status", (doc.exp_approver==user && doc.docstatus==0));
		cur_frm.toggle_enable("approval_status", (doc.exp_approver==user && doc.approval_status=="Draft"));

		/*
		if (doc.docstatus==0 && doc.exp_approver==user && doc.approval_status=="Approved")
			 cur_frm.savesubmit();
		*/
		 
		if (doc.docstatus===1 && doc.approval_status=="Approved") {
			// Ver 1.0 Begins, added by SSK on 12/09/2016
			// Following code is commented
			
			if (cint(doc.total_amount_reimbursed) < cint(doc.total_sanctioned_amount) && frappe.model.can_create("Journal Entry")) {
				cur_frm.add_custom_button(__("Bank Entry"), cur_frm.cscript.make_bank_entry, __("Make"));
				cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
			}
			
			// Ver 1.0 Ends
			
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
	//console.log('calculate_total is called...');
	doc.total_claimed_amount = 0;
	doc.total_sanctioned_amount = 0;
	// Ver 1.0 Begins by SSK on 11/08/2016
	doc.total_advance_amount = 0;
	doc.net_claimed_amount = 0;
	// Ver 1.0 Ends by SSK on 11/08/2016
	$.each((doc.expenses || []), function(i, d) {
		doc.total_claimed_amount += (d.claim_amount ? d.claim_amount:0);
		if(d.sanctioned_amount==null) {
			d.sanctioned_amount = (d.claim_amount ? d.claim_amount:0);
		}
		doc.total_sanctioned_amount += d.sanctioned_amount;
		// Ver 1.0 Begins by SSK on 11/08/2016, following code added
		doc.total_advance_amount += (d.advance_total_amount ? d.advance_total_amount:0);
		doc.net_claimed_amount += (d.claim_amount ? d.claim_amount:0) - (d.advance_total_amount ? d.advance_total_amount:0);
		doc.total_sanctioned_amount -= (d.advance_total_amount ? d.advance_total_amount:0);
		// Ver 1.0 Ends by SSK on 11/08/2016
		//console.log('##########');
		//console.log('doc.total_claimed_amount : '+doc.total_claimed_amount);
		//console.log('doc.total_advance_amount : '+doc.total_advance_amount);
		//console.log('doc.net_claimed_amount : '+doc.net_claimed_amount);
		//console.log('doc.total_sanctioned_amount : '+doc.total_sanctioned_amount);
	});

	refresh_field("total_claimed_amount");
	refresh_field('total_sanctioned_amount');
	// Ver 1.0 Begins by SSK on 11/08/2016, following code added
	refresh_field('total_advance_amount');
	refresh_field('net_claimed_amount');
	// Ver 1.0 Ends by SSK on 11/08/2016
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

// Ver 1.0 Begins, added by SSK on 07/09/2016
// Following code is added
cur_frm.cscript.expense_date = function(frm, cdt, cdn){
	var val = frm.expenses || [];
	var max_date;
	
	for(var i = 0; i<val.length; i++){
		if (!max_date){
			max_date = val[i].to_date;
		}
		
		if (val[i].to_date > max_date) {
			max_date = val[i].to_date;
		}
	}
	
	if (local_status && local_status == 'Travel Claim Draft' && !frm.expense_date){
		msgprint(__("Expense Claim Date should be a valid date"));
	}
	else if (frm.expense_date < frm.posting_date){
		msgprint(__("Expense Claim Date cannot be before travel request date."));
	}
	else if (frm.expense_date < max_date){
		msgprint(__("Expense Claim Date should be on or after "+max_date));
	}
}
// Ver 1.0 Ends

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

frappe.ui.form.on("Expense Claim Detail", "expense_date", function(frm, cdt, cdn) {
	var child = locals[cdt][cdn];
	var from_date = new Date(child.expense_date);
	var to_date = new Date(child.to_date);
	
	frappe.model.set_value(cdt, cdn, "no_of_days", ((Math.ceil(Math.abs(to_date.getTime()-from_date.getTime()))/(3600*24*1000))+1));
	//if (local_status == 'Travel Claim Draft' || local_status == 'Travel Claim Approved by Supervisor'){
	calculate_claim(cdt, cdn);	
	//}
});

frappe.ui.form.on("Expense Claim Detail", "to_date", function(frm, cdt, cdn) {
	var child = locals[cdt][cdn];
	var from_date = new Date(child.expense_date);
	var to_date = new Date(child.to_date);
	
	frappe.model.set_value(cdt, cdn, "no_of_days", ((Math.ceil(Math.abs(to_date.getTime()-from_date.getTime()))/(3600*24*1000))+1));	
	//if (local_status == 'Travel Claim Draft' || local_status == 'Travel Claim Approved by Supervisor'){
	calculate_claim(cdt, cdn);	
	//}
});


frappe.ui.form.on("Expense Claim Detail", "dsa_rate_per_day", function(frm, cdt, cdn) {
	calculate_claim(cdt, cdn);	
});

frappe.ui.form.on("Expense Claim Detail", "currency", function(frm, cdt, cdn) {
	calculate_claim(cdt, cdn);
});

frappe.ui.form.on("Expense Claim Detail", "dsa_entitled", function(frm, cdt, cdn) {
	calculate_claim(cdt, cdn);
	//frappe.model.set_value(cdt, cdn, "claim_amount", frappe.utils.date_diff());
});

frappe.ui.form.on("Expense Claim Detail", "exchange_rate", function(frm, cdt, cdn) {
	calculate_claim(cdt, cdn);	
});

frappe.ui.form.on("Expense Claim Detail", "mileage", function(frm, cdt, cdn) {
	calculate_claim(cdt, cdn);	
});

frappe.ui.form.on("Expense Claim Detail", "mileage_rate2", function(frm, cdt, cdn) {
	calculate_claim(cdt, cdn);	
});

frappe.ui.form.on("Expense Claim Detail", "other_expense_amount", function(frm, cdt, cdn) {
	calculate_claim(cdt, cdn);	
});

frappe.ui.form.on("Expense Claim Detail", "other_expense_exchange_rate", function(frm, cdt, cdn) {
	calculate_claim(cdt, cdn);	
});

frappe.ui.form.on("Expense Claim Detail", "advance_amount", function(frm, cdt, cdn) {
	calculate_claim(cdt, cdn);	
	cur_frm.cscript.calculate_total(frm.doc, cdt, cdn);
});

frappe.ui.form.on("Expense Claim Detail", "advance_exchange_rate", function(frm, cdt, cdn) {
	calculate_claim(cdt, cdn);	
	cur_frm.cscript.calculate_total(frm.doc, cdt, cdn);
});


function calculate_claim(cdt, cdn){
	var child = locals[cdt][cdn];
	var dsa=0, mileage=0, other=0, advance=0;
	
	// DSA
	dsa = (child.no_of_days ? child.no_of_days:0)*(child.dsa_rate_per_day ? child.dsa_rate_per_day:0)*(child.dsa_entitled ? child.dsa_entitled:0)*0.01;
	frappe.model.set_value(cdt, cdn, "total_claim", dsa);
	
	// Mileage
	mileage = (child.mileage ? child.mileage:0)*(child.mileage_rate2 ? child.mileage_rate2:0);
	frappe.model.set_value(cdt, cdn, "mileage_total_amount", mileage);
	
	// Advance
	advance = (child.advance_amount ? child.advance_amount:0)*(child.advance_exchange_rate ? child.advance_exchange_rate:0);
	frappe.model.set_value(cdt, cdn, "advance_total_amount", advance);
	
	// Other Expense
	other = (child.other_expense_amount ? child.other_expense_amount:0)*(child.other_expense_exchange_rate ? child.other_expense_exchange_rate:0);
	frappe.model.set_value(cdt, cdn, "other_expense_total_amount", other);
	
	frappe.model.set_value(cdt, cdn, "claim_amount", (dsa*child.exchange_rate)+(mileage+other));
	frappe.model.set_value(cdt, cdn, "sanctioned_amount", child.claim_amount);
	refresh_field("claim_amount", child.name, child.parentfield);
	refresh_field("sanctioned_amount", child.name, child.parentfield);
}
