// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
/*
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
2.0		          SHIV		                        27/02/2018         Dynamic get_query added for Salary_Components under
																			tables `earnings` and `deductions`
--------------------------------------------------------------------------------------------------------------------------                                                                          
*/

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
		method: "erpnext.hr.hr_custom_functions.get_company_pf",
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
			method: "erpnext.hr.hr_custom_functions.get_employee_gis",
			args: {
				"employee": doc.employee,
			},
			callback: function(r){	
				if (r.message){
					//calc_gis_amt = Math.round(r.message[0][0]);
					calc_gis_amt = Math.round(r.message);
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
		method: "erpnext.hr.hr_custom_functions.make_salary_slip",
		frm: cur_frm
	});
}

cur_frm.cscript.employee = function(doc, dt, dn){
	console.log('employee');
	if (doc.employee){
		//++ Ver 20160804.1 Begins added by SSK
		// GIS
		cur_frm.call({
			method: "erpnext.hr.hr_custom_functions.get_employee_gis",
			args: {
				"employee": doc.employee,
			},
			callback: function(r){
				if (r.message){
					calc_gis_amt = Math.round(parseFloat(r.message));
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
	amount: function(frm, cdt, cdn) {
                d = locals[cdt][cdn]
                if (d.salary_component == "Basic Pay") {
                        frappe.model.set_value(cdt, cdn, "amount", Math.round(d.amount))
                }
		//++ Ver 20160804.1 Begins added by SSK
		calculate_others(frm.doc);
		//-- Ver 20160804.1 Ends		
		calculate_totals(frm.doc);
		//cur_frm.refresh();
	},
	
	earnings_remove: function(frm) {
		//++ Ver 20160804.1 Begins added by SSK
		calculate_others(frm.doc);
		//-- Ver 20160804.1 Ends
		calculate_totals(frm.doc);
	}, 
	
	deductions_remove: function(frm) {
		//++ Ver 20160804.1 Begins added by SSK
		calculate_others(frm.doc);
		//-- Ver 20160804.1 Ends
		calculate_totals(frm.doc);
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
		off_all_id = -1, tran_all_id = -1, fuel_all_id = -1, ot_all_id = -1, pda_all_id = -1,
		shift_all_id = -1, ug_all_id = -1, dep_all_id = -1, scar_all_id = -1, diff_all_id = -1,
		hia_all_id = -1, cash_all_id = -1, scar_all_dn, diff_all_dn, hia_all_dn, cash_all_dn,
		corp_all_dn, cont_all_dn, comm_all_dn, psa_all_dn, mpi_all_dn,
		off_all_dn, tran_all_dn, fuel_all_dn, ot_all_dn,
		basic_all_id = -1, basic_all_dn, pda_all_dn, shift_all_dn, ug_all_dn, dep_all_dn;
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
		else if (e_tbl[id].salary_component == "Shift Allowance"){
			shift_all_id = id;
			shift_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "PDA"){
			pda_all_id = id;
			pda_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "Deputation Allowance"){
			dep_all_id = id;
			dep_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "Underground Allowance"){
			ug_all_id = id;
			ug_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "Difficult Area Allowance"){
			diff_all_id = id;
			diff_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "Cash Handling Allowance"){
			cash_all_id = id;
			cash_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "High Altitude Allowance"){
			hia_all_id = id;
			hia_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "Scarcity Allowance"){
			scar_all_id = id;
			scar_all_dn = e_tbl[id].name;
		}
		else if (e_tbl[id].salary_component == "Basic Pay"){
			basic_all_id = id;
			basic_all_dn = e_tbl[id].name;
		}
	}
	
	// Calculating Allowances
		if (doc.eligible_for_corporate_allowance==1){
			var calc_amt = 0;
			if (basic_all_id >= 0) {
				calc_amt = (e_tbl[basic_all_id].amount*doc.ca*0.01);
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
			}
		}
		else if (doc.eligible_for_corporate_allowance==0 && corp_all_id >= 0 && e_tbl[corp_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", corp_all_dn, "amount", 0);
		}

		//PDA
		if (doc.eligible_for_pda==1){
			var calc_amt = 0;
			if (basic_all_id >= 0) {
				calc_amt = (e_tbl[basic_all_id].amount*doc.pda*0.01);
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (pda_all_id >= 0){
				if (e_tbl[pda_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", pda_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "PDA";
				new_child.amount = calc_amt;				
			}
		}
		else if(doc.eligible_for_pda==0 && pda_all_id >=0 && e_tbl[pda_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", pda_all_dn, "amount", 0);
		}
		//Scarcity
		if (doc.eligible_for_scarcity==1){
			var calc_amt = 0;
			if (basic_all_id >= 0) {
				calc_amt = (e_tbl[basic_all_id].amount*doc.scarcity*0.01);
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (scar_all_id >= 0){
				if (e_tbl[scar_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", scar_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "Scarcity Allowance";
				new_child.amount = calc_amt;				
			}
		}
		else if(doc.eligible_for_scarcity==0 && scar_all_id >=0 && e_tbl[scar_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", scar_all_dn, "amount", 0);
		}
		//High Altitude
		if (doc.eligible_for_high_altitude==1){
			var calc_amt = 0;
			if (basic_all_id >= 0) {
				calc_amt = doc.high_altitude;
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (hia_all_id >= 0){
				if (e_tbl[hia_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", hia_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "High Altitude Allowance";
				new_child.amount = calc_amt;				
			}
		}
		else if(doc.eligible_for_high_altitude==0 && hia_all_id >=0 && e_tbl[hia_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", hia_all_dn, "amount", 0);
		}
		//Difficult Area
		if (doc.eligible_for_difficulty==1){
			var calc_amt = 0;
			if (basic_all_id >= 0) {
				calc_amt = doc.difficulty //(e_tbl[basic_all_id].amount*doc.pda*0.01);
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (diff_all_id >= 0){
				if (e_tbl[diff_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", diff_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "Difficult Area Allowance";
				new_child.amount = calc_amt;				
			}
		}
		else if(doc.eligible_for_difficulty==0 && diff_all_id >=0 && e_tbl[diff_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", diff_all_dn, "amount", 0);
		}
		//Cash Handling
		if (doc.eligible_for_cash_handling==1){
			var calc_amt = 0;
			if (basic_all_id >= 0) {
				calc_amt = doc.cash_handling //(e_tbl[basic_all_id].amount*doc.pda*0.01);
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (cash_all_id >= 0){
				if (e_tbl[cash_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", cash_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "Cash Handling Allowance";
				new_child.amount = calc_amt;				
			}
		}
		else if(doc.eligible_for_cash_handling==0 && cash_all_id >=0 && e_tbl[cash_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", cash_all_dn, "amount", 0);
		}
		//Shift Allowance
		if (doc.eligible_for_shift==1){
			var calc_amt = 0;
			if (basic_all_id >= 0) {
				calc_amt = (e_tbl[basic_all_id].amount*doc.shift*0.01);
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (shift_all_id >= 0){
				if (e_tbl[shift_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", shift_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "Shift Allowance";
				new_child.amount = calc_amt;				
				//cur_frm.refresh();
			}
		}
		else if(doc.eligible_for_shift==0 && shift_all_id >=0 && e_tbl[shift_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", shift_all_dn, "amount", 0);
			//console.log(shift_all_dn)
			//frappe.model.remove("Salary Detail", shift_all_dn);
		}
		//Deputation Allowance
		if (doc.eligible_for_deputation==1){
			var calc_amt = 0;
			if (basic_all_id >= 0) {
				calc_amt = (e_tbl[basic_all_id].amount*doc.deputation*0.01);
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (dep_all_id >= 0){
				if (e_tbl[dep_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", dep_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "Deputation Allowance";
				new_child.amount = calc_amt;				
				//cur_frm.refresh();
			}
		}
		else if(doc.eligible_for_deputation==0 && dep_all_id >=0 && e_tbl[dep_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", dep_all_dn, "amount", 0);
		}
		//Underground Allowance
		if (doc.eligible_for_underground==1){
			var calc_amt = 0;
			if (basic_all_id >= 0) {
				calc_amt = (e_tbl[basic_all_id].amount*doc.underground*0.01);
			}
			
			calc_amt = Math.round(calc_amt);
			
			if (ug_all_id >= 0){
				if (e_tbl[ug_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", ug_all_dn, "amount", calc_amt);				
				}
			} 
			else{
				var new_child = frappe.model.add_child(doc, "Salary Detail","earnings");
				new_child.salary_component = "Underground Allowance";
				new_child.amount = calc_amt;				
				//cur_frm.refresh();
			}
		}
		else if(doc.eligible_for_underground==0 && ug_all_id >=0 && e_tbl[ug_all_id].amount > 0){
			frappe.model.set_value("Salary Detail", ug_all_dn, "amount", 0);
		}
		//"Contract Allowance"){
		if (doc.eligible_for_contract_allowance==1){
			var calc_amt = 0;
			if (basic_all_id >= 0) {
				calc_amt = (e_tbl[basic_all_id].amount*doc.contract_allowance*0.01);
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
				calc_amt = doc.communication_allowance;
			
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
				calc_amt = (e_tbl[basic_all_id].amount*doc.psa*0.01);
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
				calc_amt = (e_tbl[basic_all_id].amount*doc.mpi*0.01);
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
				calc_amt = (e_tbl[basic_all_id].amount*doc.officiating_allowance*0.01);
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
				calc_amt = (e_tbl[basic_all_id].amount*doc.temporary_transfer_allowance*0.01);
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
			calc_amt = doc.fuel_allowances;
			
			calc_amt = Math.round(calc_amt);
			
			if (fuel_all_id >= 0){
				if (e_tbl[fuel_all_id].amount != calc_amt){
					frappe.model.set_value("Salary Detail", fuel_all_dn, "amount", calc_amt);						   }
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
				cur_frm.refresh();
			}
		}		
	}
	else if(doc.eligible_for_health_contribution==0 && health_ded_id >= 0 && d_tbl[health_ded_id].amount > 0){
			frappe.model.set_value("Salary Detail", health_ded_dn, "amount", 0);
	}
	
	// Salary Tax
	var calc_tds_amt, gross = 0;	
	calculate_totals(doc);
	if(doc.eligible_for_communication_allowance == 1) {
		gross = (doc.total_earning-calc_pf_amt-calc_gis_amt2-(0.5 * doc.communication_allowance))
	}
	else {
		gross = (doc.total_earning-calc_pf_amt-calc_gis_amt2)
	}
	cur_frm.call({
		method: "erpnext.hr.hr_custom_functions.get_salary_tax",
		args: {
			"gross_amt": gross
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
					var tax_done = 0
					cur_frm.doc.deductions.forEach(function(d) { 
						if(d.salary_component == "Salary Tax") {
							tax_done = 1
						}
					})
					if (tax_done == 0) {
						var new_child = frappe.model.add_child(doc, "Salary Detail","deductions");
						new_child.salary_component = "Salary Tax";
						new_child.amount = calc_tds_amt;
						cur_frm.refresh();
					}
				}
			}					
		}
	});	
	
	calculate_totals(doc);
}
//-- Ver 20160803.1 Ends

//++ Ver 20160804.1 Begins added by SSK

cur_frm.cscript.eligible_for_corporate_allowance = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_contract_allowance = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_communication_allowance = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_psa = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_mpi = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_officiating_allowance = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_temporary_transfer_allowance = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_fuel_allowances = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_gis = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_pda = function(frm){
	calculate_others(frm);
	cur_frm.refresh()
}

cur_frm.cscript.eligible_for_shift = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_underground = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_deputation = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_pf = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_health_contribution = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}

cur_frm.cscript.eligible_for_difficulty = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}
cur_frm.cscript.eligible_for_high_altitude = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}
cur_frm.cscript.eligible_for_scarcity = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}
cur_frm.cscript.eligible_for_cash_handling = function(frm){
	calculate_others(frm);
	cur_frm.refresh();
}
//
cur_frm.cscript.ca = function(frm){
	calculate_others(frm);
}

cur_frm.cscript.contract_allowance = function(frm){
	calculate_others(frm);
}

cur_frm.cscript.communication_allowance = function(frm){
	calculate_others(frm);
}

cur_frm.cscript.psa = function(frm){
	calculate_others(frm);
}

cur_frm.cscript.mpi = function(frm){
	calculate_others(frm);
}

cur_frm.cscript.officiating_allowance = function(frm){
	calculate_others(frm);
}

cur_frm.cscript.temporary_transfer_allowance = function(frm){
	calculate_others(frm);
}

cur_frm.cscript.fuel_allowances = function(frm){
	calculate_others(frm);
}

cur_frm.cscript.pda = function(frm){
	calculate_others(frm);
}

cur_frm.cscript.shift = function(frm){
	calculate_others(frm);
}

cur_frm.cscript.deputation = function(frm){
	calculate_others(frm);
}

cur_frm.cscript.underground = function(frm){
	calculate_others(frm);
}

cur_frm.cscript.difficulty = function(frm){
	calculate_others(frm);
}
cur_frm.cscript.high_altitude = function(frm){
	calculate_others(frm);
}
cur_frm.cscript.scarcity = function(frm){
	calculate_others(frm);
}
cur_frm.cscript.cash_handling = function(frm){
	calculate_others(frm);
}
//++ Ver 20160804.1 Ends

// ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
// Following code added by SHIV on 2018/02/27
frappe.ui.form.on("Salary Structure", "refresh", function(frm) {
    frm.fields_dict['earnings'].grid.get_field('salary_component').get_query = function(doc, cdt, cdn) {
        doc = locals[cdt][cdn]
        return {
            "query": "erpnext.hr.doctype.salary_structure.salary_structure.salary_component_query",
            filters: {'parentfield': 'earnings'}
        }
    };
});

frappe.ui.form.on("Salary Structure", "refresh", function(frm) {
    frm.fields_dict['deductions'].grid.get_field('salary_component').get_query = function(doc, cdt, cdn) {
        doc = locals[cdt][cdn]
        return {
            "query": "erpnext.hr.doctype.salary_structure.salary_structure.salary_component_query",
            filters: {'parentfield': 'deductions'}
        }
    };
});
// +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++
