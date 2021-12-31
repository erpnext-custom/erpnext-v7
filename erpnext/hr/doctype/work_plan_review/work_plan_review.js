// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('employee', 'employee_name', 'employee_name');
cur_frm.add_fetch("employee", "employee_subgroup", "grade");
cur_frm.add_fetch("employee", "designation", "designation");
cur_frm.add_fetch("employee", "branch", "branch");


frappe.ui.form.on("Work Plan Review",{
	refresh: function(frm) {

	frm.set_query("leave_approver", function() {
			return {
				query: "erpnext.hr.doctype.leave_application.leave_application.get_approvers",
				filters: {
					employee: frm.doc.employee
				}
			};
		});

	},

	onload: function(frm){
		frm.set_query('work_plan', function(){
			return{
				filters:{
					workflow_state: 'Approved',
				}
			};
		});
	},

	leave_approver: function(frm){
		if(frm.doc.leave_approver){
			frm.set_value("leave_approver_name", frappe.user.full_name(frm.doc.leave_approver));
		}
	},
});


cur_frm.cscript.refresh = function(doc,cdt,cdn){

}


cur_frm.cscript.work_plan = function(doc, cdt, cdn){
	doc.plan_template = [];
	erpnext.utils.map_current_doc({
		method: "erpnext.hr.doctype.work_plan_review.work_plan_review.fetch_appraisal_work_plan",
		source_name: cur_frm.doc.work_plan,
		frm: cur_frm
	});

}



//work complated
cur_frm.cscript.accomplished_target1 = function(doc,cdt,cdn){
	var d = locals[cdt][cdn];
	if (d.accomplished_target1){
		if (flt(d.accomplished_target1) > d.work_target) {
			msgprint(__("Work complated must be less than or equal to Work Target"));
			d.accomplished_target1 = 0;
			refresh_field('accomplished_target1', d.name, 'plan_template');
		}
		//find remaining work
		d.remaining_target = (d.work_target - d.accomplished_target1);
		refresh_field('remaining_target', d.name, 'plan_template');
	}
	else{
		d.remaining_target = d.work_target;
		refresh_field('remaining_target', d.name, 'plan_template');
	}

}


cur_frm.cscript.accomplished_targets1 = function(doc,cdt,cdn){
	var d = locals[cdt][cdn];
	if (d.accomplished_targets1){
		if (flt(d.accomplished_targets1) > d.work_targets) {
			msgprint(__("Work complated must be less than or equal to Work Target"));
			d.accomplished_targets1 = 0;
			refresh_field('accomplished_targets1', d.name, 'work_changes');
		}
		//find remaining work
		d.remaining_targets = (d.work_targets - d.accomplished_targets1);
		refresh_field('remaining_targets', d.name, 'work_changes');
	}
	else{
		d.remaining_targets = d.work_targets;
		refresh_field('remaining_targets', d.name, 'work_changes');
	}

}

//make read only after save

frappe.ui.form.on("Work Plan Review", "refresh", function(frm){
	frm.set_df_property("start_date", "read_only", frm.doc.__islocal ? 0:1);
});

frappe.ui.form.on("Work Plan Review", "refresh", function(frm){
	frm.set_df_property("end_date", "read_only", frm.doc.__islocal ? 0:1);
});


frappe.ui.form.on("Work Plan Review", "refresh", function(frm){
	frm.set_df_property("work_plan", "read_only", frm.doc.__islocal ? 0 :1);
});


frappe.ui.form.on("Work Plan Review", "refresh", function(frm){
	frm.set_df_property("employee", "read_only", frm.doc.__islocal ? 0 :1);
});


frappe.ui.form.on("Work Plan Review", "refresh", function(frm){
	frm.set_df_property("leave_approver", "read_only", frm.doc.__islocal ? 0 :1);
});


	//make read only for child table work plan




// frappe.ui.form.on("Work Plan Review", "plan_template_on_form_rendered", function(frm, grid_row, cdt, cdn){
// 	var grid_row = cur_frm.open_grid_row();
// 	if(grid_row.doc.kra){
// 		grid_row.grid_form.fields_dict.kra.df.read_only = true;
// 		grid_row.grid_form.fields_dict.kra.refresh();
// 	}
// });

