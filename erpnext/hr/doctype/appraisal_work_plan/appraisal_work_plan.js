// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('employee', 'employee_name', 'employee_name');
cur_frm.add_fetch("employee", "employee_subgroup", "grade")
cur_frm.add_fetch("employee", "designation", "designation")
cur_frm.add_fetch("employee", "branch", "branch")

frappe.ui.form.on('Appraisal Work Plan', {
	onload: function(frm){
		frm.set_query("leave_approver", function() {
		return {
			query: "erpnext.hr.doctype.leave_application.leave_application.get_approvers",
			filters: {
				employee: frm.doc.employee
			}
		};
	});
		if(!frm.doc.posting_date){
			cur_frm.set_value("posting_date", get_today())
		}
	},		
	
	// to get leave approvel name when above code selected approval email
	leave_approver: function(frm) {
		if(frm.doc.leave_approver){
			frm.set_value("leave_approver_name", frappe.user.full_name(frm.doc.leave_approver));
		}
		
	},

	//to get reviewer name when we select email from user table
	reviewer: function(frm){
		if(frm.doc.reviewer){
			frm.set_value("reviewer_name", frappe.user.full_name(frm.doc.reviewer));
		}
	},

});
/*
cur_frm.cscript.onload = function(doc,cdt,cdn){
	if(!doc.status)
		set_multiple(cdt,cdn,{status:'Draft'});
	if(doc.amended_from && doc.__islocal) {
		doc.status = "Draft";
	}
}
*/


cur_frm.cscript.refresh = function(doc,cdt,cdn){

}





/*


//calculate totale score by supervisor
cur_frm.cscript.calculate_total = function(doc,cdt,cdn){
	var vel = doc.goals || [];
	var total = 0;
	for (var i = 0; i<vel.length; i++){
		total = flt(total)+flt(vel[i].accomplished_target);
	}
	doc.total_work_completed = flt(total);
	refresh_field('total_work_completed');

}


/*
frappe.ui.form.on("Appraisal Plan Goal", "work_completed", function(frm, cdt, cdn) {
	var total = 0;
	$.each(frm.doc.appraisal_plan_goal || [], function (i, d) {
		total += flt(d.work_completed);
	});
	frm.set_value("total_work_completed", total);
});
*/
/*

frappe.ui.form.on("Appraisal Work Plan", "accomplished_target", function(frm, cdt,cdn){
	var d = locals[cdt][cdn];

frappe.model.set_value(d.doctype, d.name, "remaining_target", flt(100 - d.accomplished_target));
 frm.set_value("remaining_target", "remaining_target");
});

*/



/*
cur_frm.cscript.accomplished_target = function(doc, cdt, cdn){
	var b = locals[cdt][cdn];
	if (b.accomplished_target){
		if (flt(b.accomplished_target) > 100){
			msgprint(__("Accomplished target should not more that 100%"));
			b.accomplished_target = 0;
			refresh_field('accomplished_target', b.name, 'goals');
		}
	}
}


cur_frm.cscript.work_completed = function(doc, cdt,cdn){
	var b = locals[cdt][cdn];
	if (b.accomplished_target1){
		if (flt(b.accomplished_target1) > b.remaining_target){
			msgprint(__("2nd half Accomplished target should not more than Remaining target of 1st half"));
			b.accomplished_target1 = 0;
			refresh_field('accomplished_target1', b.name, 'goals');
		}
	}
}

*/

/*
//make child table filed readonly after save add by kinzang.
frappe.ui.form.on("Appraisal Work Plan", "onload", function(frm, cdt, cdn) {
	for(var i=0; i<frm.doc.goals.length; i++){

		var child = frm.doc.goals[i];
		var df = frappe.meta.get_docfield(child.doctype, "per_weightage", cur_frm.doc.name);
		df.read_only = frm.doc.__islocal ? 0 : 1;

	}
	refresh_field("goals");

});

*/
//make child table filed readonly after save add by kinzang.
/*
frappe.ui.form.on("Appraisal Work Plan", "onload", function(frm, cdt, cdn) {
	for(var i=0; i<frm.doc.goals.length; i++){

		var child = frm.doc.goals[i];
		var df = frappe.meta.get_docfield(child.doctype, "kra", cur_frm.doc.name);
		df.read_only = frm.doc.__islocal ? 0 : 1;

	}
	refresh_field("goals");

});

*/

//make accomplished child table filed readonly after save add by kinzang.
/*frappe.ui.form.on("Appraisal Work Plan", "onload", function(frm, cdt, cdn) {
	for(var i=0; i<frm.doc.goals.length; i++){

		var child = frm.doc.goals[i];
		var df = frappe.meta.get_docfield(child.doctype, "accomplished_target", cur_frm.doc.name);
		df.read_only = frm.doc.__islocal ? 0 : 1;

	}
	refresh_field("goals");

});

//make accomplished_target1 redaonly
frappe.ui.form.on("Appraisal Work Plan", "onload", function(frm, cdt, cdn) {
	for(var i=0; i<frm.doc.goals.length; i++){

		var child = frm.doc.goals[i];
		var df = frappe.meta.get_docfield(child.doctype, "accomplished_target1", cur_frm.doc.name);
		df.read_only = frm.doc.__islocal ? 0 : 1;

	}
	refresh_field("goals");

});

*/



