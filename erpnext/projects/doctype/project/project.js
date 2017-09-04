// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
/*
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  		  SHIV		     11/08/2017         					Default "Project Tasks" is replaced by custom
																			"Activity Tasks"
1.0				  SHIV           02/09/2017                             Introducing Project Advances
--------------------------------------------------------------------------------------------------------------------------                                                                          
*/

cur_frm.add_fetch("cost_center", "branch", "branch")

frappe.ui.form.on("Project", {
	// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
	// Following code is commented by SHIV on 2017/08/11
	/*
	setup: function(frm) {
		frm.get_field('tasks').grid.editable_fields = [
			{fieldname: 'title', columns: 3},
			{fieldname: 'status', columns: 3},
			{fieldname: 'start_date', columns: 2},
			{fieldname: 'end_date', columns: 2}
		];

	},
	*/
	
	// Follwoing code is added by SHIV on 2017/08/11
	setup: function(frm) {
		frm.get_field('activity_tasks').grid.editable_fields = [
			{fieldname: 'task', columns: 3},
			{fieldname: 'is_group', columns: 1},
			{fieldname: 'start_date', columns: 2},
			{fieldname: 'end_date', columns: 2},
			{fieldname: 'work_quantity', columns: 1},
			{fieldname: 'work_quantity_complete', columns: 1}
		];
		frm.get_field('project_advance_item').grid.editable_fields = [
			{fieldname: 'advance_name', columns: 2},
			{fieldname: 'advance_date', columns: 2},
			{fieldname: 'received_amount', columns: 2},
			{fieldname: 'adjustment_amount', columns: 2},
			{fieldname: 'balance_amount', columns: 2}
		];		
	},	
	// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++
	
	onload: function(frm) {
		var so = frappe.meta.get_docfield("Project", "sales_order");
		so.get_route_options_for_new_doc = function(field) {
			if(frm.is_new()) return;
			return {
				"customer": frm.doc.customer,
				"project_name": frm.doc.name
			}
		}

		frm.set_query('customer', 'erpnext.controllers.queries.customer_query');
		
		frm.set_query("user", "users", function() {
					return {
						query:"erpnext.projects.doctype.project.project.get_users_for_project"
					}
				});

		// sales order
		frm.set_query('sales_order', function() {
			var filters = {
				'project': ["in", frm.doc.__islocal ? [""] : [frm.doc.name, ""]]
			};

			if (frm.doc.customer) {
				filters["customer"] = frm.doc.customer;
			}

			return {
				filters: filters
			}
		});
	},
	refresh: function(frm) {
		// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
		// Following code added SHIV on 02/09/2017
		frm.add_custom_button(__("Advance"), function(){frm.trigger("make_project_advance")},__("Make"), "icon-file-alt");
		// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++
		
		if(frm.doc.__islocal) {
			frm.web_link && frm.web_link.remove();
		} else {
			frm.add_web_link("/projects?project=" + encodeURIComponent(frm.doc.name));

			if(frappe.model.can_read("Task")) {
				frm.add_custom_button(__("Gantt Chart"), function() {
					frappe.route_options = {"project": frm.doc.name,
						"start": frm.doc.expected_start_date, "end": frm.doc.expected_end_date};
					frappe.set_route("Gantt", "Task");
				});
			}

			frm.trigger('show_dashboard');
		}
	},
	
	// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
	// Following function created by SHIV on 02/09/2017
	make_project_advance: function(frm){
		frappe.model.open_mapped_doc({
			method: "erpnext.projects.doctype.project.project.make_project_advance",
			frm: frm
		});
	},
	// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++
	
	tasks_refresh: function(frm) {
		var grid = frm.get_field('tasks').grid;
		grid.wrapper.find('select[data-fieldname="status"]').each(function() {
			if($(this).val()==='Open') {
				$(this).addClass('input-indicator-open');
			} else {
				$(this).removeClass('input-indicator-open');
			}
		});
	},
	show_dashboard: function(frm) {
		if(frm.doc.__onload.activity_summary.length) {
			var hours = $.map(frm.doc.__onload.activity_summary, function(d) { return d.total_hours });
			var max_count = Math.max.apply(null, hours);
			var sum = hours.reduce(function(a, b) { return a + b; }, 0);
			var section = frm.dashboard.add_section(
				frappe.render_template('project_dashboard',
					{
						data: frm.doc.__onload.activity_summary,
						max_count: max_count,
						sum: sum
					}));

			section.on('click', '.time-sheet-link', function() {
				var activity_type = $(this).attr('data-activity_type');
				frappe.set_route('List', 'Timesheet',
					{'activity_type': activity_type, 'project': frm.doc.name});
			});
		}
	}
});

frappe.ui.form.on("Project Task", {
	edit_task: function(frm, doctype, name) {
		var doc = frappe.get_doc(doctype, name);
		if(doc.task_id) {
			frappe.set_route("Form", "Task", doc.task_id);
		} else {
			msgprint(__("Save the document first."));
		}
	},
	status: function(frm, doctype, name) {
		frm.trigger('tasks_refresh');
	},
});

frappe.ui.form.on("Project Advance Item",{
	view_advance: function(frm, doctype, name){
		var doc = frappe.get_doc(doctype, name);
		frappe.set_route("Form", "Project Advance", doc.advance_name);
	}
});

// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
// Following block of code added by SHIV on 11/08/2017
frappe.ui.form.on("Activity Tasks", {
	edit_task: function(frm, doctype, name) {
		var doc = frappe.get_doc(doctype, name);
		if(doc.task_id) {
			frappe.set_route("Form", "Task", doc.task_id);
		} else {
			msgprint(__("Save the document first."));
		}
	},
	view_timesheet: function(frm, doctype, name){
		var doc = frappe.get_doc(doctype, name);
		if(doc.task_id){
			frappe.route_options = {"project": frm.doc.name, "task": doc.task_id}
			frappe.set_route("List", "Timesheet");
		} else {
			msgprint(__("Save the document first."));
		}
	},
	status: function(frm, doctype, name) {
		frm.trigger('tasks_refresh');
	},
	work_quantity: function(frm, doctype, name){
		calculate_work_quantity(frm);
	},
});
// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++

frappe.ui.form.on("Project", "refresh", function(frm) {
    cur_frm.set_query("cost_center", function() {
        return {
            "filters": {
		"is_group": 0,
		"is_disabled": 0
            }
        };
    });
})


// ++++++++++++++++++++ Ver 1.0 BEGINS ++++++++++++++++++++
// Following function created by SHIV on 2017/08/17
var calculate_work_quantity = function(frm){
	var at = frm.doc.activity_tasks || [];
	total_work_quantity = 0;
	
	for(var i=0; i<at.length; i++){
		if (at[i].work_quantity){
			total_work_quantity += at[i].work_quantity || 0;
		}
	}
	cur_frm.set_value("tot_wq_percent",total_work_quantity);
	
}
// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++