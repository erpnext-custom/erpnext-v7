// Ver 20160701.1 by SSK, Original Version

cur_frm.cscript.onload = function(doc,cdt,cdn) {
    var internal = "Internal Vacancy Announcement"
    var external = "Job Advertisements on Media\nInter-Corporate Transfer\nCampus Recruitment"

    if (!cur_frm.fields_dict.type_of_recruitment.value){
        frappe.model.set_value(cdt, cdn, "type_of_vacancy", "External");
        cur_frm.fields_dict.type_of_recruitment.df.options = external;
        frappe.model.set_value(cdt, cdn, "type_of_recruitment", "Job Advertisements on Media");
    }
}

// Custom values for SELECT type
frappe.ui.form.on('Job Opening', 'type_of_vacancy', function(frm, cdt, cdn){
    var internal = "Internal Vacancy Announcement"
    var external = "Job Advertisements on Media\nInter-Corporate Transfer\nCampus Recruitment"

    if (cur_frm.fields_dict.type_of_vacancy.value == 'Internal'){
        cur_frm.fields_dict.type_of_recruitment.df.options = internal;
        frappe.model.set_value(cdt, cdn, "type_of_recruitment", "Internal Vacancy Announcement");
    }
    else
    {
        cur_frm.fields_dict.type_of_recruitment.df.options = external;
        frappe.model.set_value(cdt, cdn, "type_of_recruitment", "Job Advertisements on Media");
    }
    refresh_field('type_of_recruitment');
});

// Ver 20160701.1 by SSK, Original Version

// Terms and Conditions population
frappe.ui.form.on("Job Opening Item", "hr_terms", function(frm, cdt, cdn) {
	var child = locals[cdt][cdn];
        frappe.model.get_value("Terms of Reference", child.hr_terms, "hr_terms", function(value) {
                    frappe.model.set_value(cdt, cdn, "hr_terms_desc", value.hr_terms);
		});
});
