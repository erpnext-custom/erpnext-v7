// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project Invoice', {
	setup: function(frm){
		frm.get_field('project_invoice_boq').grid.editable_fields = [
			{fieldname: 'item', columns: 3},
			{fieldname: 'is_selected', columns: 1},
			{fieldname: 'uom', columns: 1},
			{fieldname: 'invoice_quantity', columns: 1},
			{fieldname: 'invoice_rate', columns: 2},
			{fieldname: 'invoice_amount', columns: 2}
		];		
	},

	onload: function(frm){
		calculate_totals(frm);
	},
	
	onload_post_render: function(frm){
		cur_frm.refresh();
	},
	
	refresh: function(frm, cdt, cdn) {
		//if(!frm.doc.__islocal){
				
			
		if(frm.doc.project){
			if(frappe.model.can_read("Project")) {
				frm.add_custom_button(__("Project"), function() {
					frappe.route_options = {"name": frm.doc.project}
					frappe.set_route("Form", "Project", frm.doc.project);
				}, __("View"), true);
			}						
		}

		if(frm.doc.boq){
			if(frappe.model.can_read("BOQ")) {
				frm.add_custom_button(__("BOQ"), function() {
					frappe.route_options = {"name": frm.doc.boq}
					frappe.set_route("Form", "BOQ", frm.doc.boq);
				}, __("View"), true);
			}					
		}
		
		if(frm.doc.docstatus===1){
			frm.add_custom_button(__('Accounting Ledger'), function(){
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.invoice_date,
					to_date: frm.doc_invoice_date,
					company: frm.doc.company,
					group_by_voucher: false
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
			
			if(frappe.model.can_read("Project Payment") && parseFloat(frm.doc.total_balance_amount) > 0){
				frm.add_custom_button(__("Payment"), function(){
					frm.trigger("make_project_payment")},
					__("Make"), "icon-file-alt");
			}
		}
		
		if(frm.doc.boq_type=="Item Based"){
			frm.fields_dict.project_invoice_boq.grid.toggle_enable("invoice_quantity", true);
			frm.fields_dict.project_invoice_boq.grid.toggle_enable("invoice_amount", false);
			//frm.fields_dict.project_invoice_boq.grid.set_column_disp("invoice_quantity", true);			
		} 
		else if(frm.doc.boq_type=="Milestone Based"){
			frm.fields_dict.project_invoice_boq.grid.toggle_enable("invoice_quantity", false);
			frm.fields_dict.project_invoice_boq.grid.toggle_enable("invoice_amount", true);
		}
		else if(frm.doc.boq_type=="Piece Rate Work Based(PRW)"){
			frm.fields_dict.project_invoice_boq.grid.toggle_enable("invoice_quantity", true);
			frm.fields_dict.project_invoice_boq.grid.toggle_enable("invoice_amount", false);
		}		
	},

	make_project_payment: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.accounts.doctype.project_payment.project_payment.make_project_payment",
			frm: frm
		});
	},
	
	price_adjustment_amount: function(frm){
		calculate_totals(frm);
	},
	
	advance_recovery: function(frm){
		calculate_totals(frm);
	},
	
	tds_amount: function(frm){
		calculate_totals(frm);
	},
	
	check_all: function(frm){
		check_uncheck_all(frm);
	}
});

frappe.ui.form.on("Project Invoice BOQ",{
	invoice_quantity: function(frm, cdt, cdn){
		child = locals[cdt][cdn];
		
		if(child.invoice_quantity > child.act_quantity){
			msgprint(__("Invoice Quantity cannot be greater than balance quantity.").format(child.invoice_quantity))
		}
		
		//if(child.invoice_quantity && child.invoice_rate){
		frappe.model.set_value(cdt, cdn, 'invoice_amount', (parseFloat(child.invoice_quantity)*parseFloat(child.invoice_rate)).toFixed(2));
		//}
	},
	invoice_amount: function(frm, cdt, cdn){
		child = locals[cdt][cdn];
		
		if(child.invoice_amount > child.act_amount){
			msgprint(__("Invoice Amount cannot be greater than balance amount."));
		}
		calculate_totals(frm);
	},
	is_selected: function(frm, cdt, cdn){
		calculate_totals(frm);
	},
});

/*
frappe.ui.form.on("Project Invoice","onload",function(frm,cdt,cdn){
	console.log("loader1");
	var df = frappe.meta.get_docfield("Project Invoice BOQ", "invoice_quantity", cur_frm.doc.name);
	
	if(frm.doc.boq_type=="Item Based"){
		df.read_only = 0;
	} 
	else if(frm.doc.boq_type=="Milestone Based"){
		df.read_only = 1;
	}
	else if(frm.doc.boq_type=="Piece Rate Work Based(PRW)"){
		df.read_only = 0;
	}
	cur_frm.refresh();
});
*/

/*
frappe.ui.form.on("Project Invoice BOQ", "invoice_amount", function(frm, cdt, cdn){
	console.log("cdt: "+cdt);
	console.log("cdn: "+cdn);
	console.log(cur_frm.fields_dict["project_invoice_boq"].grid);

	frappe.utils.filter_dict(cur_frm.fields_dict["project_invoice_boq"].grid.grid_rows_by_docname[cdn].docfields, {"fieldname": "invoice_quantity"})[0].read_only = true;
	frappe.utils.filter_dict(cur_frm.fields_dict["project_invoice_boq"].grid.grid_rows_by_docname[cdn].docfields, {"fieldname": "invoice_amount"})[0].read_only = true;
	cur_frm.fields_dict["project_invoice_boq"].grid.grid_rows_by_docname[cdn].fields_dict["invoice_quantity"].refresh();
	cur_frm.fields_dict["project_invoice_boq"].grid.grid_rows_by_docname[cdn].fields_dict["invoice_amount"].refresh();
});
*/

var calculate_totals = function(frm){
	var pi = frm.doc.project_invoice_boq || [];
	var gross_invoice_amount = 0.0, net_invoice_amount =0.0;
	
	for(var i=0; i<pi.length; i++){
		if(pi[i].invoice_amount && pi[i].is_selected==1){
			gross_invoice_amount += parseFloat(pi[i].invoice_amount);
		}
	}
	net_invoice_amount = (parseFloat(gross_invoice_amount)+parseFloat(frm.doc.price_adjustment_amount)-parseFloat(frm.doc.advance_recovery)-parseFloat(frm.doc.tds_amount));
	cur_frm.set_value("gross_invoice_amount",(gross_invoice_amount));
	cur_frm.set_value("net_invoice_amount",(net_invoice_amount));
	cur_frm.set_value("total_balance_amount",(parseFloat(frm.doc.net_invoice_amount || 0)-parseFloat(frm.doc.total_received_amount || 0)));
}

var check_uncheck_all = function(frm){
	var pib =frm.doc.project_invoice_boq || [];

	for(var id in pib){
		frappe.model.set_value("Project Invoice BOQ", pib[id].name, "is_selected", frm.doc.check_all);
	}
}