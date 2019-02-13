// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('company', 'default_letter_head', 'letter_head');

//++ Ver 20160803.1 Begins, added by SSK
var employee_pf, employer_pf=0, health_contribution=0, retirement_age=0, calc_gis_amt=0;
var counter=0;
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
			if (r.message){
				employee_pf = r.message[0][0];
				employer_pf = r.message[0][1];
				health_contribution = r.message[0][2];
				retirement_age = r.message[0][3];
			}
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
				if (r.message){
					calc_gis_amt = Math.round(r.message[0][0]);
				}
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
	},
	"lumpsum_temp_transfer_amount": function(frm) {
		calculate_others(frm.doc);
		calculate_totals(frm.doc);
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
				if (r.message){
					calc_gis_amt = Math.round(r.message[0][0]);
				}
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
	calculate_others(frm.doc);
	//-- Ver 20160804.1 Ends

	
	calculate_totals(doc);
}

/* Commented by SSK on 20160807 as the same validations done via form.on process in version 7.0

cur_frm.cscript.amount = function(doc, cdt, cdn){
	//++ Ver 20160804.1 Begins added by SSK
	calculate_others(frm.doc);
	//-- Ver 20160804.1 Ends
	
	calculate_totals(doc);
}
*/

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
	doc.net_pay = 0.0;
	if(doc.salary_slip_based_on_timesheet == 0){
		doc.net_pay = flt(total_earn) - flt(total_ded);
	}

	refresh_many(['total_earning', 'total_deduction', 'net_pay', 'amount']);
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
		//++ Ver 20160804.1 Begins added by SSK
		calculate_others(frm.doc);
		//-- Ver 20160804.1 Ends		
		calculate_totals(frm.doc);
		
		/* by SSK
		$.each((frm.doc.deductions || []), function(i, d){
			console.log(d.salary_component+': '+d.amount);
			refresh_field("amount");
		});
		*/
		//cur_frm.refresh();
	},
	
	earnings_remove: function(frm) {
		//++ Ver 20160804.1 Begins added by SSK
		calculate_others(frm.doc);
		//-- Ver 20160804.1 Ends
		calculate_totals(frm.doc);
		//++ Ver 20160804.1 Begins added by SSK		
		//cur_frm.refresh();
		//-- Ver 20160804.1 Ends						
	}, 
	
	deductions_remove: function(frm) {
		//++ Ver 20160804.1 Begins added by SSK
		calculate_others(frm.doc);
		//-- Ver 20160804.1 Ends
		calculate_totals(frm.doc);
		//++ Ver 20160804.1 Begins added by SSK		
		//cur_frm.refresh();
		//-- Ver 20160804.1 Ends						
	},
	
	total_deductible_amount: function(frm, cdt, cdn){
		d = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "total_outstanding_amount", parseFloat(d.total_deductible_amount || 0.0)-parseFloat(d.total_deducted_amount || 0.0));
    },
})

