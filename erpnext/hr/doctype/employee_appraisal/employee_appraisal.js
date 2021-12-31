// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


cur_frm.add_fetch('employee', 'company', 'company');
cur_frm.add_fetch('employee', 'employee_name', 'employee_name');
cur_frm.add_fetch("employee", "employee_subgroup", "grade")
cur_frm.add_fetch("employee", "designation", "designation")
cur_frm.add_fetch("employee", "branch", "branch")


frappe.ui.form.on('Employee Appraisal', {
	refresh: function(frm) {
		if(!frm.doc.__islocal){
			frm.set_df_property("goals", "read_only", 1);
		}


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
				filters: {
					workflow_state: 'Accepted',
				}
			};
		});
	},


	leave_approver: function(frm){
		if(frm.doc.leave_approver){
			frm.set_value("leave_approver_name", frappe.user.full_name(frm.doc.leave_approver));
		}
	},

	reviewer: function(frm) {
		if(frm.doc.reviewer){
			frm.set_value("reviewer_name", frappe.user.full_name(frm.doc.reviewer));
		
		}
	},
});



cur_frm.cscript.refresh = function(doc, cdt, cdn){

}


//to fetch work plan review

cur_frm.cscript.work_plan = function(doc, cdt, cdn){
	doc.plan_template = [];
	doc.work_changes = [];
	erpnext.utils.map_current_doc({
		method: "erpnext.hr.doctype.employee_appraisal.employee_appraisal.fetch_work_plan_review",
		source_name: cur_frm.doc.work_plan,
		frm: cur_frm
	});
}



//to fetch appraisal template
cur_frm.cscript.kra_template = function(doc, cdt, cdn){
	doc.rating_guide_template = [];
	doc.goals = [];//remove retra row
	doc.achievement = [];
	doc.rating = [];
	doc.review = [];
	doc.review_discussion = [];
	erpnext.utils.map_current_doc({
		method: "erpnext.hr.doctype.employee_appraisal.employee_appraisal.fetch_appraisal_template",
		source_name: cur_frm.doc.kra_template,
		frm: cur_frm
	});
}


//work plan calculation in group A

cur_frm.cscript.accomplished_target = function(doc, cdt, cdn){
	var d = locals[cdt][cdn];
	var vil = doc.plan_template || [];
	var totals = 0;
	if (d.accomplished_target){
		if (flt(d.accomplished_target) > d.work_target) {
			msgprint(__("Work complated must be less than or equal to Work Target"));
			d.accomplished_target = 0;
			refresh_field('accomplished_target', d.name, 'plan_template');
		}

		d.remaining_target = (d.work_target - d.accomplished_target);
		refresh_field('remaining_target', d.name, 'plan_template');
	}
	else{
		d.remaining_target = d.work_target;
		refresh_field('remaining_target', d.name, 'plan_template');
	}
	d.score = flt((d.accomplished_target) * flt(d.per_weightage)) / flt(d.work_target);
	refresh_field('score', d.name, 'plan_template');

	for (var i = 0; i<vil.length; i++){
		totals = flt(totals) + flt(vil[i].score);
	}
	doc.achievement_score = flt((totals) * 70/100);
	refresh_field('achievement_score');

	cur_frm.cscript.calculate_total1(doc, cdt, cdn);
	
	//cur_frm.cscript.calculate_total1(doc, cdt, cdn);
	
	frappe.ui.form.on("Employee Appraisal", "validate", function(frm,cdt,cdn){
		var c = locals[cdt][cdn].rating;
		c[0].weighted_score = flt(cur_frm.doc.total_supervisor);
		c[1].weighted_score = flt(cur_frm.doc.achievement_score);
		c[2].weighted_score = flt(cur_frm.doc.total_supervisor) + flt(cur_frm.doc.achievement_rating) + 
		flt(cur_frm.doc.achievement_score);
		cur_frm.refresh_field('rating');

	});

	doc.final_rating =  flt(doc.total_supervisor) + flt(doc.achievement_score);
	refresh_field('final_rating');
	
}

