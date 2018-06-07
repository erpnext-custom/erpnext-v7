// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt
/*
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
2.0		  		  SHIV		     11/08/2017         					Default "Project Tasks" is replaced by custom
																			"Activity Tasks"
2.0				  SHIV           02/09/2017                             Introducing Project Advances
--------------------------------------------------------------------------------------------------------------------------                                                                          
*/

cur_frm.add_fetch("cost_center", "branch", "branch")
cur_frm.add_fetch("customer", "image", "customer_image" );
cur_frm.add_fetch("customer", "customer_details", "customer_address" );

frappe.ui.form.on("Project", {
	// ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
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
		frm.get_docfield("activity_tasks").allow_bulk_edit = 1;		
		frm.get_docfield("additional_tasks").allow_bulk_edit = 1;		
		
		frm.get_field('activity_tasks').grid.editable_fields = [
			{fieldname: 'task', columns: 3},
			{fieldname: 'is_group', columns: 1},
			{fieldname: 'start_date', columns: 2},
			{fieldname: 'end_date', columns: 2},
			{fieldname: 'work_quantity', columns: 1},
			{fieldname: 'work_quantity_complete', columns: 1}
		];
		
		frm.get_field('additional_tasks').grid.editable_fields = [
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
		
		frm.get_field('project_boq_item').grid.editable_fields = [
			{fieldname: 'boq_name', columns: 2},
			{fieldname: 'boq_date', columns: 2},
			{fieldname: 'total_amount', columns: 2},
			{fieldname: 'received_amount', columns: 2},
			{fieldname: 'balance_amount', columns: 2}
		];				
		
		frm.get_field('project_invoice_item').grid.editable_fields = [
			{fieldname: 'invoice_name', columns: 2},
			{fieldname: 'invoice_date', columns: 2},
			{fieldname: 'net_invoice_amount', columns: 2},
			{fieldname: 'total_received_amount', columns: 2},
			{fieldname: 'total_balance_amount', columns: 2}
		];						
	},	
	// +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++
	
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
		frm.add_custom_button(__("Project Register"), function(){
				frappe.route_options = {
					project: frm.doc.name,
					additional_info: 1
				};
				frappe.set_route("query-report", "Project Register");
			},__("Reports"), "icon-file-alt"
		);
		frm.add_custom_button(__("Manpower"), function(){
				frappe.route_options = {
					project: frm.doc.name
				};
				frappe.set_route("query-report", "Project Manpower");
			},__("Reports"), "icon-file-alt"
		);
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
		
		if(frm.doc.docstatus === 0){
			enable_disable_items(frm);
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
		// ++++++++++++++++++++ Ver 2.0 BEGINS ++++++++++++++++++++
		// Following code is replaced by following code by SHIV on 20/09/2017
		/*
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
		*/
		if(frm.doc.__onload.activity_summary.length) {
			var days = $.map(frm.doc.__onload.activity_summary, function(d) { return d.total_days });
			var max_count = Math.max.apply(null, days);
			var sum = days.reduce(function(a, b) { return a + b; }, 0);
			/*
			var section = frm.dashboard.add_section(
				frappe.render_template('project_dashboard',
					{
						data: frm.doc.__onload.activity_summary,
						max_count: max_count,
						sum: sum
					}));
			*/
			
			var section = frm.dashboard.add_section(
				frappe.render_template('test_dashboard',
					{
						sum: sum
					}
			));
			
			section.on('click', '.time-sheet-link', function() {
				var activity_type = $(this).attr('data-activity_type');
				frappe.set_route('List', 'Timesheet',
					{'activity_type': activity_type, 'project': frm.doc.name});
			});
		}
		// +++++++++++++++++++++ Ver 2.0 ENDS +++++++++++++++++++++
	},
	
	imprest_limit: function(frm){
		if (parseFloat(frm.doc.imprest_limit || 0.0) < parseFloat(frm.doc.imprest_received || 0.0)){
			msgprint(__("Imprest Limit cannot be less than already received amount."));
		}
		else {
			cur_frm.set_value("imprest_receivable",parseFloat(frm.doc.imprest_limit || 0.0)-parseFloat(frm.doc.imprest_received || 0.0))
		}
	},
	branch: function(frm){
		// Update Cost Center
		if(frm.doc.branch){
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Cost Center',
					filters: {
						'branch': frm.doc.branch
					},
					fieldname: ['name']
				},
				callback: function(r){
					if(r.message){
						cur_frm.set_value("cost_center", r.message.name);
						refresh_field('cost_center');
					}
				}
			});
		}
	},
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
	activity_tasks_remove: function(frm, doctype, name){
		calculate_work_quantity(frm);
	},
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

frappe.ui.form.on("Additional Tasks", {
	activity_tasks_remove: function(frm, doctype, name){
		calculate_work_quantity(frm);
	},
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
	var adt= frm.doc.additional_tasks || [];
	total_work_quantity = 0.0;
	total_work_quantity_complete = 0.0;
	total_add_work_quantity = 0.0;
	total_add_work_quantity_complete = 0.0;

	for(var i=0; i<at.length; i++){
		//console.log(at[i].is_group);
		if (at[i].work_quantity && !at[i].is_group){
			total_work_quantity += at[i].work_quantity || 0;
			total_work_quantity_complete += at[i].work_quantity_complete || 0;
		}
	}
	
	for(var i=0; i<adt.length; i++){
		//console.log(at[i].is_group);
		if (adt[i].work_quantity && !adt[i].is_group){
			total_add_work_quantity += adt[i].work_quantity || 0;
			total_add_work_quantity_complete += adt[i].work_quantity_complete || 0;
		}
	}
	
	cur_frm.set_value("tot_wq_percent",total_work_quantity);
	cur_frm.set_value("tot_wq_percent_complete",total_work_quantity_complete);
	cur_frm.set_value("tot_add_wq_percent",total_add_work_quantity);
	cur_frm.set_value("tot_add_wq_percent_complete",total_add_work_quantity_complete);
}
// +++++++++++++++++++++ Ver 1.0 ENDS +++++++++++++++++++++

/*
frappe.ui.form.on("Activity Tasks","is_group", function(frm, cdt, cdn){
	var child = locals[cdt][cdn];
	cur_frm.doc.activity_tasks.forEach(function(child){
		var sel = format('div[data-fieldname="activity_tasks"] > div.grid-row[data-idx="{0}"]',[child.idx]);
		if (child.is_group == 1){
			$(sel).css('background-color',"#ff5858");
		} else {
			$(sel).css('background-color','transparent');
		}
	});
});
*/

function enable_disable_items(frm){
	var toggle_fields = ["branch"];
	
	if(frm.doc.branch){
		if(in_list(user_roles, "Project Committee")){
			toggle_fields.forEach(function(field_name){
				frm.set_df_property(field_name, "read_only", 0);
			});
		}
		else {
			toggle_fields.forEach(function(field_name){
				frm.set_df_property(field_name, "read_only", 1);
			});
		}
	}
}