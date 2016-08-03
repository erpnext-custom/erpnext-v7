// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('company', 'default_letter_head', 'letter_head');


cur_frm.cscript.onload = function(doc, dt, dn){
	e_tbl = doc.earnings || [];
	d_tbl = doc.deductions || [];
	if (e_tbl.length == 0 && d_tbl.length == 0)
		return $c_obj(doc,'make_earn_ded_table','', function(r, rt) { refresh_many(['earnings', 'deductions']);});
}

cur_frm.cscript.refresh = function(doc, dt, dn){
	if((!doc.__islocal) && (doc.is_active == 'Yes') && cint(doc.salary_slip_based_on_timesheet == 0)){
		cur_frm.add_custom_button(__('Salary Slip'),
			cur_frm.cscript['Make Salary Slip'], __("Make"));
		cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
	}
}

frappe.ui.form.on('Salary Structure', {
	refresh: function(frm) {
		frm.trigger("toggle_fields")
		frm.fields_dict['earnings'].grid.set_column_disp("default_amount", false);
		frm.fields_dict['deductions'].grid.set_column_disp("default_amount", false);
	},

	salary_slip_based_on_timesheet: function(frm) {
		frm.trigger("toggle_fields")
	},

	toggle_fields: function(frm) {
		frm.toggle_display(['salary_component', 'hour_rate'], frm.doc.salary_slip_based_on_timesheet);
		frm.toggle_reqd(['salary_component', 'hour_rate'], frm.doc.salary_slip_based_on_timesheet);
	}
})

cur_frm.cscript['Make Salary Slip'] = function() {
	frappe.model.open_mapped_doc({
		method: "erpnext.hr.doctype.salary_structure.salary_structure.make_salary_slip",
		frm: cur_frm
	});
}

cur_frm.cscript.employee = function(doc, dt, dn){
	if (doc.employee)
		return get_server_fields('get_employee_details','','',doc,dt,dn);
}

cur_frm.cscript.modified_value = function(doc, cdt, cdn){
	//++ Ver 20160714.1 Begins added by SSK
	var item = frappe.get_doc(cdt, cdn);
	console.log(item.e_type);

	//-- Ver 20160714.1 Ends
	
	calculate_totals(doc);
}

cur_frm.cscript.amount = function(doc, cdt, cdn){
	calculate_totals(doc);
}

var calculate_totals = function(doc) {
	var tbl1 = doc.earnings || [];
	var tbl2 = doc.deductions || [];
	
	var total_earn = 0; var total_ded = 0;
	for(var i = 0; i < tbl1.length; i++){
		total_earn += flt(tbl1[i].amount);
	}
	for(var j = 0; j < tbl2.length; j++){
		total_ded += flt(tbl2[j].amount);
	}
	
	//++ Ver 20160714.1 Begins added by SSK
	
	//if (eligible_for_corporate_allowance){
	//	
	//}
	
	//-- Ver 20160714.1 Ends
	doc.total_earning = total_earn;
	doc.total_deduction = total_ded;
	doc.net_pay = 0.0
	if(doc.salary_slip_based_on_timesheet == 0){
		doc.net_pay = flt(total_earn) - flt(total_ded);
	}

	refresh_many(['total_earning', 'total_deduction', 'net_pay']);
}

cur_frm.cscript.validate = function(doc, cdt, cdn) {
	calculate_totals(doc);
	if(doc.employee && doc.is_active == "Yes") frappe.model.clear_doc("Employee", doc.employee);
}

cur_frm.fields_dict.employee.get_query = function(doc,cdt,cdn) {
	return{ query: "erpnext.controllers.queries.employee_query" }
}

//++ Ver 20160714.1 Begins added by SSK

cur_frm.cscript.eligible_for_corporate_allowance = function(doc, cdt, cdn){
	//console.log('Value Changed.');
	//console.log(doc.eligible_for_corporate_allowance);
	//console.log(doc.earnings.length);
	//console.log(doc.earnings);
	//console.log(doc.deductions.length);
	//console.log(doc.deductions);
	calculate_totals(doc);
}

cur_frm.cscript.eligibile_for_contract_allowance = function(doc, cdt, cdn){
	calculate_totals(doc);
}

cur_frm.cscript.eligibile_for_comunication_allowance = function(doc, cdt, cdn){
	calculate_totals(doc);
}

cur_frm.cscript.eligibile_for_psa = function(doc, cdt, cdn){
	calculate_totals(doc);
}

cur_frm.cscript.eligibile_for_mpi = function(doc, cdt, cdn){
	calculate_totals(doc);
}

cur_frm.cscript.eligible_for_officiating_allowance = function(doc, cdt, cdn){
	calculate_totals(doc);
}

cur_frm.cscript.eligible_for_temporary_transfer_allowance = function(doc, cdt, cdn){
	calculate_totals(doc);
}

cur_frm.cscript.eligible_for_fuel_allowances = function(doc, cdt, cdn){
	calculate_totals(doc);
}

cur_frm.cscript.eligible_for_fuel_allowances = function(doc, cdt, cdn){
	calculate_totals(doc);
}

//++ Ver 20160714.1 Ends

frappe.ui.form.on('Salary Detail', {
	amount: function(frm) {
		calculate_totals(frm.doc);
	},
	
	earnings_remove: function(frm) {
		calculate_totals(frm.doc);
	}, 
	
	deductions_remove: function(frm) {
		calculate_totals(frm.doc);
	}
})