//work changes for Group A
cur_frm.cscript.accomplished_targets = function(doc, cdt, cdn){
	var d = locals[cdt][cdn];
	var vil = doc.work_changes || [];
	var totals = 0;

	if (d.accomplished_targets){
		if (flt(d.accomplished_targets) > d.work_targets) {
			msgprint(__("Work complated must be less than or equal to work Target"));
			d.accomplished_targets = 0;
			refresh_field ('accomplished_targets', d.name, 'work_changes');
		}
		
		d.remaining_targets = (d.work_targets - d.accomplished_targets);
		refresh_field('remaining_targets', d.name, 'work_changes');

	} 
	else{
		d.remaining_targets = d.work_targets;
		refresh_field('remaining_targets', d.name, 'work_changes');

	}
	d.score_changes = flt((d.accomplished_targets) * flt(d.per_weightage)) / flt(d.work_targets);
	refresh_field('score_changes', d.name, 'work_changes');

	for (var i = 0; i<vil.length; i++){
		totals = flt(totals) + flt(vil[i].score_changes);
	}
	doc.achievement_score = flt((totals) * 70)/100;
	refresh_field('achievement_score');

	cur_frm.cscript.calculate_total1(doc, cdt, cdn);
	//cur_frm.cscript.accomplished_targets(doc, cdt, cdn);
	//cur_frm.cscript.calculate_total1(doc, cdt, cdn);
	
	frappe.ui.form.on("Employee Appraisal", "validate", function(frm,cdt,cdn){
		var c = locals[cdt][cdn].rating;
		c[0].weighted_score = flt(cur_frm.doc.total_supervisor);
		c[1].weighted_score = flt(cur_frm.doc.achievement_score);
		c[2].weighted_score = flt(cur_frm.doc.total_supervisor) + flt(cur_frm.doc.achievement_rating) + 
		flt(cur_frm.doc.achievement_score);
		cur_frm.refresh_field('rating');

	});
	
	doc.final_rating = flt(doc.total_supervisor) + flt(doc.achievement_score);
	refresh_field('final_rating');


}

//total on achievement code anable

//cur_frm.cscript.calculate_total2 = function(doc, cdt, cdn){
//	var vil = doc.work_changes || [];
//	var weighted_score = 0;
//	var total2 = 0;
//	for (var i = 0; i<vil.length; i++){
//		total2 = flt(total2) + flt(vil[i].score_changes);
//	}
//	doc.achievement_score = flt(total2);
//	refresh_field('achievement_score');

	//cur_frm.cscript.calculate_total1(doc, cdt, cdn)

	//frappe.ui.form.on("Employee Appraisal", "validate", function(frm,cdt,cdn){
	//	var c = locals[cdt][cdn].rating;
	//	c[0].weighted_score = flt(cur_frm.doc.total_supervisor);
	//	c[1].weighted_score = flt(cur_frm.doc.achievement_score);
	//	cur_frm.refresh_field('rating');

	//});

	//doc.final_rating = flt(doc.total_supervisor) + flt(doc.achievement_score);
	//refresh_field('final_rating');
//}




//self score in competencies for both group A and B
cur_frm.cscript.score = function(doc, cdt, cdn){
	var d = locals[cdt][cdn];
	if (d.score){
		if (flt(d.score) > d.per_weightage) {
			msgprint(__("score must be less than or equal to Weightage"));
			d.score = 0;
			refresh_field('score', d.name, 'goals');
		}

		d.score_earned = d.score;
		refresh_field('score_earned', d.name, 'goals');
	}
	cur_frm.cscript.calculate_total(doc, cdt,cdn);
}

cur_frm.cscript.calculate_total = function(doc, cdt, cdn){
	var val = doc.goals || [];
	var total = 0;
	for(var i = 0; i<val.length; i++){
		total = flt(total)+flt(val[i].score_earned);
	}
	doc.self_score = flt(total);
	refresh_field('self_score');
}

