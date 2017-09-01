// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
/*
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  		 SSK		                        26/08/2016         Auto calculations when amount in child changed
1.0				 SSK								30/08/2016		   Modified Auto-calculations
1.0              SSK                                12/09/2016         Modified Auto-calculations
--------------------------------------------------------------------------------------------------------------------------                                                                          
*/
var employee_pf, employer_pf=0, health_contribution=0, retirement_age=0, calc_gis_amt=0;

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('time_sheet', 'total_hours', 'working_hours');

frappe.ui.form.on("Salary Slip", {
	setup: function(frm) {
		frm.fields_dict["timesheets"].grid.get_field("time_sheet").get_query = function(){
			return {
				filters: {
					employee: frm.doc.employee
				}
			}
		}
	},

	company: function(frm) {
		var company = locals[':Company'][frm.doc.company];
		if(!frm.doc.letter_head && company.default_letter_head) {
			frm.set_value('letter_head', company.default_letter_head);
		}
	},
	
	refresh: function(frm) {
		frm.trigger("toggle_fields")
		frm.fields_dict['earnings'].grid.set_column_disp("default_amount", false);
		frm.fields_dict['deductions'].grid.set_column_disp("default_amount", false);
		frm.fields_dict['earnings'].grid.set_column_disp("section_break_5", false);
		frm.fields_dict['deductions'].grid.set_column_disp("section_break_5", false);
	},

	salary_slip_based_on_timesheet: function(frm) {
		frm.trigger("toggle_fields")
	},

	toggle_fields: function(frm) {
		frm.toggle_display(['start_date', 'end_date', 'hourly_wages', 'timesheets'],
			cint(frm.doc.salary_slip_based_on_timesheet)==1);
		frm.toggle_display(['fiscal_year', 'month', 'total_days_in_month', 'leave_without_pay', 'payment_days'],
			cint(frm.doc.salary_slip_based_on_timesheet)==0);
	}
})


frappe.ui.form.on("Salary Slip Timesheet", {
	time_sheet: function(frm, cdt, cdn) {
		doc = frm.doc;
		cur_frm.cscript.fiscal_year(doc, cdt, cdn)
	}
})


// On load
// -------------------------------------------------------------------
cur_frm.cscript.onload = function(doc,dt,dn){
	if((cint(doc.__islocal) == 1) && !doc.amended_from){
		if(!doc.month) {
			var today=new Date();
			month = (today.getMonth()+01).toString();
			if(month.length>1) doc.month = month;
			else doc.month = '0'+month;
		}
		if(!doc.fiscal_year) doc.fiscal_year = sys_defaults['fiscal_year'];
		refresh_many(['month', 'fiscal_year']);
	}
}

// Get leave details
//---------------------------------------------------------------------
cur_frm.cscript.fiscal_year = function(doc,dt,dn){
		return $c_obj(doc, 'get_emp_and_leave_details','',function(r, rt) {
			var doc = locals[dt][dn];
			cur_frm.refresh();
			calculate_all(doc, dt, dn);
		});
}

cur_frm.cscript.month = cur_frm.cscript.salary_slip_based_on_timesheet = cur_frm.cscript.fiscal_year;
cur_frm.cscript.start_date = cur_frm.cscript.end_date = cur_frm.cscript.fiscal_year;

cur_frm.cscript.employee = function(doc,dt,dn){
	doc.salary_structure = ''
	cur_frm.cscript.fiscal_year(doc, dt, dn)
	// Ver 1.0 Begins, added by SSK on 12/09/2016
	// GIS
		if (doc.employee){
			cur_frm.call({
				method: "erpnext.hr.hr_custom_functions.get_employee_gis",
				args: {
					"employee": doc.employee
				},
				callback: function(r){	
					if (r.message){
						calc_gis_amt = Math.round(r.message[0][0]);
					}
				}
			});	
		}
			
		// PF
		if (doc.employee){
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
		}
		
		//fetch_eligibility_criteria(cur_frm);
	// Ver 1.0 Ends
}

