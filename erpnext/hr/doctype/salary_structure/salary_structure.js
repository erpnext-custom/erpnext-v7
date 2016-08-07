// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('company', 'default_letter_head', 'letter_head');

//++ Ver 20160803.1 Begins, added by SSK
var employee_pf, employer_pf=0, health_contribution=0, retirement_age=0, calc_gis_amt=0;
//-- Ver 20160803.1 Ends

cur_frm.cscript.onload = function(doc, dt, dn){
	e_tbl = doc.earnings || [];
	d_tbl = doc.deductions || [];
	
	//++ Ver 20160803.1 Begins added by SSK
	cur_frm.call({
		method: "erpnext.hr.doctype.salary_structure.salary_structure.get_company_pf",
		args: {
			fiscal_year: "",
		},
		callback: function(r){
			employee_pf = r.message[0][0];
			employer_pf = r.message[0][1];
			health_contribution = r.message[0][2];
			retirement_age = r.message[0][3];
		}
	});	
	
	// GIS
	if (doc.employee){
		cur_frm.call({
			method: "erpnext.hr.doctype.salary_structure.salary_structure.get_employee_gis",
			args: {
				"employee": doc.employee,
			},
			callback: function(r){	
				calc_gis_amt = Math.round(r.message[0][0]);
			}
		});	
	}
	//-- Ver 20160803.1 Ends
	
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
	if (doc.employee){
		//++ Ver 20160804.1 Begins added by SSK
		// GIS
		cur_frm.call({
			method: "erpnext.hr.doctype.salary_structure.salary_structure.get_employee_gis",
			args: {
				"employee": doc.employee,
			},
			callback: function(r){	
				calc_gis_amt = Math.round(r.message[0][0]);
			}
		});
		//-- Ver 20160804.1 Ends				
		return get_server_fields('get_employee_details','','',doc,dt,dn);
	}
}

cur_frm.cscript.modified_value = function(doc, cdt, cdn){
	//++ Ver 20160714.1 Begins added by SSK
	//var item = frappe.get_doc(cdt, cdn);
	//console.log(item.e_type);
	//-- Ver 20160714.1 Ends

	//++ Ver 20160804.1 Begins added by SSK
	calculate_others(doc, cdt, cdn);
	//-- Ver 20160804.1 Ends

	
	calculate_totals(doc);
}