//score by supervisor in competencies both A and B

cur_frm.cscript.score_supervisor =  function(doc, cdt, cdn){
	var b = locals[cdt][cdn];
	if (b.score_supervisor){
		if (flt(b.score_supervisor) > b.per_weightage){
			msgprint(__("Score must be less than or equal to Weightage"));
			b.score_supervisor = 0;
			refresh_field('score_supervisor', b.name, 'goals');
		}
		b.earned_supervisor = b.score_supervisor;
		refresh_field('earned_supervisor', b.name, 'goals')
		
	}
	else{
		b.earned_supervisor = 0;
		refresh_field('earned_supervisor', b.name, 'goals');
	}
	cur_frm.cscript.calculate_total1(doc, cdt, cdn);
	
	cur_frm.cscript.accomplished_target(doc, cdt, cdn);
	//cur_frm.cscript.accomplished_targets(doc, cdt, cdn);
//additional code
	frappe.ui.form.on("Employee Appraisal", "validate", function(frm,cdt,cdn){
		var c = locals[cdt][cdn].rating;
		c[0].weighted_score = flt(cur_frm.doc.total_supervisor);
		//achievement_ratting is for group B
		c[1].weighted_score = flt(cur_frm.doc.achievement_rating) + flt(cur_frm.doc.achievement_score) ;
		
		c[2].weighted_score = flt(cur_frm.doc.total_supervisor) + flt(cur_frm.doc.achievement_rating) + 
		flt(cur_frm.doc.achievement_score);
		cur_frm.refresh_field('rating');

	});
	// addition for group A and achievement_score field is for Group A
	doc.final_rating = flt(doc.total_supervisor) + flt(doc.achievement_score);
	refresh_field('final_rating');
	//addition for group B and achievement_rating field is for Group A
	doc.final_rating = flt(doc.total_supervisor) + flt(doc.achievement_rating);
	refresh_field('final_rating');

}

//total by supervisor in competencies in group B n A

cur_frm.cscript.calculate_total1 = function(doc, cdt, cdn){
	var vel = doc.goals || [];
	var total1 = 0;
	for (var i = 0; i<vel.length; i++){
		total1 = flt(total1)+flt(vel[i].score_supervisor);
	}
	doc.total_supervisor = flt(total1);
	refresh_field('total_supervisor');

	//to calculate final total rating
	//cur_frm.cscript.accomplished_targets(doc, cdt, cdn);
	//cur_frm.cscript.accomplished_target(doc, cdt, cdn);
	//cur_frm.cscript.calculate_total2(doc, cdt, cdn);

	frappe.ui.form.on("Employee Appraisal", "validate", function(frm,cdt,cdn){
		var c = locals[cdt][cdn].rating;
		c[0].weighted_score = flt(cur_frm.doc.total_supervisor);
		c[1].weighted_score = flt(cur_frm.doc.achievement_score) + flt(cur_frm.doc.achievement_rating);
		c[2].weighted_score = flt(cur_frm.doc.total_supervisor) + flt(cur_frm.doc.achievement_rating) + 
		flt(cur_frm.doc.achievement_score);
		cur_frm.refresh_field('rating');

	});

	// addition for group A
	doc.final_rating = flt(doc.total_supervisor) + flt(doc.achievement_score);
	refresh_field('final_rating');

	//addition for group B
	doc.final_rating = flt(doc.total_supervisor) + flt(doc.achievement_rating);
	refresh_field('final_rating');	
}




//self rating  in achievement on Group B

cur_frm.cscript.self_score = function(doc, cdt, cdn){
	var d = locals[cdt][cdn];
	if (d.self_score){
		if (flt(d.self_score) > d.per_weightage) {
			msgprint(__("Score must be less than or equal to Weightage"));
			d.self_score = 0;
			refresh_field('self_score', d.name, 'achievement');

		}
		d.earned_self = d.self_score;
		refresh_field('earned_self', d.name, 'achievement');
	}
	else{
		d.earned_self = 0;
		refresh_field('earned_self', d.name, 'achievement');
	}
	cur_frm.cscript.calculate_total2(doc,cdt,cdn);
}


