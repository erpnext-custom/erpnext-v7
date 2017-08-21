// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
/*
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  		  SHIV		     2017/08/15         					Project Name & Task are added at 'Timesheet' level
																			inorder to provide flexibility in task based
																			progress logging.
--------------------------------------------------------------------------------------------------------------------------                                                                          
*/
cur_frm.add_fetch('employee', 'employee_name', 'employee_name');

frappe.ui.form.on("Timesheet", {
	setup: function(frm) {
		// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
		// Following code is commented by SHIV on 2017/08/11		
		/*
		frm.get_field('time_logs').grid.editable_fields = [
			{fieldname: 'billable', columns: 1},
			{fieldname: 'project', columns: 3},
			{fieldname: 'activity_type', columns: 2},
			{fieldname: 'from_time', columns: 3},
			{fieldname: 'hours', columns: 1}
		];
		*/

		// Follwoing code is added by SHIV on 2017/08/11
		frm.get_field('time_logs').grid.editable_fields = [
			{fieldname: 'from_time', columns: 3},
			{fieldname: 'to_time', columns: 3},
			{fieldname: 'hours', columns: 1},
			{fieldname: 'target_quantity', columns: 1},
			{fieldname: 'target_quantity_complete', columns: 2},
		];
		
		frm.fields_dict.task.get_query = function() {
			return {
				filters:{
					'project': frm.doc.project
				}
			}
		}
		// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++
		
		frm.fields_dict.employee.get_query = function() {
			return {
				filters:{
					'status': 'Active'
				}
			}
		}

		frm.fields_dict['time_logs'].grid.get_field('task').get_query = function(frm, cdt, cdn) {
			child = locals[cdt][cdn];
			return{
				filters: {
					'project': child.project,
					'status': ["!=", "Closed"]
				}
			}
		}
	},

	onload: function(frm){
		if (frm.doc.__islocal && frm.doc.time_logs) {
			calculate_time_and_amount(frm);
		}
	},

	refresh: function(frm) {
		if(frm.doc.docstatus==1) {
			if(!frm.doc.sales_invoice && frm.doc.total_billing_amount > 0){
				frm.add_custom_button(__("Make Sales Invoice"), function() { frm.trigger("make_invoice") },
					"icon-file-alt");
			}

			if(!frm.doc.salary_slip && frm.doc.employee){
				frm.add_custom_button(__("Make Salary Slip"), function() { frm.trigger("make_salary_slip") },
					"icon-file-alt");
			}
		}

		// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
		if(frappe.model.can_read("Project")) {
			frm.add_custom_button(__("Project"), function() {
				frappe.route_options = {"name": frm.doc.project}
				frappe.set_route("Form", "Project", frm.doc.project);
			}, __("View"), true);
		}
		
		if(frappe.model.can_read("Task")) {
			frm.add_custom_button(__("Task"), function() {
				frappe.route_options = {"name": frm.doc.task}
				frappe.set_route("Form", "Task", frm.doc.task);
			}, __("View"), true);
		}
		// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++		
	},

	make_invoice: function(frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.timesheet.timesheet.make_sales_invoice",
			frm: frm
		});
	},

	make_salary_slip: function(frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.timesheet.timesheet.make_salary_slip",
			frm: frm
		});
	},
	
	onsubmit: function(frm){
		msgprint(__("are you sure?"));
	},
})