/*
frappe.ui.form.on("Appraisal Work Plan", "goals_on_form_rendered", function(frm, grid_row, cdt, cdn){
	var grid_row = cur_frm.open_grid_row();
	if(grid_row.doc.verified1 = 0{
		//grid_row.toggle_editable("accomplished_target", 0);
		grid_row.grid_form.fields_dict.accomplished_target.df.read_only = true;
		grid_row.grid_form.fields_dict.accomplished_target.refresh();
	}
});
*/

/*

//to make read and write when Verified check box used
frappe.ui.form.on("Appraisal Work Plan", "goals_on_form_rendered", function(frm, grid_row, cdt, cdn){
	var grid_row = cur_frm.open_grid_row();
	if(grid_row.doc.verified2 == 1){
		grid_row.toggle_editable("kra", 0);
		}
		grid_row.grid_form.fields_dict.kra.refresh();
});

*/


//calculate remaining target 
frappe.ui.form.on("Appraisal Plan Goal", "accomplished_target", function(frm,cdt,cdn){
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "remaining_target", 100 - d.accomplished_target);
	refresh_field("goals");

});


frappe.ui.form.on("Appraisal Plan Goal", "accomplished_target1", function(frm, cdt, cdn){

	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "remaining_target1", 100 - (d.accomplished_target + d.accomplished_target1));
	refresh_field("goals");
});
//calculate the work completed

frappe.ui.form.on("Appraisal Plan Goal", "accomplished_target1", function(frm, cdt, cdn){
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "work_completed", ((d.accomplished_target + d.accomplished_target1) * d.per_weightage)/100);
	refresh_field("goals");
});

frappe.ui.form.on("Appraisal Plan Goal", "work_completed", function(frm, cdt, cdn){
	var d = locals[cdt][cdn];
	frappe.model.set_value(cdt, cdn, "target_remaining", d.per_weightage - d.work_completed);
		refresh_field("goals");
	
});





/*
frappe.ui.form.on("Appraisal Work Plan", "total_score", function(frm, cdt, cdn){
	var total = 0;
	var row_length = cur_frm.doc.goals.length || 0;
	$.each(cur_frm.doc.goals || [], function(i, row){
		total += row.work_completed/row_length;
	});
	cur_frm.set_value("total_score", total)
	
});

*/


/*
frappe.ui.form.on("Appraisal Work Plan", "goals_on_form_rendered", function(frm, grid_row, cdt, cdn){
	var grid_row = cur_frm.open_grid_row();
	if(grid_row.doc.kra){
		grid_row.grid_form.fields_dict.kra.df.read_only = true;
		grid_row.grid_form.fields_dict.kra.refresh();
	}
});
*/


//make read only in child table field: whan status is Approved
 
 /*
frappe.ui.form.on("Appraisal Work Plan", "goals_on_form_rendered", function(frm, grid_row, cdt, cdn){
	var grid_row = cur_frm.open_grid_row();
	if(frm.doc.workflow_state === "Approved"){
		grid_row.grid_form.fields_dict.kra.df.read_only = true;
		grid_row.grid_form.fields_dict.kra.refresh();
	}
});


*/

frappe.ui.form.on("Appraisal Work Plan", "onload", function(frm, cdt,cdn){
	if(frm.doc.workflow_state == "Approved"){
		var df = frappe.meta.get_docfield("Appraisal Plan Goal","kra", cur_frm.doc.name);
		df.read_only = 1;

	}	

});



frappe.ui.form.on("Appraisal Work Plan", "onload", function(frm, grid_row, cdt, cdn){
	if(frm.doc.workflow_state === "Approved"){
		var df = frappe.meta.get_docfield("Appraisal Plan Goal","deadline", cur_frm.doc.name);
		df.read_only = 1;
		
	}
});





frappe.ui.form.on("Appraisal Work Plan", "onload", function(frm, grid_row, cdt, cdn){
	if(frm.doc.workflow_state === "Approved"){
		var df = frappe.meta.get_docfield("Appraisal Plan Goal","work_target", cur_frm.doc.name);
		df.read_only = 1;
		
	}
});






frappe.ui.form.on("Appraisal Work Plan", "onload", function(frm, grid_row, cdt, cdn){
	if(frm.doc.workflow_state === "Approved"){
		var df = frappe.meta.get_docfield("Appraisal Plan Goal","per_weightage", cur_frm.doc.name);
		df.read_only = 1;
	}
});



//make read only in parents table when workflow status = Approved

frappe.ui.form.on("Appraisal Work Plan", "refresh", function(frm){
	//var cur_frm.();
	if(frm.doc.workflow_state === "Approved"){
		frm.set_df_property("employee_comments", "read_only", frm.doc.__islocal ? 0 :1);
	}	
});


frappe.ui.form.on("Appraisal Work Plan", "refresh", function(frm){
	//var cur_frm.();
	if(frm.doc.workflow_state === "Submitted"){
		frm.set_df_property("supervisor_comments", "read_only", frm.doc.__islocal ? 0 :1);
	}	
});



//make read only after save

frappe.ui.form.on("Appraisal Work Plan", "refresh", function(frm){
	frm.set_df_property("employee", "read_only", frm.doc.__islocal ? 0 :1);
});

frappe.ui.form.on("Appraisal Work Plan", "refresh", function(frm){
	frm.set_df_property("start_date", "read_only", frm.doc.__islocal ? 0 :1);
});
frappe.ui.form.on("Appraisal Work Plan", "refresh", function(frm){
	frm.set_df_property("end_date", "read_only", frm.doc.__islocal ? 0 :1);
});

frappe.ui.form.on("Appraisal Work Plan", "refresh", function(frm){
	frm.set_df_property("leave_approver", "read_only", frm.doc.__islocal ? 0 :1);
});