//supervisor in achievement in Group B

cur_frm.cscript.score_supervisors =  function(doc, cdt, cdn){
	var c = locals[cdt][cdn];
	if (c.score_supervisors){
		if (flt(c.score_supervisors) > c.per_weightage){
			msgprint(__("Score must be less than or equal to Weightage"));
			c.score_supervisors = 0;
			refresh_field('score_supervisors', c.name, 'achievement');
		}
		c.earned_supervisors = c.score_supervisors;
		refresh_field('earned_supervisors', c.name, 'achievement');

	}
	else{
		c.earned_supervisors = 0;
		refresh_field('earned_supervisors', c.name, 'achievement');
	}
	cur_frm.cscript.calculate_total2(doc, cdt, cdn);
	doc.final_rating = flt(doc.total_supervisor) + flt(doc.achievement_rating);
	refresh_field('final_rating');
	
}


//total on achievement for Group B

cur_frm.cscript.calculate_total2 = function(doc,cdt, cdn){
	var vil = doc.achievement || [];
	var weighted_score = 0;
	var total2 = 0;
	for (var i = 0; i<vil.length; i++){
		total2 = flt(total2) + flt(vil[i].score_supervisors);
	}
	doc.achievement_rating = flt(total2);
	refresh_field('achievement_rating');

	frappe.ui.form.on("Employee Appraisal", "validate", function(frm,cdt,cdn){
		var c = locals[cdt][cdn].rating;
		c[0].weighted_score = flt(cur_frm.doc.total_supervisor);
		c[1].weighted_score = flt(cur_frm.doc.achievement_rating);
		c[2].weighted_score = flt(cur_frm.doc.total_supervisor) + flt(cur_frm.doc.achievement_rating) + 
		flt(cur_frm.doc.achievement_score);
		cur_frm.refresh_field('rating');

	});

//addition for group B
	doc.final_rating = flt(doc.total_supervisor) + flt(doc.achievement_rating);
	refresh_field('final_rating');

}



//fetch previous employee training 
//cur_frm.cscript.previous_training = function(doc, cdt, cdn){
//	doc.training = [];
//	erpnext.utils.map_current_doc({
//		method: "erpnext.hr.doctype.employee_appraisal.employee_appraisal.fetch_appraisal_training",
//		source_name: cur_frm.doc.previous_training,
//		frm: cur_frm
//	});
//}






//make read only after save data. field is employee
frappe.ui.form.on("Employee Appraisal", "refresh", function(frm){
	frm.set_df_property("work_plan", "read_only", frm.doc.__islocal ? 0 :1);
});

frappe.ui.form.on("Employee Appraisal", "refresh", function(frm){
	frm.set_df_property("employee", "read_only", frm.doc.__islocal ? 0 :1);

});

frappe.ui.form.on("Employee Appraisal", "refresh", function(frm){
	frm.set_df_property("leave_approver", "read_only", frm.doc.__islocal ? 0 :1);

});
frappe.ui.form.on("Employee Appraisal", "refresh", function(frm){
	frm.set_df_property("kra_template", "read_only", frm.doc.__islocal ? 0 :1);

});

frappe.ui.form.on("Employee Appraisal", "refresh", function(frm){
	frm.set_df_property("start_date", "read_only", frm.doc.__islocal ? 0 :1);

});

frappe.ui.form.on("Employee Appraisal", "refresh", function(frm){
	frm.set_df_property("end_date", "read_only", frm.doc.__islocal ? 0 :1);

});

frappe.ui.form.on("Employee Appraisal", "refresh", function(frm){
	frm.set_df_property("reviewer", "read_only", frm.doc.__islocal ? 0 :1);

});

frappe.ui.form.on("Employee Appraisal", "refresh", function(frm){
	frm.set_df_property("reviewer", "read_only", frm.doc.__islocal ? 0 :1);

});


