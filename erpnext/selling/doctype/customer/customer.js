// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on("Customer", {
	before_load: function(frm) {
		frappe.setup_language_field(frm);
	},
	refresh: function(frm) {
		if(frappe.defaults.get_default("cust_master_name")!="Naming Series") {
			frm.toggle_display("naming_series", false);
		} else {
			erpnext.toggle_naming_series();
		}

		frm.toggle_display(['address_html','contact_html'], !frm.doc.__islocal);

		if(!frm.doc.__islocal) {
			erpnext.utils.render_address_and_contact(frm);
		} else {
			erpnext.utils.clear_address_and_contact(frm);
		}

		var grid = cur_frm.get_field("sales_team").grid;
		grid.set_column_disp("allocated_amount", false);
		grid.set_column_disp("incentives", false);
		apply_customer_group_validations(frm);
	},
	validate: function(frm) {
		if(frm.doc.lead_name) frappe.model.clear_doc("Lead", frm.doc.lead_name);
	},

	customer_group: function(frm) {
		apply_customer_group_validations(frm);
	},
	inter_company: (frm)=>{
		frm.toggle_reqd('company_code',frm.doc.inter_company);
		if (!frm.doc.inter_company){
			frm.set_value('company_code','')
			frm.set_value('company_name','')
		}
	},
	// for consolidation purpose
	inter_company: (frm)=>{
		frm.toggle_reqd('company_code',frm.doc.inter_company);
		if (!frm.doc.inter_company){
			frm.set_value('company_code','')
			frm.set_value('company_name','')
		}
	},
});


apply_customer_group_validations = function(frm){
	//cur_frm.toggle_display(["customer_id","license_no","reference_no"], 0);
	if(frm.doc.customer_group){
		frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Customer Group',
				filters: {
					'name': frm.doc.customer_group
				},
				fieldname: '*'
			},
			callback: function(r){
				if(r.message){
					cur_frm.toggle_reqd(["customer_id","license_no","reference_no"], 0);

					if(r.message.document_type == "Citizenship ID"){
						cur_frm.toggle_display("customer_id", 1);
						cur_frm.toggle_reqd("customer_id", 1);
					}else if(r.message.document_type == "License Number"){
						cur_frm.toggle_display("license_no", 1);
						cur_frm.toggle_reqd("license_no", 1);
					}else if(r.message.document_type == "Reference Number"){
						cur_frm.toggle_display("reference_no", 1);
						cur_frm.toggle_reqd("reference_no", 1);
					}else if(r.message.document_type == "License/Reference Number"){
						cur_frm.toggle_display(["license_no","reference_no"], 1);
					}
				}
			}
		});
	}
}

cur_frm.cscript.onload = function(doc, dt, dn) {
	cur_frm.cscript.load_defaults(doc, dt, dn);
}

cur_frm.cscript.load_defaults = function(doc, dt, dn) {
	doc = locals[doc.doctype][doc.name];
	if(!(doc.__islocal && doc.lead_name)) { return; }

	var fields_to_refresh = frappe.model.set_default_values(doc);
	if(fields_to_refresh) { refresh_many(fields_to_refresh); }
}

cur_frm.add_fetch('lead_name', 'company_name', 'customer_name');
cur_frm.add_fetch('default_sales_partner','commission_rate','default_commission_rate');

cur_frm.fields_dict['customer_group'].get_query = function(doc, dt, dn) {
	return{
		filters:{'is_group': 0}
	}
}

cur_frm.fields_dict.lead_name.get_query = function(doc, cdt, cdn) {
	return{
		query: "erpnext.controllers.queries.lead_query"
	}
}

cur_frm.fields_dict['default_price_list'].get_query = function(doc, cdt, cdn) {
	return{
		filters:{'selling': 1}
	}
}

cur_frm.fields_dict['accounts'].grid.get_field('account').get_query = function(doc, cdt, cdn) {
	var d  = locals[cdt][cdn];
	var filters = {
		'account_type': 'Receivable',
		'company': d.company,
		"is_group": 0
	};

	if(doc.party_account_currency) {
		$.extend(filters, {"account_currency": doc.party_account_currency});
	}

	return {
		filters: filters
	}
}