// frappe.ui.form.on("Work Plan Review", "onload", function(frm, grid_row, cdt, cdn){
// 	frm.set_df_property("Appraisal Plan Goal", "read_only", 1);

// });

frappe.ui.form.on("Work Plan Review", "onload", function(frm, grid_row, cdt, cdn){
	var df = frappe.meta.get_docfield("Appraisal Plan Goal", "kra", cur_frm.doc.name);
	df.read_only = 1;


});

frappe.ui.form.on("Work Plan Review", "onload", function(frm, grid_row, cdt, cdn){
	var df = frappe.meta.get_docfield("Appraisal Plan Goal", "deadline", cur_frm.doc.name);
	df.read_only = 1;

});

frappe.ui.form.on("Work Plan Review", "onload", function(frm, grid_row, cdt, cdn){
	var df = frappe.meta.get_docfield("Appraisal Plan Goal", "work_target", cur_frm.doc.name);
	df.read_only = 1;

});


frappe.ui.form.on("Work Plan Review", "onload", function(frm, grid_row, cdt, cdn){
	var df = frappe.meta.get_docfield("Appraisal Plan Goal", "per_weightage", cur_frm.doc.name);
	df.read_only = 1;
});


//make read only when workflow status = Accepted in work plan (accomplished_target)

frappe.ui.form.on("Work Plan Review", "onload", function(frm, grid_row, cdt, cdn){	
	if(frm.doc.workflow_state === "Accepted"){
		var df = frappe.meta.get_docfield("Appraisal Plan Goal","accomplished_target1", cur_frm.doc.name);
		df.read_only = 1;
		
	}
});





// make read only after workflow status = approved in change work Plan



frappe.ui.form.on("Work Plan Review", "onload", function(frm, grid_row, cdt, cdn){
	if(frm.doc.workflow_state === "Accepted"){
		var df = frappe.meta.get_docfield("Appraisal Plan Goals", "kra", cur_frm.doc.name);
		df.read_only = 1;
	
	}
});



frappe.ui.form.on("Work Plan Review", "onload", function(frm, grid_row, cdt, cdn){
	if(frm.doc.workflow_state === "Accepted"){
		var df = frappe.meta.get_docfield("Appraisal Plan Goals", "work_targets", cur_frm.doc.name);
		df.read_only = 1;
	}
});

frappe.ui.form.on("Work Plan Review", "onload", function(frm, grid_row, cdt, cdn){
	if(frm.doc.workflow_state === "Accepted"){
		var df = frappe.meta.get_docfield("Appraisal Plan Goals", "deadline", cur_frm.doc.name);
		df.read_only = 1;
	}
});

frappe.ui.form.on("Work Plan Review", "onload", function(frm, grid_row, cdt, cdn){
	if(frm.doc.workflow_state === "Accepted"){
		var df = frappe.meta.get_docfield("Appraisal Plan Goals", "accomplished_targets1", cur_frm.doc.name);
		df.read_only = 1;
	}
});


frappe.ui.form.on("Work Plan Review", "onload", function(frm, grid_row, cdt, cdn){
	if(frm.doc.workflow_state === "Accepted"){
		var df = frappe.meta.get_docfield("Appraisal Plan Goals", "per_weightage", cur_frm.doc.name);
		df.read_only = 1;
	}
});



//make read only in parents table when workflow status = Approved

frappe.ui.form.on("Work Plan Review", "refresh", function(frm){
	//var cur_frm.();
	if(frm.doc.workflow_state === "Accepted"){
		frm.set_df_property("employee_comments", "read_only", frm.doc.__islocal ? 0 :1);
	}	
});


frappe.ui.form.on("Work Plan Review", "refresh", function(frm){
	//var cur_frm.();
	if(frm.doc.workflow_state === "Accepted"){
		frm.set_df_property("supervisor_comments", "read_only", frm.doc.__islocal ? 0 :1);
	}	
});