cur_frm.cscript.leave_without_pay = function(doc,dt,dn){
	if (doc.employee && doc.fiscal_year && doc.month) {
		return $c_obj(doc, 'get_leave_details', {"lwp": doc.leave_without_pay}, function(r, rt) {
			var doc = locals[dt][dn];
			cur_frm.refresh();
			calculate_all(doc, dt, dn);
		});
	}
}

var calculate_all = function(doc, dt, dn) {
	calculate_earning_total(doc, dt, dn);
	calculate_ded_total(doc, dt, dn);
	calculate_net_pay(doc, dt, dn);
}

// Ver 1.0 Begins, by SSK on 26/08/2016, Following block is commented
/*
cur_frm.cscript.amount = function(doc,dt,dn){
	calculate_earning_total(doc, dt, dn);
	calculate_net_pay(doc, dt, dn);
}
*/
// Ver 1.0 Ends

cur_frm.cscript.depends_on_lwp = function(doc,dt,dn){
	calculate_earning_total(doc, dt, dn, true);
	calculate_net_pay(doc, dt, dn);
}
// Trigger on earning modified amount and depends on lwp
// ------------------------------------------------------------------------
cur_frm.cscript.amount = function(doc,dt,dn){
	// Ver 1.0 Begins, by SSK on 26/08/2016, Following line is added
	calculate_earning_total(doc, dt, dn);
	// Ver 1.0 Ends
	calculate_ded_total(doc, dt, dn);
	// Ver 1.0 Begins, by SSK on 26/08/2016, Following line is added
	calculate_others(doc, dt, dn);
	// Ver 1.0 Ends
	calculate_net_pay(doc, dt, dn);
}

frappe.ui.form.on('Salary Detail', {
	earnings_remove: function(doc,dt,dn) {
		calculate_earning_total(doc, dt, dn);
		calculate_ded_total(doc, dt, dn);
		calculate_others(cur_frm.doc, dt, dn);
		calculate_net_pay(doc, dt, dn);
		refresh_many(['amount','gross_pay','total_deduction']);
	}, 
	
	deductions_remove: function(doc,dt,dn) {
		calculate_earning_total(doc, dt, dn);
		calculate_ded_total(doc, dt, dn);
		calculate_others(cur_frm.doc, dt, dn);
		calculate_net_pay(doc, dt, dn);
		refresh_many(['amount','gross_pay','total_deduction']);
	}
})

cur_frm.cscript.depends_on_lwp = function(doc, dt, dn) {
	calculate_ded_total(doc, dt, dn, true);
	calculate_net_pay(doc, dt, dn);
};

// Calculate earning total
// ------------------------------------------------------------------------
var calculate_earning_total = function(doc, dt, dn, reset_amount) {
	var tbl = doc.earnings || [];
	var total_earn = 0;
	for(var i = 0; i < tbl.length; i++){
		if(cint(tbl[i].depends_on_lwp) == 1) {
			tbl[i].amount =  Math.round(tbl[i].default_amount)*(flt(doc.payment_days) /
				cint(doc.total_days_in_month)*100)/100;
			refresh_field('amount', tbl[i].name, 'earnings');
		} else if(reset_amount) {
			tbl[i].amount = tbl[i].default_amount;
			refresh_field('amount', tbl[i].name, 'earnings');
		}
		total_earn += flt(tbl[i].amount);
		
	}
	doc.gross_pay = total_earn + flt(doc.arrear_amount) + flt(doc.leave_encashment_amount);
	refresh_many(['amount','gross_pay']);
}

// Calculate deduction total
// ------------------------------------------------------------------------
var calculate_ded_total = function(doc, dt, dn, reset_amount) {
	var tbl = doc.deductions || [];
	var total_ded = 0;
	for(var i = 0; i < tbl.length; i++){
		if(cint(tbl[i].depends_on_lwp) == 1) {
			tbl[i].amount = Math.round(tbl[i].default_amount)*(flt(doc.payment_days)/cint(doc.total_days_in_month)*100)/100;
			refresh_field('amount', tbl[i].name, 'deductions');
		} else if(reset_amount) {
			tbl[i].amount = tbl[i].default_amount;
			refresh_field('amount', tbl[i].name, 'deductions');
		}
		total_ded += flt(tbl[i].amount);
	}
	doc.total_deduction = total_ded;
	refresh_field('total_deduction');
}

