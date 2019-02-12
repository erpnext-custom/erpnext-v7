// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Revenue Target Adjustment', {
	setup: function(frm){
		frm.get_docfield("revenue_target_adjustment_account").allow_bulk_edit = 1;
		
		frm.get_field("revenue_target_adjustment_account").grid.editable_fields = [
			{fieldname: 'cost_center', columns: 2},
			{fieldname: 'account', columns: 2},
			{fieldname: 'account_code', columns: 2},
			{fieldname: 'target_amount', columns: 2},
			{fieldname: 'adjustment_amount', columns: 2}
		];
	},
	onload: function(frm){
		frm.fields_dict['revenue_target_adjustment_account'].grid.get_field('account').get_query = function(){
			return{
				filters: {
					'root_type': 'Income'
				}
			}
		}
	},
	refresh: function(frm) {
		frm.add_custom_button(__("Achievement Report"), function(){
				var fy = frappe.model.get_doc("Fiscal Year", frm.doc.fiscal_year);
				var y_start_date = y_end_date = "";
				
				if (fy){
					y_start_date = fy.year_start_date;
					y_end_date   = fy.year_end_date;
				}
				
				frappe.route_options = {
					fiscal_year: frm.doc.fiscal_year,
					from_date: y_start_date,
					to_date: y_end_date
				};
				frappe.set_route("query-report", "Revenue Target");
			}
		);
	},
	dummy_button: function(frm){
		
	}
});

frappe.ui.form.on('Revenue Target Adjustment Account',{
	target_amount: function(frm, cdt, cdn){
		update_total(frm, cdt, cdn);
	},
	
	adjustment_amount: function(frm, cdt, cdn){
		update_total(frm, cdt, cdn);
	},
	
	net_target_amount: function(frm){
		calculate_total(frm);
	},
	
	revenue_target_adjustment_account_remove: function(frm){
		calculate_total(frm);
	},
});

var update_total = function(frm, cdt, cdn){
	var child  = locals[cdt][cdn];
	var amount = 0.0;
	
	amount = parseFloat(child.target_amount || 0.0) + parseFloat(child.adjustment_amount || 0.0);
	frappe.model.set_value(cdt, cdn, "net_target_amount", parseFloat(amount || 0.0));
}

var calculate_total = function(frm, cdt, cdn){
	var list  = frm.doc.revenue_target_adjustment_account || [];
	var tot_target_amount = 0.0;
	var tot_adjustment_amount = 0.0;
	
	for(var i=0; i<list.length; i++){
		tot_target_amount     = parseFloat(tot_target_amount || 0.0) + parseFloat(list[i].target_amount || 0.0);
		tot_adjustment_amount = parseFloat(tot_adjustment_amount || 0.0) + parseFloat(list[i].adjustment_amount || 0.0);
	}
	
	cur_frm.set_value("tot_target_amount", parseFloat(tot_target_amount));
	cur_frm.set_value("tot_adjustment_amount", parseFloat(tot_adjustment_amount));
	cur_frm.set_value("tot_net_target_amount", parseFloat(tot_target_amount) + parseFloat(tot_adjustment_amount));
}