//++ Ver 20160803.1 Begins, calculate_totals2 is added by SSK on 03/08/2016
var calculate_others = function(doc, allowance_type="None", amt_flag="None"){
	var e_tbl = doc.earnings || [];
	var d_tbl = doc.deductions || [];
	var corp_all_id = -1, cont_all_id = -1, comm_all_id = -1, psa_all_id = -1, mpi_all_id = -1,
		off_all_id = -1, tran_all_id = -1, fuel_all_id = -1, ot_all_id = -1,
		corp_all_dn, cont_all_dn, comm_all_dn, psa_all_dn, mpi_all_dn,
		off_all_dn, tran_all_dn, fuel_all_dn, ot_all_dn,
		basic_all_id = -1, basic_all_dn;
	var pf_ded_id = -1, pf_ded_dn, health_ded_id = -1, health_ded_dn, tds_ded_id = -1, tds_ded_dn,
		gis_ded_id = -1, gis_ded_dn;
	
	for (var id in e_tbl){
		if (e_tbl[id].salary_component == "Corporate Allowance"){
			corp_all_id = id;
			corp_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "Contract Allowance"){
			cont_all_id = id;
			cont_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "Communication Allowance"){
			comm_all_id = id;
			comm_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "PSA"){
			psa_all_id = id;
			psa_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "MPI"){
			mpi_all_id = id;
			mpi_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "Officiating Allowance"){
			off_all_id = id;
			off_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "Temporary Transfer Allowance"){
			tran_all_id = id;
			tran_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "Fuel Allowance"){
			fuel_all_id = id;
			fuel_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "Overtime Allowance"){
			ot_all_id = id;
			ot_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "Basic Pay"){
			basic_all_id = id;
			basic_all_dn = e_tbl[id].name;
		}
	}
	
	// Calculating Allowances
	//if (allowance_type == "Corporate Allowance"){
		//console.log('Checkvalue: '+doc.eligible_for_corporate_allowance);
		if (doc.eligible_for_corporate_allowance==1){
			var calc_amt = 0;
			if (basic_all_id >= 0) {
				//if (amt_flag == "P"){
					calc_amt = (e_tbl[basic_all_id].amount*doc.ca*0.01);
				//}
				//else{
				//	calc_amt = doc.ca;
				//}
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (corp_all_id >= 0){
				if (e_tbl[corp_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", corp_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "Corporate Allowance";
				new_child.amount = calc_amt;	
				//cur_frm.refresh();
			}
		}
		else if (doc.eligible_for_corporate_allowance==0 && corp_all_id >= 0 && e_tbl[corp_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", corp_all_dn, "amount", 0);
		}
	//}
	//else if (allowance_type == "Contract Allowance"){
		if (doc.eligible_for_contract_allowance==1){
			var calc_amt = 0;
			if (basic_all_id >= 0) {
				//if (amt_flag == "P"){
					calc_amt = (e_tbl[basic_all_id].amount*doc.contract_allowance*0.01);
				//}
				//else{
				//	calc_amt = doc.contract_allowance;
				//}
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (cont_all_id >= 0){
				if (e_tbl[cont_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", cont_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "Contract Allowance";
				new_child.amount = calc_amt;				
				//cur_frm.refresh();
			}
		}
		else if(doc.eligible_for_contract_allowance==0 && cont_all_id >=0 && e_tbl[cont_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", cont_all_dn, "amount", 0);
		}
	//}
	//else if (allowance_type == "Communication Allowance"){
		if (doc.eligible_for_communication_allowance==1){
			var calc_amt = 0;
			//if (amt_flag == "P"){
			//	calc_amt = (e_tbl[basic_all_id].amount*doc.communication_allowance*0.01);
			//}
			//else{
				calc_amt = doc.communication_allowance;
			//}
			
			calc_amt = Math.round(calc_amt);
			
			if (comm_all_id >= 0){
				if (e_tbl[comm_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", comm_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "Communication Allowance";
				new_child.amount = calc_amt;				
				//cur_frm.refresh();
			}
		}
		else if(doc.eligible_for_communication_allowance==0 && comm_all_id >= 0 && e_tbl[comm_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", comm_all_dn, "amount", 0);
		}	
	//}
	//else if (allowance_type == "PSA"){
		if (doc.eligible_for_psa==1){
			if (basic_all_id >= 0) {
				//var calc_amt = 0;
				//if (amt_flag == "P"){
					calc_amt = (e_tbl[basic_all_id].amount*doc.psa*0.01);
				//}
				//else{
				//	calc_amt = doc.psa;
				//}
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (psa_all_id >= 0){
				if (e_tbl[psa_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", psa_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "PSA";
				new_child.amount = calc_amt;				
				//cur_frm.refresh();
			}
		}
		else if(doc.eligible_for_psa==0 && psa_all_id >= 0 && e_tbl[psa_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", psa_all_dn, "amount", 0);
		}		
	//}
	//else if (allowance_type == "MPI"){
		if (doc.eligible_for_mpi==1){
			var calc_amt = 0;
			if (basic_all_id >= 0) {
				//if (amt_flag == "P"){
					calc_amt = (e_tbl[basic_all_id].amount*doc.mpi*0.01);
				//}
				//else{
				//	calc_amt = doc.mpi;
				//}
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (mpi_all_id >= 0){
				if (e_tbl[mpi_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", mpi_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "MPI";
				new_child.amount = calc_amt;				
				//cur_frm.refresh();
			}
		}
		else if(doc.eligible_for_mpi==0 && mpi_all_id >= 0 && e_tbl[mpi_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", mpi_all_dn, "amount", 0);
		}			
	//}
	//else if (allowance_type == "Officiating Allowance"){
		if (doc.eligible_for_officiating_allowance==1){
			var calc_amt = 0;
			if (basic_all_id >= 0) {
				//if (amt_flag == "P"){
					calc_amt = (e_tbl[basic_all_id].amount*doc.officiating_allowance*0.01);
				//}
				//else{
				//	calc_amt = doc.officiating_allowance;
				//}
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (off_all_id >= 0){
				if (e_tbl[off_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", off_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "Officiating Allowance";
				new_child.amount = calc_amt;				
				//cur_frm.refresh();
			}
		}
		else if(doc.eligible_for_officiating_allowance==0 && off_all_id >= 0 && e_tbl[off_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", off_all_dn, "amount", 0);
		}				
	//}
	//else if (allowance_type == "Temporary Transfer Allowance"){	
		if (doc.eligible_for_temporary_transfer_allowance==1){
			var calc_amt = 0;
			if (basic_all_id >= 0) {
				//if (amt_flag == "P"){
					calc_amt = (e_tbl[basic_all_id].amount*doc.temporary_transfer_allowance*0.01);
				//}
				//else{
				//	calc_amt = doc.temporary_transfer_allowance;
				//}
			}
			
			calc_amt = Math.round(calc_amt);
			if(doc.lumpsum_temp_transfer_amount > 0) {
				calc_amt = doc.lumpsum_temp_transfer_amount
			}
			
			if (tran_all_id >= 0){
				if (e_tbl[tran_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", tran_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "Temporary Transfer Allowance";
				new_child.amount = calc_amt;				
				//cur_frm.refresh();
			}
		}
		else if(doc.eligible_for_temporary_transfer_allowance==0 && tran_all_id >=0 && e_tbl[tran_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", tran_all_dn, "amount", 0);
		}					
	//}
	//else if (allowance_type == "Fuel Allowance"){		
		if (doc.eligible_for_fuel_allowances==1){
			var calc_amt = 0;
			//if (amt_flag == "P"){
			//	calc_amt = (e_tbl[basic_all_id].amount*doc.fuel_allowances*0.01);
			//}
			//else{
				calc_amt = doc.fuel_allowances;
			//}
			
			calc_amt = Math.round(calc_amt);
			
			if (fuel_all_id >= 0){
				if (e_tbl[fuel_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", fuel_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "Fuel Allowance";
				new_child.amount = calc_amt;		
				//cur_frm.refresh();				
			}
		}
		else if(doc.eligible_for_fuel_allowances==0 && fuel_all_id >= 0 && e_tbl[fuel_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", fuel_all_dn, "amount", 0);
		}						
	//}	
	
	/*
	// Calculating Allowances
	if (allowance_type == "Corporate Allowance"){
		console.log('Checkvalue: '+doc.eligible_for_corporate_allowance);
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
				new_child.salary_component = allowance_type;
				new_child.amount = calc_amt;	
				//cur_frm.refresh();
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
				new_child.salary_component = allowance_type;
				new_child.amount = calc_amt;				
				//cur_frm.refresh();
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
				new_child.salary_component = allowance_type;
				new_child.amount = calc_amt;				
				//cur_frm.refresh();
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
				new_child.salary_component = allowance_type;
				new_child.amount = calc_amt;				
				//cur_frm.refresh();
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
				new_child.salary_component = allowance_type;
				new_child.amount = calc_amt;				
				//cur_frm.refresh();
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
				new_child.salary_component = allowance_type;
				new_child.amount = calc_amt;				
				//cur_frm.refresh();
			}
		}
		else{
			frappe.model.set_value("Salary Detail", off_all_dn, "amount", 0);
		}				
	}
	else if (allowance_type == "Temporary Transfer Allowance"){	
		if (doc.eligible_for_temporary_transfer_allowance){
			var calc_amt = 0;
			if (amt_flag == "P"){
				calc_amt = (e_tbl[basic_all_id].amount*doc.temporary_transfer_allowance*0.01);
			}
			else{
				calc_amt = doc.temporary_transfer_allowance;
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (tran_all_id >= 0){
				frappe.model.set_value("Salary Detail", tran_all_dn, "amount", calc_amt);				
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = allowance_type;
				new_child.amount = calc_amt;				
				//cur_frm.refresh();
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
				new_child.salary_component = allowance_type;
				new_child.amount = calc_amt;		
				//cur_frm.refresh();				
			}
		}
		else{
			frappe.model.set_value("Salary Detail", fuel_all_dn, "amount", 0);
		}						
	}*/
	
	// Calculating Deductions
	for (var id in d_tbl){
		if (d_tbl[id].salary_component == "PF"){
			pf_ded_id = id;
			pf_ded_dn = d_tbl[id].name;
		}
		else if(d_tbl[id].salary_component == "Salary Tax"){
			tds_ded_id = id;
			tds_ded_dn = d_tbl[id].name;			
		}
		else if(d_tbl[id].salary_component == "Health Contribution"){
			health_ded_id = id;
			health_ded_dn = d_tbl[id].name;			
		}
		else if(d_tbl[id].salary_component == "Group Insurance Scheme"){
			gis_ded_id = id;
			gis_ded_dn = d_tbl[id].name;			
		}		
	}

	// GIS
	var calc_gis_amt2 = 0;
	if (doc.eligible_for_gis){
		calc_gis_amt2 = calc_gis_amt;
		if (gis_ded_id >= 0){
			if (d_tbl[gis_ded_id].amount != calc_gis_amt2){
				frappe.model.set_value("Salary Detail", gis_ded_dn, "amount", calc_gis_amt2);				
			}
		} 
		else{
			if (calc_gis_amt > 0){
				var new_child = frappe.model.add_child(doc, "Salary Detail","deductions");
				new_child.salary_component = "Group Insurance Scheme";
				new_child.amount = calc_gis_amt2;	
				//cur_frm.refresh();
			}
		}						
	}
	else if(doc.eligible_for_gis==0 && gis_ded_id >= 0 && d_tbl[gis_ded_id].amount > 0){
			frappe.model.set_value("Salary Detail", gis_ded_dn, "amount", 0);
	}
		
	// PF
	var calc_pf_amt = 0;
	if (doc.eligible_for_pf){
		calc_pf_amt = Math.round(e_tbl[basic_all_id].amount*employee_pf*0.01);
		if (pf_ded_id >= 0){
			if (d_tbl[pf_ded_id].amount != calc_pf_amt){
				frappe.model.set_value("Salary Detail", pf_ded_dn, "amount", calc_pf_amt);				
			}
		} 
		else{
			if (calc_pf_amt > 0){
				var new_child = frappe.model.add_child(doc, "Salary Detail","deductions");
				new_child.salary_component = "PF";
				new_child.amount = calc_pf_amt;				
				//cur_frm.refresh();
			}
		}	
	}
	else if(doc.eligible_for_pf==0 && pf_ded_id >= 0 && d_tbl[pf_ded_id].amount > 0){
			frappe.model.set_value("Salary Detail", pf_ded_dn, "amount", 0);
	}
	
	// Health Contribution
	calculate_totals(doc);
	var calc_health_amt = 0;
	if (doc.eligible_for_health_contribution){
		calc_health_amt = Math.round(doc.total_earning*health_contribution*0.01);
		if (health_ded_id >= 0){
			if (d_tbl[health_ded_id].amount != calc_health_amt){
				frappe.model.set_value("Salary Detail", health_ded_dn, "amount", calc_health_amt);				
			}
		} 
		else{
			if (calc_health_amt > 0){
				var new_child = frappe.model.add_child(doc, "Salary Detail","deductions");
				new_child.salary_component = "Health Contribution";
				new_child.amount = calc_health_amt;				
				//cur_frm.refresh();
			}
		}		
	}
	else if(doc.eligible_for_health_contribution==0 && health_ded_id >= 0 && d_tbl[health_ded_id].amount > 0){
			frappe.model.set_value("Salary Detail", health_ded_dn, "amount", 0);
	}
	
	// Salary Tax
	var calc_tds_amt = 0;	
	calculate_totals(doc);
	cur_frm.call({
		method: "erpnext.hr.doctype.salary_structure.salary_structure.get_salary_tax",
		args: {
			"gross_amt": (doc.total_earning-calc_pf_amt-calc_gis_amt2),
		},
		callback: function(r){
			if (r.message){
				calc_tds_amt = Math.round(r.message);
			}
			else{
				calc_tds_amt = 0;
			}
			
			if (tds_ded_id >= 0){
				if (d_tbl[tds_ded_id].amount != calc_tds_amt){
					frappe.model.set_value("Salary Detail", tds_ded_dn, "amount", calc_tds_amt);				
				}
			} 
			else{
				if (calc_tds_amt > 0){
					var new_child = frappe.model.add_child(doc, "Salary Detail","deductions");
					new_child.salary_component = "Salary Tax";
					new_child.amount = calc_tds_amt;
					cur_frm.refresh();
				}
			}					
		}
	});	
	
	calculate_totals(doc);
}
//-- Ver 20160803.1 Ends

//++ Ver 20160804.1 Begins added by SSK

cur_frm.cscript.eligible_for_corporate_allowance = function(frm){
	calculate_others(frm, "Corporate Allowance", "P");
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_contract_allowance = function(frm){
	calculate_others(frm, "Contract Allowance", "P");
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_communication_allowance = function(frm){
	calculate_others(frm, "Communication Allowance", "A");
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_psa = function(frm){
	calculate_others(frm, "PSA", "P");
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_mpi = function(frm){
	calculate_others(frm, "MPI", "P");
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_officiating_allowance = function(frm){
	calculate_others(frm, "Officiating Allowance", "P");
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_temporary_transfer_allowance = function(frm){
	calculate_others(frm, "Temporary Transfer Allowance", "P");
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_fuel_allowances = function(frm){
	calculate_others(frm, "Fuel Allowance", "A");
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_gis = function(frm){
	calculate_others(frm, "GIS", "A");
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_pf = function(frm){
	calculate_others(frm, "GIS", "A");
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_health_contribution = function(frm){
	calculate_others(frm, "GIS", "A");
	cur_frm.refresh();
}
//
cur_frm.cscript.ca = function(frm){
	calculate_others(frm, "Corporate Allowance", "P");
}

cur_frm.cscript.contract_allowance = function(frm){
	calculate_others(frm, "Contract Allowance", "P");
}

cur_frm.cscript.communication_allowance = function(frm){
	calculate_others(frm, "Communication Allowance", "A");
}

cur_frm.cscript.psa = function(frm){
	calculate_others(frm, "PSA", "P");
}

cur_frm.cscript.mpi = function(frm){
	calculate_others(frm, "MPI", "P");
}

cur_frm.cscript.officiating_allowance = function(frm){
	calculate_others(frm, "Officiating Allowance", "P");
}

cur_frm.cscript.temporary_transfer_allowance = function(frm){
	calculate_others(frm, "Temporary Transfer Allowance", "P");
}

cur_frm.cscript.fuel_allowances = function(frm){
	calculate_others(frm, "Fuel Allowance", "A");
}

//++ Ver 20160804.1 Ends
