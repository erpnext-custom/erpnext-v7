// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Salary Increment', {
	onload: function(frm){
		if(frm.doc.__islocal){
			frm.set_value("fiscal_year", sys_defaults.fiscal_year);
		}
	},
	
	employee: function(frm){
		/*
		if (frm.doc.employee) {
			frm.trigger("get_employee_payscale");
		}
		*/
		get_employee_payscale(frm.doc);
	},
	
	fiscal_year: function(frm){
		/*
		if (frm.doc.fiscal_year){
			frm.trigger("get_employee_payscale");
		}
		*/
		get_employee_payscale(frm.doc);
	},
	
	month: function(frm){
		/*
		if (frm.doc.month){
			frm.trigger("get_employee_payscale");
		}
		*/
		get_employee_payscale(frm.doc);
	},
	
	
	increment: function(frm){
		var old_basic = flt((frm.doc.old_basic)?frm.doc.old_basic:0);
		var increment = flt((frm.doc.increment)?frm.doc.increment:0);
		
		if (old_basic){
			frm.set_value("new_basic",(old_basic+increment));
		}
	},
	
	/*
	get_employee_payscale: function(frm){
		if(frm.doc.employee && frm.doc.employee_subgroup && frm.doc.fiscal_year && frm.doc.month){
			frappe.call({
				method: "erpnext.hr.doctype.salary_increment.salary_increment.get_employee_payscale",
				args: {
					employee: frm.doc.employee,
					gradecd: frm.doc.employee_subgroup,
					fiscal_year: frm.doc.fiscal_year,
					month: frm.doc.month
				},
				callback: function(r){
					frm.set_value('payscale_minimum',r.message.minimum);
					frm.set_value('payscale_increment',r.message.increment);
					frm.set_value('payscale_maximum',r.message.maximum);
					frm.set_value('old_basic',r.message.old_basic);
					frm.set_value('new_basic',r.message.new_basic);
					frm.set_value('increment',r.message.increment);
					frm.set_value('salary_structure',r.message.salary_structure);
				}
			});			
		}
	}
	*/
});

var get_employee_payscale = function(doc){
	cur_frm.call({
		method: "get_employee_payscale",
		doc: doc
	});
}