cur_frm.cscript.amount = function(doc, cdt, cdn){
	//++ Ver 20160804.1 Begins added by SSK
	calculate_others(doc, cdt, cdn);
	//-- Ver 20160804.1 Ends
	
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

//++ Ver 20160803.1 Begins, calculate_totals2 is added by SSK on 03/08/2016
var calculate_others = function(doc, cdt, cdn, allowance_type="None", amt_flag="None"){
	var e_tbl = doc.earnings || [];
	var d_tbl = doc.deductions || [];
	var corp_all_id = -1, cont_all_id = -1, comm_all_id = -1, psa_all_id = -1, mpi_all_id = -1,
		off_all_id = -1, tran_all_id = -1, fuel_all_id = -1, ot_all_id = -1,
		corp_all_dn, cont_all_dn, comm_all_dn, psa_all_dn, mpi_all_dn,
		off_all_dn, tran_all_dn, fuel_all_dn, ot_all_dn,
		basic_all_id = -1, basic_all_dn;
	var pf_ded_id = -1, pf_ded_dn, health_ded_id = -1, health_ded_dn, tds_ded_id = -1, tds_ded_dn,
		gis_ded_id = -1, gis_ded_dn;
	
	
	// Saving IndexValue and DocumentName from Earnings child table
	for (var id in e_tbl){
		if (e_tbl[id].e_type == "Corporate Allowance"){
			corp_all_id = id;
			corp_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].e_type == "Contract Allowance"){
			cont_all_id = id;
			cont_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].e_type == "Communication Allowance"){
			comm_all_id = id;
			comm_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].e_type == "PSA"){
			psa_all_id = id;
			psa_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].e_type == "MPI"){
			mpi_all_id = id;
			mpi_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].e_type == "Officiating Allowance"){
			off_all_id = id;
			off_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].e_type == "Temporary Transfer Allowance"){
			tran_all_id = id;
			tran_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].e_type == "Fuel Allowance"){
			fuel_all_id = id;
			fuel_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].e_type == "Overtime Allowance"){
			ot_all_id = id;
			ot_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].e_type == "Basic Pay"){
			basic_all_id = id;
			basic_all_dn = e_tbl[id].name;
		}
	}
		
	// Calculating Allowances
	if (allowance_type == "Corporate Allowance"){
		if (doc.eligible_for_corporate_allowance){
			var calc_amt = 0;
			if (amt_flag == "P"){
				calc_amt = (e_tbl[basic_all_id].amount*doc.ca*0.01);
			}
			else{
				calc_amt = doc.ca;
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (corp_all_id >= 0){
				frappe.model.set_value("Salary Detail", corp_all_dn, "amount", calc_amt);				
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.e_type = allowance_type;
				new_child.amount = calc_amt;				
				cur_frm.refresh();
			}
		}
		else{
			frappe.model.set_value("Salary Detail", corp_all_dn, "amount", 0);
		}
	}
	else if (allowance_type == "Contract Allowance"){
		if (doc.eligible_for_contract_allowance){
			var calc_amt = 0;
			if (amt_flag == "P"){
				calc_amt = (e_tbl[basic_all_id].amount*doc.contract_allowance*0.01);
			}
			else{
				calc_amt = doc.contract_allowance;
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (cont_all_id >= 0){
				frappe.model.set_value("Salary Detail", cont_all_dn, "amount", calc_amt);				
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.e_type = allowance_type;
				new_child.amount = calc_amt;				
				cur_frm.refresh();
			}
		}
		else{
			frappe.model.set_value("Salary Detail", cont_all_dn, "amount", 0);
		}
	}
	else if (allowance_type == "Communication Allowance"){
		if (doc.eligible_for_communication_allowance){
			var calc_amt = 0;
			if (amt_flag == "P"){
				calc_amt = (e_tbl[basic_all_id].amount*doc.communication_allowance*0.01);
			}
			else{
				calc_amt = doc.communication_allowance;
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (comm_all_id >= 0){
				frappe.model.set_value("Salary Detail", comm_all_dn, "amount", calc_amt);				
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.e_type = allowance_type;
				new_child.amount = calc_amt;				
				cur_frm.refresh();
			}
		}
		else{
			frappe.model.set_value("Salary Detail", comm_all_dn, "amount", 0);
		}	
	}
	else if (allowance_type == "PSA"){
		if (doc.eligible_for_psa){
			var calc_amt = 0;
			if (amt_flag == "P"){
				calc_amt = (e_tbl[basic_all_id].amount*doc.psa*0.01);
			}
			else{
				calc_amt = doc.psa;
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (psa_all_id >= 0){
				frappe.model.set_value("Salary Detail", psa_all_dn, "amount", calc_amt);				
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.e_type = allowance_type;
				new_child.amount = calc_amt;				
				cur_frm.refresh();
			}
		}
		else{
			frappe.model.set_value("Salary Detail", psa_all_dn, "amount", 0);
		}		
	}
	else if (allowance_type == "MPI"){
		if (doc.eligible_for_mpi){
			var calc_amt = 0;
			if (amt_flag == "P"){
				calc_amt = (e_tbl[basic_all_id].amount*doc.mpi*0.01);
			}
			else{
				calc_amt = doc.mpi;
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (mpi_all_id >= 0){
				frappe.model.set_value("Salary Detail", mpi_all_dn, "amount", calc_amt);				
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.e_type = allowance_type;
				new_child.amount = calc_amt;				
				cur_frm.refresh();
			}
		}
		else{
			frappe.model.set_value("Salary Detail", mpi_all_dn, "amount", 0);
		}			
	}
	else if (allowance_type == "Officiating Allowance"){
		if (doc.eligible_for_officiating_allowance){
			var calc_amt = 0;
			if (amt_flag == "P"){
				calc_amt = (e_tbl[basic_all_id].amount*doc.officiating_allowance*0.01);
			}
			else{
				calc_amt = doc.officiating_allowance;
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (off_all_id >= 0){
				frappe.model.set_value("Salary Detail", off_all_dn, "amount", calc_amt);				
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.e_type = allowance_type;
				new_child.amount = calc_amt;				
				cur_frm.refresh();
			}
		}
		else{
			frappe.model.set_value("Salary Detail", off_all_dn, "amount", 0);
		}				
	}
	else if (allowance_type == "Temporary Transfer Allowance"){	
		if (doc.eligible_for_temporary_transfer_allowance){
			var calc_amt = 0;
			console.log('tran_all_id: '+tran_all_id);
			console.log('tran_all_dn: '+tran_all_dn);
			if (amt_flag == "P"){
				calc_amt = (e_tbl[basic_all_id].amount*doc.temporary_transfer_allowance*0.01);
			}
			else{
				calc_amt = doc.temporary_transfer_allowance;
			}
			
			calc_amt = Math.round(calc_amt);
			
			console.log("temp tran calc_amt: "+calc_amt);
			if (tran_all_id >= 0){
				frappe.model.set_value("Salary Detail", tran_all_dn, "amount", calc_amt);				
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.e_type = allowance_type;
				new_child.amount = calc_amt;				
				cur_frm.refresh();
			}
		}
		else{
			frappe.model.set_value("Salary Detail", tran_all_dn, "amount", 0);
		}					
	}
	else if (allowance_type == "Fuel Allowance"){		
		if (doc.eligible_for_fuel_allowances){
			var calc_amt = 0;
			if (amt_flag == "P"){
				calc_amt = (e_tbl[basic_all_id].amount*doc.fuel_allowances*0.01);
			}
			else{
				calc_amt = doc.fuel_allowances;
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (fuel_all_id >= 0){
				frappe.model.set_value("Salary Detail", fuel_all_dn, "amount", calc_amt);				
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.e_type = allowance_type;
				new_child.amount = calc_amt;				
				cur_frm.refresh();
			}
		}
		else{
			frappe.model.set_value("Salary Detail", fuel_all_dn, "amount", 0);
		}						
	}
	
	// Calculating Deductions
	for (var id in d_tbl){
		if (d_tbl[id].d_type == "PF"){
			pf_ded_id = id;
			pf_ded_dn = d_tbl[id].name;
		}
		else if(d_tbl[id].d_type == "Salary Tax"){
			tds_ded_id = id;
			tds_ded_dn = d_tbl[id].name;			
		}
		else if(d_tbl[id].d_type == "Health Contribution"){
			health_ded_id = id;
			health_ded_dn = d_tbl[id].name;			
		}
		else if(d_tbl[id].d_type == "Group Insurance Scheme"){
			gis_ded_id = id;
			gis_ded_dn = d_tbl[id].name;			
		}		
	}

	// GIS
	if (gis_ded_id >= 0){
		frappe.model.set_value("Salary Detail", gis_ded_dn, "amount", calc_gis_amt);				
	} 
	else{
		var new_child = frappe.model.add_child(doc, "Salary Detail","deductions");
		new_child.d_type = "Group Insurance Scheme";
		new_child.amount = calc_gis_amt;				
		//cur_frm.refresh();
	}						
	
	// PF
	var calc_pf_amt = 0;
	calc_pf_amt = Math.round(e_tbl[basic_all_id].amount*employee_pf*0.01);
	if (pf_ded_id >= 0){
		frappe.model.set_value("Salary Detail", pf_ded_dn, "amount", calc_pf_amt);				
	} 
	else{
		var new_child = frappe.model.add_child(doc, "Salary Detail","deductions");
		new_child.d_type = "PF";
		new_child.amount = calc_pf_amt;				
		//cur_frm.refresh();
	}	
	
	// Health Contribution
	calculate_totals(doc, cdt, cdn);
	var calc_health_amt = 0;
	calc_health_amt = Math.round(doc.total_earning*health_contribution*0.01);
	if (health_ded_id >= 0){
		frappe.model.set_value("Salary Detail", health_ded_dn, "amount", calc_health_amt);				
	} 
	else{
		var new_child = frappe.model.add_child(doc, "Salary Detail","deductions");
		new_child.d_type = "Health Contribution";
		new_child.amount = calc_health_amt;				
		//cur_frm.refresh();
	}		
	
	// Salary Tax
	var calc_tds_amt = 0;	
	calculate_totals(doc, cdt, cdn);
	cur_frm.call({
		method: "erpnext.hr.doctype.salary_structure.salary_structure.get_salary_tax",
		args: {
			"gross_amt": (doc.total_earning-calc_pf_amt-calc_gis_amt),
		},
		callback: function(r){	
			calc_tds_amt = Math.round(r.message[0][0]);
			
			if (tds_ded_id >= 0){
				frappe.model.set_value("Salary Detail", tds_ded_dn, "amount", calc_tds_amt);				
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","deductions");
				new_child.d_type = "Salary Tax";
				new_child.amount = calc_tds_amt;				
				//cur_frm.refresh();
			}					
		}
	});	
	
	cur_frm.refresh();
}
//-- Ver 20160803.1 Ends

//++ Ver 20160804.1 Begins added by SSK

cur_frm.cscript.eligible_for_corporate_allowance = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "Corporate Allowance", "P");
}

cur_frm.cscript.eligible_for_contract_allowance = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "Contract Allowance", "P");
}

cur_frm.cscript.eligible_for_communication_allowance = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "Communication Allowance", "A");
}

cur_frm.cscript.eligible_for_psa = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "PSA", "P");
}

cur_frm.cscript.eligible_for_mpi = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "MPI", "P");
}

cur_frm.cscript.eligible_for_officiating_allowance = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "Officiating Allowance", "P");
}

cur_frm.cscript.eligible_for_temporary_transfer_allowance = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "Temporary Transfer Allowance", "P");
}

cur_frm.cscript.eligible_for_fuel_allowances = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "Fuel Allowance", "A");
}

//
cur_frm.cscript.ca = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "Corporate Allowance", "P");
}

cur_frm.cscript.contract_allowance = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "Contract Allowance", "P");
}

cur_frm.cscript.communication_allowance = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "Communication Allowance", "A");
}

cur_frm.cscript.psa = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "PSA", "P");
}

cur_frm.cscript.mpi = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "MPI", "P");
}

cur_frm.cscript.officiating_allowance = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "Officiating Allowance", "P");
}

cur_frm.cscript.temporary_transfer_allowance = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "Temporary Transfer Allowance", "P");
}

cur_frm.cscript.fuel_allowances = function(doc, cdt, cdn){
	calculate_others(doc, cdt, cdn, "Fuel Allowance", "A");
}
//++ Ver 20160804.1 Ends