frappe.ui.form.on("Timesheet Detail", {	
	percent_complete: function(frm){
		calculate_time_and_amount(frm);
	},

	target_quantity_complete: function(frm, cdt, cdn){
		var child = locals[cdt][cdn];
		
		if(child.target_quantity_complete > child.target_quantity){
			msgprint(__("Achieved value cannot be more than Target value."));
			//frappe.model.set_value(cdt, cdn, "target_quantity_complete",child.target_quantity);
		}
		calculate_target_quantity_complete(frm);
	},
		
	time_logs_remove: function(frm) {
		calculate_time_and_amount(frm);
	},

	from_time: function(frm, cdt, cdn) {
		calculate_end_time(frm, cdt, cdn)
	},

	to_time: function(frm, cdt, cdn) {
		var child = locals[cdt][cdn];

		if(frm._setting_hours) return;
		frappe.model.set_value(cdt, cdn, "hours", moment(child.to_time).diff(moment(child.from_time),
			"seconds") / 3600);
	},

	hours: function(frm, cdt, cdn) {
		calculate_end_time(frm, cdt, cdn)
	},

	billing_rate: function(frm, cdt, cdn) {
		calculate_billing_costing_amount(frm, cdt, cdn)
	},

	costing_rate: function(frm, cdt, cdn) {
		calculate_billing_costing_amount(frm, cdt, cdn)
	},

	billable: function(frm, cdt, cdn) {
		calculate_billing_costing_amount(frm, cdt, cdn)
	},

	activity_type: function(frm, cdt, cdn) {
		child = locals[cdt][cdn];
		frappe.call({
			method: "erpnext.projects.doctype.timesheet.timesheet.get_activity_cost",
			args: {
				employee: frm.doc.employee,
				activity_type: child.activity_type
			},
			callback: function(r){
				if(r.message){
					frappe.model.set_value(cdt, cdn, 'billing_rate', r.message['billing_rate']);
					frappe.model.set_value(cdt, cdn, 'costing_rate', r.message['costing_rate']);
					calculate_billing_costing_amount(frm, cdt, cdn)
				}
			}
		})
	}
});

calculate_end_time = function(frm, cdt, cdn){
	var child = locals[cdt][cdn];

	var d = moment(child.from_time);
	d.add(child.hours, "hours");
	frm._setting_hours = true;
	frappe.model.set_value(cdt, cdn, "to_time", d.format(moment.defaultDatetimeFormat));
	frm._setting_hours = false;

	calculate_billing_costing_amount(frm, cdt, cdn)
}

var calculate_billing_costing_amount = function(frm, cdt, cdn){
	child = locals[cdt][cdn]
	billing_amount = costing_amount = 0.0;

	if(child.hours && child.billable){
		billing_amount = (child.hours * child.billing_rate);
		costing_amount = flt(child.costing_rate * child.hours);
	}

	frappe.model.set_value(cdt, cdn, 'billing_amount', billing_amount);
	frappe.model.set_value(cdt, cdn, 'costing_amount', costing_amount);
	calculate_time_and_amount(frm)
}

// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
// Following function created by SHIV on 2017/08/17
var calculate_target_quantity_complete = function(frm){
	var tl = frm.doc.time_logs || [];
	total_target_quantity_complete = 0;
	
	for(var i=0; i<tl.length; i++) {
		if (tl[i].target_quantity_complete) {
			total_target_quantity_complete += parseFloat(tl[i].target_quantity_complete || 0);
		}
	}
	
	frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Timesheet",
				filters: {
					task: frm.doc.task
				},
				fields:["name","target_quantity_complete"]
			},
			callback: function(r){
				$.each(r.message, function(i, d){
					if (d.name != frm.doc.name){
						total_target_quantity_complete += parseFloat(d.target_quantity_complete || 0);
					}
				})
				cur_frm.set_value("target_quantity_complete", parseFloat(total_target_quantity_complete));
			}
	})	
	
	/*
	frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Task",
				filters: {
					name: frm.doc.task
				},
				fieldname:["target_quantity_complete"]
			},
			callback: function(r){
				cur_frm.set_value("target_quantity_complete", (r.message.target_quantity_complete || 0) + (total_target_quantity_complete || 0));
			}
	})
	*/
}
// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++	

var calculate_time_and_amount = function(frm) {
	var tl = frm.doc.time_logs || [];
	total_hr = 0;
	total_billing_amount = 0;
	total_costing_amount = 0;
		
	for(var i=0; i<tl.length; i++) {
		if (tl[i].hours) {
			total_hr += tl[i].hours || 0;
			total_billing_amount += tl[i].billing_amount;
			total_costing_amount += tl[i].costing_amount;
		}
	}

	cur_frm.set_value("total_hours", total_hr);
	cur_frm.set_value("total_billing_amount", total_billing_amount);
	cur_frm.set_value("total_costing_amount", total_costing_amount);
}