frappe.ui.form.on("Employee Appraisal", "refresh", function(frm){
	frm.set_df_property("employee_comments", "read_only", frm.doc.__islocal ? 0 :1);
});






//make kra of appraisal goal child table filed readonly
frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Goal", "kra", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("goals");
	
});


//make per_weightage of appraisal Goal child table filed readonly 
frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Goal", "per_weightage", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("goals");
	
});





//make read only in child table field: score (self ratting) whan status is waiting submiting in Competancies

frappe.ui.form.on("Employee Appraisal", "goals_on_form_rendered", function(frm, grid_row, cdt, cdn){
	var grid_row = cur_frm.open_grid_row();
	if(frm.doc.workflow_state === "Waiting for Submitting"){
		grid_row.grid_form.fields_dict.score.df.read_only = true;
		grid_row.grid_form.fields_dict.score.refresh();
	}
});

frappe.ui.form.on("Employee Appraisal", "goals_on_form_rendered", function(frm, grid_row, cdt, cdn){
	var grid_row = cur_frm.open_grid_row();
	if(frm.doc.workflow_state === "Re-Check"){
		grid_row.grid_form.fields_dict.score.df.read_only = true;
		grid_row.grid_form.fields_dict.score.refresh();
	}
});
//make read only in child table field (score) when status is Waiting Acceptance
frappe.ui.form.on("Employee Appraisal", "goals_on_form_rendered", function(frm, grid_row, cdt, cdn){
	var grid_row = cur_frm.open_grid_row();
	if(frm.doc.workflow_state === "Waiting for Acceptance"){
		grid_row.grid_form.fields_dict.score.df.read_only = true;
		grid_row.grid_form.fields_dict.score.refresh();
	}
});


frappe.ui.form.on("Employee Appraisal", "goals_on_form_rendered", function(frm, grid_row, cdt, cdn){
	var grid_row = cur_frm.open_grid_row();
	if(frm.doc.workflow_state === "Waiting for Acceptance"){
		grid_row.grid_form.fields_dict.score_supervisor.df.read_only = true;
		grid_row.grid_form.fields_dict.score_supervisor.refresh();
	}
});






//Achievement

frappe.ui.form.on("Employee Appraisal", "achievement_on_form_rendered", function(frm, grid_row, cdt, cdn){
	var grid_row = cur_frm.open_grid_row();
	if(frm.doc.workflow_state === "Waiting for Submitting"){
		grid_row.grid_form.fields_dict.self_score.df.read_only = true;
		grid_row.grid_form.fields_dict.self_score.refresh();
	}
});


frappe.ui.form.on("Employee Appraisal", "achievement_on_form_rendered", function(frm, grid_row, cdt, cdn){
	var grid_row = cur_frm.open_grid_row();
	if(frm.doc.workflow_state === "Waiting for Acceptance"){
		grid_row.grid_form.fields_dict.self_score.df.read_only = true;
		grid_row.grid_form.fields_dict.self_score.refresh();
	}
});

frappe.ui.form.on("Employee Appraisal", "achievement_on_form_rendered", function(frm, grid_row, cdt, cdn){
	var grid_row = cur_frm.open_grid_row();
	if(frm.doc.workflow_state === "Re-Check"){
		grid_row.grid_form.fields_dict.self_score.df.read_only = true;
		grid_row.grid_form.fields_dict.self_score.refresh();
	}
});


frappe.ui.form.on("Employee Appraisal", "achievement_on_form_rendered", function(frm, grid_row, cdt, cdn){
	var grid_row = cur_frm.open_grid_row();
	if(frm.doc.workflow_state === "Waiting for Acceptance"){
		grid_row.grid_form.fields_dict.score_supervisors.df.read_only = true;
		grid_row.grid_form.fields_dict.score_supervisors.refresh();
	}
});