// Calculate net payable amount
// ------------------------------------------------------------------------
var calculate_net_pay = function(doc, dt, dn) {
	doc.net_pay = flt(doc.gross_pay) - flt(doc.total_deduction);
	doc.rounded_total = Math.round(doc.net_pay);
	refresh_many(['net_pay', 'rounded_total']);
}

// trigger on arrear
// ------------------------------------------------------------------------
cur_frm.cscript.arrear_amount = function(doc,dt,dn){
	calculate_earning_total(doc, dt, dn);
	calculate_net_pay(doc, dt, dn);
}

// trigger on encashed amount
// ------------------------------------------------------------------------
cur_frm.cscript.leave_encashment_amount = cur_frm.cscript.arrear_amount;

// validate
// ------------------------------------------------------------------------
cur_frm.cscript.validate = function(doc, dt, dn) {
	calculate_all(doc, dt, dn);
}

cur_frm.fields_dict.employee.get_query = function(doc,cdt,cdn) {
	return{
		query: "erpnext.controllers.queries.employee_query"
	}
}


//++ Ver 20160803.1 Begins, calculate_totals2 is added by SSK on 27/08/2016
var calculate_others = function(doc, dt, dn){
	var e_tbl = doc.earnings || [];
	var d_tbl = doc.deductions || [];
	var corp_all_id = -1, cont_all_id = -1, comm_all_id = -1, psa_all_id = -1, mpi_all_id = -1,
		off_all_id = -1, tran_all_id = -1, fuel_all_id = -1, ot_all_id = -1,
		corp_all_dn, cont_all_dn, comm_all_dn, psa_all_dn, mpi_all_dn,
		off_all_dn, tran_all_dn, fuel_all_dn, ot_all_dn,
		basic_all_id = -1, basic_all_dn;
	var pf_ded_id = -1, pf_ded_dn, health_ded_id = -1, health_ded_dn, tds_ded_id = -1, tds_ded_dn,
		gis_ded_id = -1, gis_ded_dn;
		
	console.log('--------------');

	//fetch_eligibility_criteria(cur_frm);
	if (typeof doc.salary_structure !== 'undefined'){
		frappe.model.with_doc("Salary Structure",doc.salary_structure,function(){
			var ss = frappe.model.get_doc("Salary Structure",doc.salary_structure);
			auto_calculate_items(ss);
		});
	}
	
	function auto_calculate_items(ss){
		
		// Saving IndexValue and DocumentName from Earnings child table
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
		if (ss.eligible_for_corporate_allowance==1){
			var calc_amt = 0;
			if (basic_all_id >= 0){
				calc_amt = (e_tbl[basic_all_id].amount*ss.ca*0.01);
				calc_amt = Math.round(calc_amt);
			}
			
			if (corp_all_id >= 0){
				if (calc_amt != e_tbl[corp_all_id].amount){
					console.log('++CORP: calc_amt: '+calc_amt+' e_tbl: '+e_tbl[corp_all_id].amount);
					frappe.model.set_value("Salary Detail", corp_all_dn, "amount", calc_amt);				
				}
			} 
		}
		else if (ss.eligible_for_corporate_allowance==0 && corp_all_id >= 0 && e_tbl[corp_all_id].amount > 0){
			console.log('--CORP');
			frappe.model.set_value("Salary Detail", corp_all_dn, "amount", 0);
		}

		if (ss.eligible_for_contract_allowance==1){
			var calc_amt = 0;
			if (basic_all_id >= 0){
				calc_amt = (e_tbl[basic_all_id].amount*ss.contract_allowance*0.01);
				calc_amt = Math.round(calc_amt);
			}
			
			if (cont_all_id >= 0){
				if (e_tbl[cont_all_id].amount != calc_amt){
					console.log('++CONT: calc_amt: '+calc_amt+' e_tbl: '+e_tbl[cont_all_id].amount);
					frappe.model.set_value("Salary Detail", cont_all_dn, "amount", calc_amt);				
				}
			}
		}
		else if(ss.eligible_for_contract_allowance==0 && cont_all_id >=0 && e_tbl[cont_all_id].amount > 0){
			console.log('--CONT');
			frappe.model.set_value("Salary Detail", cont_all_dn, "amount", 0);
		}

		if (ss.eligible_for_communication_allowance==1){
			var calc_amt = 0;
			calc_amt = ss.communication_allowance;
			calc_amt = Math.round(calc_amt);
			
			if (comm_all_id >= 0){
				if (e_tbl[comm_all_id].amount != calc_amt){
					console.log('++COMM: calc_amt: '+calc_amt+' e_tbl: '+e_tbl[comm_all_id].amount);
					frappe.model.set_value("Salary Detail", comm_all_dn, "amount", calc_amt);				
				}
			} 
		}
		else if(ss.eligible_for_communication_allowance==0 && comm_all_id >= 0 && e_tbl[comm_all_id].amount > 0){
			console.log('--COMM');
			frappe.model.set_value("Salary Detail", comm_all_dn, "amount", 0);
		}	

		if (ss.eligible_for_psa==1){
			var calc_amt = 0;
			if (basic_all_id >= 0){
				calc_amt = (e_tbl[basic_all_id].amount*ss.psa*0.01);
				calc_amt = Math.round(calc_amt);
			}
			
			if (psa_all_id >= 0){
				if (e_tbl[psa_all_id].amount > calc_amt){
					console.log('++PSA: calc_amt: '+calc_amt+' e_tbl: '+e_tbl[psa_all_id].amount);
					frappe.model.set_value("Salary Detail", psa_all_dn, "amount", calc_amt);				
				}
			} 
		}
		else if(ss.eligible_for_psa==0 && psa_all_id >= 0 && e_tbl[psa_all_id].amount > 0){
			console.log('--PSA');
			frappe.model.set_value("Salary Detail", psa_all_dn, "amount", 0);
		}		

		if (ss.eligible_for_mpi==1){
			var calc_amt = 0;
			if (basic_all_id >= 0){
				calc_amt = (e_tbl[basic_all_id].amount*ss.mpi*0.01);
				calc_amt = Math.round(calc_amt);
			}
			
			if (mpi_all_id >= 0){
				if (e_tbl[mpi_all_id].amount != calc_amt){
					console.log('++MPI: calc_amt: '+calc_amt+' e_tbl: '+e_tbl[mpi_all_id].amount);
					frappe.model.set_value("Salary Detail", mpi_all_dn, "amount", calc_amt);		
				}
			} 
		}
		else if(ss.eligible_for_mpi==0 && mpi_all_id >= 0 && e_tbl[mpi_all_id].amount > 0){
			console.log('--MPI: ');
			frappe.model.set_value("Salary Detail", mpi_all_dn, "amount", 0);
		}			

		if (ss.eligible_for_officiating_allowance==1){
			var calc_amt = 0;
			if (basic_all_id >= 0){
				calc_amt = (e_tbl[basic_all_id].amount*ss.officiating_allowance*0.01);
				calc_amt = Math.round(calc_amt);
			}
			
			if (off_all_id >= 0){
				if (e_tbl[off_all_id].amount != calc_amt){
					console.log('++OFF: calc_amt: '+calc_amt+' e_tbl: '+e_tbl[off_all_id].amount);
					frappe.model.set_value("Salary Detail", off_all_dn, "amount", calc_amt);				
				}
			} 
		}
		else if(ss.eligible_for_officiating_allowance==0 && off_all_id >= 0 && e_tbl[off_all_id].amount > 0){
			console.log('--OFF');
			frappe.model.set_value("Salary Detail", off_all_dn, "amount", 0);
		}				

		if (ss.eligible_for_temporary_transfer_allowance==1){
			var calc_amt = 0;
			if (basic_all_id >= 0){
				calc_amt = (e_tbl[basic_all_id].amount*ss.temporary_transfer_allowance*0.01);
				calc_amt = Math.round(calc_amt);
			}
			
			if (tran_all_id >= 0){
				if (e_tbl[tran_all_id].amount != calc_amt){
					console.log('++TRAN: calc_amt: '+calc_amt+' e_tbl: '+e_tbl[tran_all_id].amount);
					frappe.model.set_value("Salary Detail", tran_all_dn, "amount", calc_amt);				
				}
			} 
		}
		else if(ss.eligible_for_temporary_transfer_allowance==0 && tran_all_id >=0 && e_tbl[tran_all_id].amount > 0){
			console.log('--TRANT');
			frappe.model.set_value("Salary Detail", tran_all_dn, "amount", 0);
		}					


		if (ss.eligible_for_fuel_allowances==1){
			var calc_amt = 0;
			calc_amt = ss.fuel_allowances;
			calc_amt = Math.round(calc_amt);
			
			if (fuel_all_id >= 0){
				if (e_tbl[fuel_all_id].amount != calc_amt){
					console.log('++FUEL: calc_amt: '+calc_amt+' e_tbl: '+e_tbl[fuel_all_id].amount);
					frappe.model.set_value("Salary Detail", fuel_all_dn, "amount", calc_amt);				
				}
			} 
		}
		else if(ss.eligible_for_fuel_allowances==0 && fuel_all_id >= 0 && e_tbl[fuel_all_id].amount > 0){
			console.log('--FUEL');
			frappe.model.set_value("Salary Detail", fuel_all_dn, "amount", 0);
		}						

		
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
		if (gis_ded_id >= 0 && ss.eligible_for_gis){
			if (d_tbl[gis_ded_id].amount != calc_gis_amt){
				console.log('++GIS: calc_amt: '+calc_gis_amt+' d_tbl: '+d_tbl[gis_ded_id].amount);
				frappe.model.set_value("Salary Detail", gis_ded_dn, "amount", calc_gis_amt);				
			}
		}

		// PF
		var calc_pf_amt = 0;
		if (pf_ded_id >= 0 && ss.eligible_for_pf){
			if (basic_all_id >= 0){
				calc_pf_amt = Math.round(e_tbl[basic_all_id].amount*employee_pf*0.01);
			}
			if(d_tbl[pf_ded_id].amount != calc_pf_amt){
				console.log('++PF: pf_amt: '+calc_pf_amt+' d_tbl: '+d_tbl[pf_ded_id].amount);
				frappe.model.set_value("Salary Detail", pf_ded_dn, "amount", calc_pf_amt);				
			}
		}
		
		// Health Contribution
		//calculate_earning_total(doc, dt, dn);

		var calc_health_amt = 0;
		if (health_ded_id >= 0 && ss.eligible_for_health_contribution){
			calc_health_amt = Math.round(cur_frm.doc.gross_pay*health_contribution*0.01);
			if (d_tbl[health_ded_id].amount != calc_health_amt){
				console.log('++HEALTH: calc_amt: '+calc_health_amt+' d_tbl: '+d_tbl[health_ded_id].amount);
				frappe.model.set_value("Salary Detail", health_ded_dn, "amount", calc_health_amt);				
			}
		} 
		
		// Salary Tax
		var calc_tds_amt = 0;	
		cur_frm.call({
			method: "erpnext.hr.hr_custom_functions.get_salary_tax",
			args: {
				"gross_amt": (cur_frm.doc.gross_pay-calc_pf_amt-calc_gis_amt),
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
						console.log('++TDS: calc_amt: '+calc_tds_amt+' d_tbl: '+d_tbl[tds_ded_id].amount);
						frappe.model.set_value("Salary Detail", tds_ded_dn, "amount", calc_tds_amt);				
					}
				}
			}
		});	
	}
}
// Ver 1.0 Ends
