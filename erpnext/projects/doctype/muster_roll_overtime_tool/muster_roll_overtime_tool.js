frappe.ui.form.on("Muster Roll Overtime Tool", {
	refresh: function(frm) {
		frm.disable_save();
	},
	
	onload: function(frm) {
		frm.set_value("date", get_today());
	},

	number_of_hours: function(frm) {
		erpnext.muster_roll_overtime_tool.load_employees(frm);
	},

	project: function(frm) {
		erpnext.muster_roll_overtime_tool.load_employees(frm);
	},

	date: function(frm) {
		erpnext.muster_roll_overtime_tool.load_employees(frm);
	},
});


erpnext.muster_roll_overtime_tool = {
	load_employees: function(frm) {
		if(frm.doc.project && frm.doc.date && frm.doc.number_of_hours) {
			frappe.call({
				method: "erpnext.projects.doctype.muster_roll_overtime_tool.muster_roll_overtime_tool.get_employees",
				args: {
					project: frm.doc.project,
					date: frm.doc.date,
					number_of_hours: frm.doc.number_of_hours,
				},
				callback: function(r) {
					if(r.message['unmarked'].length > 0) {
						unhide_field('unmarked_attendance_section')
						if(!frm.employee_area) {
							frm.employee_area = $('<div>')
							.appendTo(frm.fields_dict.employees_html.wrapper);
						}
						frm.EmployeeSelector = new erpnext.EmployeeSelector(frm, frm.employee_area, r.message['unmarked'])
					}
					else{
						hide_field('unmarked_attendance_section')
					}

					if(r.message['marked'].length > 0) {
						unhide_field('marked_attendance_section')
						if(!frm.marked_employee_area) {
							frm.marked_employee_area = $('<div>')
								.appendTo(frm.fields_dict.marked_attendance_html.wrapper);
						}
						frm.marked_employee = new erpnext.MarkedEmployee(frm, frm.marked_employee_area, r.message['marked'])
					}
					else{
						hide_field('marked_attendance_section')
					}
				}
			});
		}
	}
}

erpnext.MarkedEmployee = Class.extend({
	init: function(frm, wrapper, employee) {
		this.wrapper = wrapper;
		this.frm = frm;
		this.make(frm, employee);
	},
	make: function(frm, employee) {
		var me = this;
		$(this.wrapper).empty();

		var row;
		$.each(employee, function(i, m) {
			var attendance_icon = "icon-check";
			var color_class = "";
			if(m.status == "Absent") {
				attendance_icon = "icon-check-empty"
				color_class = "text-muted";
			}

			if (i===0 || i % 4===0) {
				row = $('<div class="row"></div>').appendTo(me.wrapper);
			}

			$(repl('<div class="col-sm-3 %(color_class)s">\
				<label class="marked-employee-label"><span class="%(icon)s"></span>\
				%(employee)s (%(id)s)</label>\
				</div>', {
					employee: m.person_name,
					id: m.name,
					icon: attendance_icon,
					color_class: color_class
				})).appendTo(row);
		});
	}
});


erpnext.EmployeeSelector = Class.extend({
	init: function(frm, wrapper, employee) {
		this.wrapper = wrapper;
		this.frm = frm;
		this.make(frm, employee);
	},
	make: function(frm, employee) {
		var me = this;

		$(this.wrapper).empty();
		var employee_toolbar = $('<div class="col-sm-12 top-toolbar">\
			<button class="btn btn-default btn-add btn-xs"></button>\
			<button class="btn btn-xs btn-default btn-remove"></button>\
			</div>').appendTo($(this.wrapper));

		var mark_employee_toolbar = $('<div class="col-sm-12 bottom-toolbar">\
			<button class="btn btn-primary btn-mark-present btn-xs"></button>\
			<button class="btn btn-default btn-mark-absent btn-xs"></button></div>')

		employee_toolbar.find(".btn-add")
			.html(__('Check all'))
			.on("click", function() {
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if(!$(check).is(":checked")) {
						check.checked = true;
					}
				});
			});

		employee_toolbar.find(".btn-remove")
			.html(__('Uncheck all'))
			.on("click", function() {
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if($(check).is(":checked")) {
						check.checked = false;
					}
				});
			});

		mark_employee_toolbar.find(".btn-mark-present")
			.html(__('Allocate Overtime'))
			.on("click", function() {
				var employee_present = [];
				$(me.wrapper).find('input[type="checkbox"]').each(function(i, check) {
					if($(check).is(":checked")) {
						employee_present.push(employee[i]);
					}
				});
				if(frm.doc.number_of_hours > 0) {
					frappe.call({
						method: "erpnext.projects.doctype.muster_roll_overtime_tool.muster_roll_overtime_tool.allocate_overtime",
						args:{
							"employee_list":employee_present,
							"project":frm.doc.project,
							"date": frm.doc.date,
							"purpose": frm.doc.purpose,
							"number_of_hours": frm.doc.number_of_hours,
						},

						callback: function(r) {
							erpnext.muster_roll_overtime_tool.load_employees(frm);

						}
					});
				}
				else {frappe.msgprint("Number of Hours should be greater than 0")}
			});

		var row;
		$.each(employee, function(i, m) {
			if (i===0 || (i % 4) === 0) {
				row = $('<div class="row"></div>').appendTo(me.wrapper);
			}

			$(repl('<div class="col-sm-3 unmarked-employee-checkbox">\
				<div class="checkbox">\
				<label><input type="checkbox" class="employee-check" employee="%(employee)s"/>\
				%(employee)s (%(id)s)</label>\
				</div></div>', {employee: m.person_name, id:m.name})).appendTo(row);
		});

		mark_employee_toolbar.appendTo($(this.wrapper));
	}
});