//work plan
//frappe.ui.form.on("Employee Appraisal", "plan_template_on_form_rendered", function(frm, grid_row, cdt, cdn){
//	var grid_row = cur_frm.open_grid_row();
//	if(frm.doc.workflow_state === "Waiting for Submitting"){
//		grid_row.grid_form.fields_dict.accomplished_target.df.read_only =  true;
//		grid_row.grid_form.fields_dict.accomplished_target.refresh();
//	}
//});


frappe.ui.form.on("Employee Appraisal", "plan_template_on_form_rendered", function(frm, grid_row, cdt, cdn){
	var grid_row = cur_frm.open_grid_row();
	if(frm.doc.workflow_state === "Waiting for Acceptance"){
		grid_row.grid_form.fields_dict.accomplished_target.df.read_only =  true;
		grid_row.grid_form.fields_dict.accomplished_target.refresh();
	}
});


//make read only when workflow status = approved in Appraisal (accomplished_target)in work plan
frappe.ui.form.on("Employee Appraisal", "work_changes_on_form_rendered", function(frm, grid_row, cdt, cdn){
	var grid_row = cur_frm.open_grid_row();
	if(frm.doc.workflow_state === "Waiting for Acceptance"){
		grid_row.grid_form.fields_dict.accomplished_targets.df.read_only = true;
		grid_row.grid_form.fields_dict.accomplished_targets.refresh();
	}
});


//make kra of appraisal goals child table filed readonly  add by kinzang.
frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Goals", "kra", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("achievement");
	
});

//make per_weightage of appraisal Goal child table filed readonly  add by kinzang.
frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Goals", "per_weightage", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("achievement");
});



//make read only work plan
frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Plan Goal", "kra", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("plan_template");
	
});

frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Plan Goal", "per_weightage", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("plan_template");
	
});

frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Plan Goal", "work_target", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("plan_template");
	
});

frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Plan Goal", "deadline", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("plan_template");
	
});

frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Plan Goal", "accomplished_target1", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("plan_template");
	
});


/*
frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Plan Goal", "accomplished_target", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("plan_template");
	
});
*/

//make read only work plan changes
frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Plan Goals", "kra", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("plan_template");
	
});

frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Plan Goals", "per_weightage", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("work_changes");
	
});
frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Plan Goals", "accomplished_targets1", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("work_changes");
	
});


frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Plan Goals", "work_targets", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("work_changes");
	
});

frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Plan Goals", "deadline", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("work_changes");
	
});


frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Rating", "kra", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("rating");
	
});

frappe.ui.form.on("Employee Appraisal", "onload", function(frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Appraisal Rating", "weightage", cur_frm.doc.name);
	df.read_only= 1;
	frm.refresh_field("rating");
	
});


frappe.ui.form.on("Employee Appraisal", "onload", function (frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Rating Guide Template", "adjective_rating", cur_frm.doc.name);
	df.read_only = 1;
	frm.refresh_field("rating_guide_template");
});

frappe.ui.form.on("Employee Appraisal", "onload", function (frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Rating Guide Template", "rating", cur_frm.doc.name);
	df.read_only = 1;
	frm.refresh_field("rating_guide_template");
});

frappe.ui.form.on("Employee Appraisal", "onload", function (frm, cdt, cdn) {
	var df = frappe.meta.get_docfield("Rating Guide Template", "explanation", cur_frm.doc.name);
	df.read_only = 1;
	frm.refresh_field("rating_guide_template");
});

frappe.ui.form.on("Employee Appraisal", "onload", function (frm, cdt, cdn){
	var df = frappe.meta.get_docfield("Review Question", "answer", cur_frm.doc.name);
	df.read_only = 1;
	frm.refresh_field("review");
});

frappe.ui.form.on("Employee Appraisal", "onload", function (frm, cdt, cdn){
	var df = frappe.meta.get_docfield("Review Discussion", "answer", cur_frm.doc.name);
	df.read_only = 1;
	frm.refresh_field("review_discussion");
});
