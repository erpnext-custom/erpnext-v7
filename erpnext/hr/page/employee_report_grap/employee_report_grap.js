frappe.provide('frappe.energy_points');
// import { Chart } from ('frappe-charts');
// var chart = undefined;
// frappe.require('frappe-charts', () => {
//     imported_helper = Chart;
// });
// frappe.require('assets/../../../node_modules/', () => {
//     imported_helper = Chart;
// });
// import {Chart} from "../node_modules/frappe-charts/dist/frappe-charts.min.esm.js";
// import {Chart} from "frappe-charts";
frappe.pages['employee-report-grap'].on_page_load = function(wrapper) {

	frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Employee Report'),
	});

	let employee_report = new EmployeeReport(wrapper);
	$(wrapper).bind('show', ()=> {
		employee_report.show();
	});
};

class EmployeeReport {

	constructor(wrapper) {
		this.wrapper = $(wrapper);
		this.page = wrapper.page;
		// this.sidebar = this.wrapper.find('.layout-side-section');
		this.main_section = this.wrapper.find('.layout-main-section');
	}

	show() {
		let route = frappe.get_route();
		this.user_id = route[1] || frappe.session.user;

		//validate if user
		if (route.length > 1) {
			frappe.db.exists('User', this.user_id).then( exists => {
				if (exists) {
					this.make_user_profile();
				} else {
					frappe.msgprint(__('User does not exist'));
				}
			});
		} else {
			this.user_id = frappe.session.user;
			this.make_user_profile();
		}
	}

	make_user_profile() {
		frappe.set_route('employee-report-grap');
		this.user = frappe.user_info(this.user_id);
		// this.page.set_title(this.user.fullname);
		this.setup_transaction_link();
		this.main_section.empty().append(frappe.render_template('employee_report_grap'));
		this.render_graph();
		// this.render_user_details();
		// if(this.user_id != "Administrator"){
		// 	this.basic_emp_info();
		// 	this.employee_work_history();
		// 	this.employee_job_description();
		// 	this.employee_leave_dashboard();
		// 	this.employee_pms_records();
		// 	this.employee_trainings()
		// 	this.disciplinary_records()
		// this.create_attendance_dashboard_filters();
		// this.employee_attendance_dashboard(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
		// "December"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()]);
		// this.checkin_info();
		// }
		// this.render_line_chart();
		// this.render_percentage_chart('type', 'Type Distribution');
		// this.create_percentage_chart_filters();
		// this.setup_show_more_activity();
		// this.render_user_activity();
		// this.setup_punching_button();
		// this.display_time();
	}
	
	setup_transaction_link() {
		this.$user_search_button = this.page.set_secondary_action('<b>Transactions Link</b>', () => {
			frappe.set_route('')
		});
	}

	employee_attendance_dashboard(month) {
		let $attendance_dashboard = this.wrapper.find('.attendance-dashboard');
		let current_year = this.get_year(frappe.datetime.now_date());
		$attendance_dashboard.empty();
		if (this.user_id) {
			frappe.call({
				method: "frappe.desk.page.employee_desk.employee_desk.get_checkin_data",
				async: false,
				args: {
					user: this.user_id,
					month: month,
				},
				callback: function(r) {
					console.log(r.message.length)
					if(r.message.length > 0){
						let html = $(__(`
						<table class="table table-bordered small" style="margin: 0px 0px 20px 0px;">
							<thead style="background-color: #9badf052;">
								<tr>
									<th style="width: 20%" class="text-center">${__('Date')}</th>
									<th style="width: 20%" class="text-center">${__('Office In')}</th>
									<th style="width: 20%" class="text-center">${__('Lunch Out')}</th>
									<th style="width: 20%" class="text-center">${__('Lunch In')}</th>
									<th style="width: 20%" class="text-center">${__('Office Out')}</th>
								</tr>
							</thead>
							<tbody style="background-color: white;">
							`));
							for(const [key, value] of Object.entries(r.message)) {

								let office_in_color = "color:#36414c";
								let lunch_out_color = "color:#36414c";
								let lunch_in_color = "color:#36414c";
								let office_out_color = "color:#36414c";

								if(value["office_in"] == "Not Punch")
									office_in_color = "color:red";
								if(value["lunch_out"] == "Not Punch")
									lunch_out_color = "color:red";
								if(value["lunch_in"] == "Not Punch")
									lunch_in_color = "color:red";
								if(value["office_out"] == "Not Punch")
									office_out_color = "color:red";

								html.append($(__(`
										<tr>
											<td>${value["date"]}</td>
											<td class="text-right" style=${office_in_color}>${value["office_in"]}</td>
											<td class="text-right" style=${lunch_out_color}>${value["lunch_out"]}</td>
											<td class="text-right" style=${lunch_in_color}>${value["lunch_in"]}</td>
											<td class="text-right" style=${office_out_color}>${value["office_out"]}</td>
										</tr>
								`)));
							}
							html.append($(__(`
							</tbody>
							</table>
							`)));
							$attendance_dashboard.append(html);
					}
					else{
						let html = $(__(`<p style="margin-top: 30px; color:red;"> No Checkin records in ${month}, ${current_year}. </p>`));
						$attendance_dashboard.append(html);
					}						
				}
			});
		}
	}

	employee_trainings() {
		let $training = this.wrapper.find('.emp-training');
		if (this.user_id) {
			frappe.call({
				method: "frappe.desk.page.employee_desk.employee_desk.get_training_history",
				async: false,
				args: {
					user: this.user_id,
				},
				callback: function(r) {
					console.log(r.message.length)
					if(r.message.length > 0){
						let html = $(__(`
						<table class="table table-bordered small" style="margin: 0px 0px 20px 0px;">
							<thead style="background-color: #9badf052;">
								<tr>
									<th style="width: 15%" class="text-center">${__('Training Type')}</th>
									<th style="width: 15%" class="text-center">${__('Training Category')}</th>
									<th style="width: 15%" class="text-center">${__('Country')}</th>
									<th style="width: 15%" class="text-center">${__('Course Title')}</th>
									<th style="width: 15%" class="text-center">${__('College/Training Institute')}</th>
									<th style="width: 15%" class="text-center">${__('Start Date')}</th>
									<th style="width: 15%" class="text-center">${__('End Date')}</th>
									<th style="width: 15%" class="text-center">${__('Duration')}</th>
								</tr>
							</thead>
							<tbody style="background-color: white;">
							`));
							for(const [key, value] of Object.entries(r.message)) {
								html.append($(__(`
										<tr>
											<td class="text-right">${value["training_type"]}</td>
											<td class="text-right">${value["training_category"]}</td>
											<td class="text-right">${value["country"]}</td>
											<td class="text-right">${value["course_title"]}</td>
											<td class="text-right">${value["college_training_institute"]}</td>
											<td class="text-right">${value["start_date"]}</td>
											<td class="text-right">${value["end_date"]}</td>
											<td class="text-right">${value["duration"]}</td>
										</tr>
								`)));
							}
							html.append($(__(`
							</tbody>
							</table>
							`)));
							$training.append(html);
					}
					else{
						let html = $(__(`<p style="margin-top: 30px; color:red;">No Training Record.</p>`));
						$training.append(html);
					}						
				}
			});
		}
	}

	disciplinary_records() {
		let $disciplinary_records = this.wrapper.find('.disciplinary-records');
		if (this.user_id) {
			frappe.call({
				method: "frappe.desk.page.employee_desk.employee_desk.get_disciplinary_records",
				async: false,
				args: {
					user: this.user_id,
				},
				callback: function(r) {
					console.log(r.message.length)
					if(r.message.length > 0){
						let html = $(__(`
						<table class="table table-bordered small" style="margin: 0px 0px 20px 0px;">
							<thead style="background-color: #9badf052;">
								<tr>
									<th style="width: 20%" class="text-center">${__('Disciplinary Action Taken')}</th>
									<th style="width: 20%" class="text-center">${__('Nature')}</th>
									<th style="width: 20%" class="text-center">${__('From Date')}</th>
									<th style="width: 20%" class="text-center">${__('Complaint Frequency')}</th>
									<th style="width: 10%" class="text-center">${__('Action Taken')}</th>
									<th style="width: 10%" class="text-center">${__('Link')}</th>
								</tr>
							</thead>
							<tbody style="background-color: white;">
							`));
							for(const [key, value] of Object.entries(r.message)) {
								html.append($(__(`
										<tr>
											<td class="text-right">${value["disciplinary_action_taken"]}</td>
											<td class="text-right">${value["nature"]}</td>
											<td class="text-right">${value["from_date"]}</td>
											<td class="text-right">${value["complaint_frequency"]}</td>
											<td class="text-right">${value["action_taken"]}</td>
											<td class="text-right"><a href="#Form/Employee%20Disciplinary%20Record/${value["disciplinary_record"]}">${value["disciplinary_record"]}</td>
										</tr>
								`)));
							}
							html.append($(__(`
							</tbody>
							</table>
							`)));
							$disciplinary_records.append(html);
					}
					else{
						let html = $(__(`<p style="margin-top: 30px; color:red;">No Disciplinary Record.</p>`));
						$disciplinary_records.append(html);
					}						
				}
			});
		}
	}

	get_year(date_str) {
		return date_str.substring(0, date_str.indexOf('-'));
	}
	/*
	render_line_chart() {
		this.line_chart_filters = {'user': this.user_id};
		this.line_chart_config = {
			timespan: 'Last Month',
			time_interval: 'Daily',
			type: 'Line',
			value_based_on: 'points',
			chart_type: 'Sum',
			document_type: 'Energy Point Log',
			name: 'Energy Points',
			width: 'half',
			based_on: 'creation'
		};

		this.line_chart = new frappe.Chart( '.performance-line-chart', {
			title: 'Energy Points',
			type: 'line',
			height: 200,
			data: {
				labels: [],
				datasets: [{}]
			},
			colors: ['purple'],
			axisOptions: {
				xIsSeries: 1
			}
		});
		this.update_line_chart_data();
		this.create_line_chart_filters();
	}

	update_line_chart_data() {
		this.line_chart_config.filters_json = JSON.stringify(this.line_chart_filters);

		frappe.xcall('frappe.desk.doctype.dashboard_chart.dashboard_chart.get', {
			chart: this.line_chart_config,
			no_cache: 1,
		}).then(chart => {
			this.line_chart.update(chart);
		});
	}

	render_percentage_chart(field, title) {
		frappe.xcall('frappe.desk.page.employee_desk.employee_desk.get_energy_points_percentage_chart_data', {
			user: this.user_id,
			field: field
		}).then(chart => {
			if (chart.labels.length) {
				this.percentage_chart = new frappe.Chart( '.performance-percentage-chart', {
					title: title,
					type: 'percentage',
					data: {
						labels: chart.labels,
						datasets: chart.datasets
					},
					truncateLegends: 1,
					barOptions: {
						height: 11,
						depth: 1
					},
					height: 160,
					maxSlices: 8,
					colors: ['#5e64ff', '#743ee2', '#ff5858', '#ffa00a', '#feef72', '#28a745', '#98d85b', '#a9a7ac'],
				});
			} else {
				this.wrapper.find('.percentage-chart-container').hide();
			}
		});
	}

	create_line_chart_filters() {
		let filters = [
			{
				label: 'All',
				options: ['All', 'Auto', 'Criticism', 'Appreciation', 'Revert'],
				action: (selected_item) => {
					if (selected_item === 'All') delete this.line_chart_filters.type;
					else this.line_chart_filters.type = selected_item;
					this.update_line_chart_data();
				}
			},
			{
				label: 'Last Month',
				options: ['Last Week', 'Last Month', 'Last Quarter'],
				action: (selected_item) => {
					this.line_chart_config.timespan = selected_item;
					this.update_line_chart_data();
				}
			},
			{
				label: 'Daily',
				options: ['Daily', 'Weekly', 'Monthly'],
				action: (selected_item) => {
					this.line_chart_config.time_interval = selected_item;
					this.update_line_chart_data();
				}
			},
		];
		this.render_chart_filters(filters, '.line-chart-container', 1);
	}

	create_percentage_chart_filters() {
		let filters = [
			{
				label: 'Type',
				options: ['Type', 'Reference Doctype', 'Rule'],
				fieldnames: ['type', 'reference_doctype', 'rule'],
				action: (selected_item, fieldname) => {
					let title = selected_item + ' Distribution';
					this.render_percentage_chart(fieldname, title);
				}
			},
		];
		this.render_chart_filters(filters, '.percentage-chart-container');
	}*/

	create_attendance_dashboard_filters() {
		let filters = [
			{
				label: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
				"December"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
				options: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",	"December"],
				action: (selected_item) => {
					this.employee_attendance_dashboard(selected_item);
				}
			},
		];
		this.render_chart_filters(filters, '.filters-container');
	}

	render_chart_filters(filters, container, append) {
		filters.forEach(filter => {
			let chart_filter_html = `<div class="chart-filter pull-right">
				<a class="dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
					<button class="btn btn-default btn-xs">
						<span class="filter-label">${filter.label}</span>
						<span class="caret"></span>
					</button>
				</a>`;
			let options_html;

			if (filter.fieldnames) {
				options_html = filter.options.map((option, i) =>
					`<li><a data-fieldname = "${filter.fieldnames[i]}">${option}</a></li>`).join('');
			} else {
				options_html = filter.options.map( option => `<li><a>${option}</a></li>`).join('');
			}

			let dropdown_html = chart_filter_html + `<ul class="dropdown-menu">${options_html}</ul></div>`;
			let $chart_filter = $(dropdown_html);

			if (append) {
				$chart_filter.prependTo(this.wrapper.find(container));
			} else $chart_filter.appendTo(this.wrapper.find(container));

			$chart_filter.find('.dropdown-menu').on('click', 'li a', (e) => {
				let $el = $(e.currentTarget);
				let fieldname;
				if ($el.attr('data-fieldname')) {
					fieldname = $el.attr('data-fieldname');
				}
				let selected_item = $el.text();
				$el.parents('.chart-filter').find('.filter-label').text(selected_item);
				filter.action(selected_item, fieldname);
			});
		});

	}

	//......Inserting Employee Checkin........
	make_employee_checkin(checkin_type){
		var ct = ""
		if(checkin_type == "Office IN"){
			ct = "Lunch OUT"
		}
		else if(checkin_type == "Lunch OUT"){
			ct = "Lunch IN"
		}
		else if(checkin_type == "Lunch IN"){
			ct = "Office OUT"
		}
		else{
			ct = "Office IN"
		}
		frappe.call({
			method:"frappe.desk.page.employee_desk.employee_desk.get_employee_info",
			args: ({"user":frappe.session.user, "checkin_type":ct}),
			callback: function(r){
				console.log(r)	
				if(r.message){
					console.log("here");
					if((r.message[0].flag == 1 && ct == "Office IN") || (r.message[0].oo_flag == 1 && ct == "Office OUT")){
						let reason_dialog = new frappe.ui.Dialog({
							title: __('Late coming/Early Exit Reason'),
							fields: [
								{
									fieldtype: 'Small Text',
									fieldname: 'reason',
									label: 'Reason',
									reqd: 1,
								}
							],
							primary_action: values => {
								reason_dialog.disable_primary_action();
								frappe.xcall('frappe.desk.page.employee_desk.employee_desk.make_employee_checkin', {
									"employee": r.message[0].employee,
									"employee_name": r.message[0].employee_name,
									"shift_type": r.message[0].shift_type,
									"time": r.message[0].time,
									"time_difference": r.message[0].time_difference,
									reason: values['reason'],
									checkin_type: ct
								}).then(user => {
									reason_dialog.hide();
								}).finally(() => {
									reason_dialog.enable_primary_action();
								});
								let alert_dialog = new frappe.ui.Dialog({
									title: 'Your Record is updated successfully',
									primary_action: values => {
										alert_dialog.disable_primary_action();
										window.location.reload()
								},
								primary_action_label: 'OK'
								});
								alert_dialog.show();
						},
						primary_action_label: __('Save')
						});
						reason_dialog.show();
					}
					else{
						frappe.call({
							method: "frappe.desk.page.employee_desk.employee_desk.make_employee_checkin",
							args: {
									"employee": r.message[0].employee,
									"employee_name": r.message[0].employee_name,
									"shift_type": r.message[0].shift_type,
									"time": r.message[0].time,
									"time_difference": r.message[0].time_difference,
									checkin_type: ct
								},
							callback: function(r){
								let alert_dialog = new frappe.ui.Dialog({
									title: __('Your Record is updated successfully'),
									primary_action: values => {
										alert_dialog.disable_primary_action();
										window.location.reload()
								},
								primary_action_label: __('OK')
								});
								alert_dialog.show();
							}
						})
					}
				}
			}
		})
	}

	edit_profile() {
		let edit_profile_dialog = new frappe.ui.Dialog({
			title: __('Edit Profile'),
			fields: [
				// {
				// 	fieldtype: 'Attach Image',
				// 	fieldname: 'user_image',
				// 	label: 'Profile Image',
				// },
				{
					fieldtype: 'Data',
					fieldname: 'interest',
					label: 'Interests',
				},
				{
					fieldtype: 'Column Break'
				},
				{
					fieldtype: 'Data',
					fieldname: 'location',
					label: 'Location',
				},
				{
					fieldtype: 'Section Break',
					fieldname: 'Interest',
				},
				{
					fieldtype: 'Small Text',
					fieldname: 'bio',
					label: 'Bio',
				}
			],
			primary_action: values => {
				edit_profile_dialog.disable_primary_action();
				frappe.xcall('frappe.desk.page.employee_desk.employee_desk.update_profile_info', {
					profile_info: values
				}).then(user => {
					user.image = user.user_image;
					this.user = Object.assign(values, user);
					edit_profile_dialog.hide();
					this.render_user_details();
				}).finally(() => {
					edit_profile_dialog.enable_primary_action();
				});
			},
			primary_action_label: __('Save')
		});

		edit_profile_dialog.set_values({
			// user_image: this.user.image,
			location: this.user.location,
			interest: this.user.interest,
			bio: this.user.bio
		});
		edit_profile_dialog.show();
	}

	render_user_details() {
		this.sidebar.empty().append(frappe.render_template('employee_desk_sidebar', {
			user_image: frappe.avatar(this.user_id, 'avatar-frame', 'user_image', this.user.image),
			user_abbr: this.user.abbr,
			user_location: this.user.location,
			user_interest: this.user.interest,
			user_bio: this.user.bio,
		}));

		this.setup_user_profile_links();
	}

	// Sidebar Links
	setup_user_profile_links() {
		if (this.user_id !== frappe.session.user) {
			this.wrapper.find('.profile-links').hide();
		} else {
			this.wrapper.find('.edit-profile-link').on('click', () => {
				this.edit_profile();
			});

			this.wrapper.find('.transaction-link').on('click', () => {
				this.go_to_desk();
			});
		}
	}

	go_to_desk() {
		// frappe.set_route('Form', 'User', this.user_id);
		frappe.set_route('');
	}

	// go_to_todo_details() {
	// 	frappe.set_route('Form', 'ToDo Details', '2407');
	// }

	// Enabling and disabling employee checkin button
	setup_punching_button(){
		var checkin_type = ""
		frappe.call({
			method: "frappe.desk.page.employee_desk.employee_desk.get_employee_checkin_info",
			async: false,
			callback: function(r){
				// console.log(r);
				checkin_type = r.message
			}
		});
		if(frappe.session.user == 'Administrator'){
			this.wrapper.find('.office-in-button').hide();
			this.wrapper.find('.lunch-out-button').hide();
			this.wrapper.find('.lunch-in-button').hide();
			this.wrapper.find('.office-out-button').hide();
		}
		else if(checkin_type == "Office IN"){
			// console.log(r.message)				
			this.wrapper.find('.office-in-button').hide();
			this.wrapper.find('.lunch-in-button').hide();
			this.wrapper.find('.office-out-button').hide();
			this.wrapper.find('.lunch-out').on('click', () => {
				this.make_employee_checkin(checkin_type);
			});
		}
		else if(checkin_type == "Lunch OUT"){					
			this.wrapper.find('.office-in-button').hide();
			this.wrapper.find('.lunch-out-button').hide();
			this.wrapper.find('.office-out-button').hide();
			this.wrapper.find('.lunch-in').on('click', () => {
				this.make_employee_checkin(checkin_type);
			});
		}
		else if(checkin_type == "Lunch IN"){					
			this.wrapper.find('.office-in-button').hide();
			this.wrapper.find('.lunch-out-button').hide();
			this.wrapper.find('.lunch-in-button').hide();
			this.wrapper.find('.office-out').on('click', () => {
				this.make_employee_checkin(checkin_type);
			});
		}
		else if(checkin_type == "Office OUT"){
			this.wrapper.find('.office-in-button').hide();
			this.wrapper.find('.lunch-out-button').hide();
			this.wrapper.find('.lunch-in-button').hide();
			this.wrapper.find('.office-out-button').hide();
		}
		else {
			this.wrapper.find('.lunch-out-button').hide();
			this.wrapper.find('.lunch-in-button').hide();
			this.wrapper.find('.office-out-button').hide();
			this.wrapper.find('.office-in').on('click', () => {
				this.make_employee_checkin(checkin_type);
			});
		}
	}

	get_display_time()	{
		return frappe.xcall("frappe.desk.page.employee_desk.employee_desk.get_display_time", {
			async: false,
		}).then(r =>{
			this.d_time = r[0].d_time;
		});
	}

	display_time() {
		let $display_t = this.wrapper.find('.display-time');

		this.get_display_time().then(() => {
			let html = $(__(`<span>${this.d_time}</span>`,[this.d_time]));
			setInterval(()=>this.display_time(),60000)
				
			$display_t.html(html);
		});
	}

	get_checkin_info() {
		return frappe.xcall('frappe.desk.page.employee_desk.employee_desk.get_checkin_info', {
			user: this.user_id,
		}).then(r => {
			this.office_in = r[0].office_in;
			this.lunch_out = r[0].lunch_out;
			this.lunch_in = r[0].lunch_in;
			this.office_out = r[0].office_out;
			this.date = r[0].date;
		});
	}

	checkin_info() {
		let $checkin_details = this.wrapper.find('.checkin_details');

		this.get_checkin_info().then(() => {
				let html = $(__(`<p style="color:#1f1e1e; font-size:16px; ">${__('Date: ')}<span class="rank">${this.date}</span></p>
					<p style="color:#15F906; font-size:14px;">${__('Office In: ')}<span class="rank">${this.office_in}</span></p>
					<p style="color:#bba00a; font-size:14px;">${__('Lunch Out: ')}<span class="rank">${this.lunch_out}</span></p>
					<p style="color:#bba00a; font-size:14px;">${__('Lunch In: ')}<span class="rank">${this.lunch_in}</span></p>
					<p style="color:#f44336; font-size:14px;">${__('Office Out: ')}<span class="rank">${this.office_out}</span></p>
				`, [this.date, this.office_in, this.lunch_out, this.lunch_in, this.office_out]));

				$checkin_details.append(html);
		});
	}

	get_job_description() {
		return frappe.xcall('frappe.desk.page.employee_desk.employee_desk.get_job_description', {
			user: this.user_id,
		}).then(r => {
			// console.log(r)
			this.job_description = r[0].job_description;
		});
	}

	get_emp_info() {
		return frappe.xcall('frappe.desk.page.employee_desk.employee_desk.get_emp_info', {
			user: this.user_id,
		}).then(r => {
			// console.log(r)
			this.eid = r.name;
			this.grade = r.grade;
			this.designation = r.designation;
		});
	}
	render_graph(){
		// debugger;

		// page.add_menu_item('Projects', () => frappe.set_route('List', 'Project'))
		// // debugger;
		// const graph = new frappe.ui.Chart("#chart",{
		// 	innerHeight:140,
		// 	parent: page.main,
		// 	mode: 'line',
		// 	x:{
		// 		values: [
		// 			'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sept', 'oct', 'nov', 'dec'
		// 		]
		// 	},
		// 	y:[{
		// 		values:[23, 34, 23, 34, 4, 6, 2, 1, 8, 5, 32, 34]
		// 	}]
		// });
		// wrapper = $(wrapper).find('.chart');
		// wrapper.append(`
		// 		<div id="chart"></div>
		// 	`);	  
	// try{
        var xyValues = [
			{x:50, y:7},
			{x:60, y:8},
			{x:70, y:8},
			{x:80, y:9},
			{x:90, y:9},
			{x:100, y:9},
			{x:110, y:10},
			{x:120, y:11},
			{x:130, y:14},
			{x:140, y:14},
			{x:150, y:15}
		  ];
		const graph = new frappe.ui.Chart({
		    // chart_type: "line",
			// data: {
			// },
			// options: {
			//   legend: {display: false},
			//   scales: {
			// 	xAxes: [{ticks: {min: 40, max:160}}],
			// 	yAxes: [{ticks: {min: 6, max:16}}],
			//   }
			// }
		  });
		// }
		// catch(err){
		// 	console.log(err)
		// }
		//   setTimeout(function () {graph.draw(!0)}, 1);
	}
	employee_job_description(){
		let $leave_and_job_description = this.wrapper.find('.job-description');
		this.get_job_description().then(() => {
				// console.log(this.job_description)
				if(this.job_description != 'None'){
					let html = $(__(`<p style="color:#1f1e1e; margin-left: 2%; font-size:12px;"><a href="${this.job_description}">Download</a></p>
					`, [this.job_description]));
					$leave_and_job_description.append(html);
				}
				else{
					let html = $(__(`<p style="margin-top: 30px; color:red;">No Job Description Found</p>
					`, [this.job_description]));
					$leave_and_job_description.append(html);
				}

		});
	}

	basic_emp_info(){
		let $b_emp_info = this.wrapper.find('.b-emp-info');

		this.get_emp_info().then(() => {
			let html = $(__(`
			<p style="font-size:14px;"><b>${__('EID: ')}</b><a href="#Form/Employee/${this.eid}"><span title="Go to Employee Master">${this.eid}</span></a></p>
			<p style="font-size:14px;"><b>${__('Grade: ')}</b><span class="rank">${this.grade}</span></p>
			<p style="font-size:14px;"><b>${__('Designation: ')}</b><span class="rank">${this.designation}</span></p>
		`, [this.eid, this.grade, this.designation]));

			$b_emp_info.append(html);
		});
	}
	employee_work_history(){
		let $work_history = this.wrapper.find('.work-history');
		if (this.user_id) {
			frappe.call({
				method: "frappe.desk.page.employee_desk.employee_desk.get_emp_work_history",
				async: false,
				args: {
					user: this.user_id,
				},
				callback: function(r) {
					if(r.message.length > 0){
						let html = $(__(`
						<table class="table table-bordered small" style="margin: 0px 0px 20px 0px;">
							<thead style="background-color: #9badf052;">
								<tr>
									<th style="width: 10%" class="text-right">${__('Type')}</th>
									<th style="width: 10%" class="text-right">${__('Link')}</th>
									<th style="width: 10%" class="text-right">${__('Branch')}</th>
									<th style="width: 15%" class="text-right">${__('Department')}</th>
									<th style="width: 15%" class="text-right">${__('Division')}</th>
									<th style="width: 10%" class="text-right">${__('Designation')}</th>
									<th style="width: 10%" class="text-right">${__('From Date')}</th>
									<th style="width: 10%" class="text-right">${__('To Date')}</th>
									<th style="width: 10%" class="text-right">${__('Promotion Due Date')}</th>
								</tr>
							</thead>
							<tbody style="background-color: white;">
							`));
							// let table_data = $(__());
							for(const [key, value] of Object.entries(r.message)) {
								html.append($(__(`
										<tr>
											<td class="text-right">${value["reference_doctype"]}</td>
											<td class="text-right">${value["reference_docname"]}</td>
											<td class="text-right">${value["branch"]}</td>
											<td class="text-right">${value["department"]}</td>
											<td class="text-right">${value["division"]}</td>
											<td class="text-right">${value["designation"]}</td>
											<td class="text-right">${value["from_date"]}</td>
											<td class="text-right">${value["to_date"]}</td>
											<td class="text-right">${value["promotion_due_date"]}</td>
										</tr>
								`)));
							}
							// html.append(table_data);
							html.append($(__(`
							</tbody>
							</table>
							`)));
							console.log(html)
							$work_history.append(html);

					}
					else{
						let html = $(__(`<p style="margin-top: 30px; color:red;"> No Work History found. </p>`));
						$work_history.append(html);
					}

						
				}
			});
		}
	}
	employee_leave_dashboard() {
		let $leave_dashboard = this.wrapper.find('.leave-dashboard');
		if (this.user_id) {
			frappe.call({
				method: "frappe.desk.page.employee_desk.employee_desk.get_leave_details",
				async: false,
				args: {
					user: this.user_id,
				},
				callback: function(r) {
					if(r.message.leave_allocation){
						let html = $(__(`
						<table class="table table-bordered small" style="margin: 0px 0px 20px 0px;">
							<thead style="background-color: #9badf052;">
								<tr>
									<th style="width: 20%">${__('Leave Type')}</th>
									<th style="width: 20%" class="text-right">${__('Total Allocated Leaves')}</th>
									<th style="width: 20%" class="text-right">${__('Used Leaves')}</th>
									<th style="width: 20%" class="text-right">${__('Pending Leaves')}</th>
									<th style="width: 20%" class="text-right">${__('Available Leaves')}</th>
								</tr>
							</thead>
							<tbody style="background-color: white;">
							`));
							// let table_data = $(__());
							for(const [key, value] of Object.entries(r.message.leave_allocation)) {
								html.append($(__(`
										<tr>
											<td>${key}</td>
											<td class="text-right">${value["total_leaves"]}</td>
											<td class="text-right">${value["leaves_taken"]}</td>
											<td class="text-right">${value["pending_leaves"]}</td>
											<td class="text-right">${value["remaining_leaves"]}</td>
										</tr>
								`)));
							}
							// html.append(table_data);
							html.append($(__(`
							</tbody>
							</table>
							`)));
							console.log(html)
							$leave_dashboard.append(html);

					}
					else{
						let html = $(__(`<p style="margin-top: 30px;"> No Leaves have been allocated. </p>`));
						$leave_dashboard.append(html);
					}

						
				}
			});
		}
	}
	employee_pms_records() {
		let $pms_records = this.wrapper.find('.pms-records');
		if (this.user_id) {
			frappe.call({
				method: "frappe.desk.page.employee_desk.employee_desk.get_pms_records",
				async: false,
				args: {
					user: this.user_id,
				},
				callback: function(r) {
					if(r.message.length > 0){
						let html = $(__(`
						<table class="table table-bordered small" style="margin: 0px 0px 20px 0px;">
							<thead style="background-color: #9badf052;">
								<tr>
									<th style="width: 20%">${__('PMS Calendar')}</th>
									<th style="width: 20%" class="text-right">${__('Final Score')}</th>
									<th style="width: 20%" class="text-right">${__('Overall Rating')}</th>
								</tr>
							</thead>
							<tbody style="background-color: white;">
							`));
							// let table_data = $(__());
							for(const [key, value] of Object.entries(r.message)) {
								html.append($(__(`
										<tr>
											<td class="text-right">${value["fiscal_year"]}</td>
											<td class="text-right">${value["final_score"]}</td>
											<td class="text-right">${value["overall_rating"]}</td>
										</tr>
								`)));
							}
							// html.append(table_data);
							html.append($(__(`
							</tbody>
							</table>
							`)));
							console.log(html)
							$pms_records.append(html);

					}
					else{
						let html = $(__(`<p style="margin-top: 30px; color:red;"> No PMS records found. </p>`));
						$pms_records.append(html);
					}

						
				}
			});
		}
	}
	/*
	get_user_points() {
		return frappe.xcall(
			'frappe.social.doctype.energy_point_log.energy_point_log.get_user_energy_and_review_points',
			{
				user: this.user_id,
			}
		).then(r => {
			if (r[this.user_id]) {
				this.energy_points = r[this.user_id].energy_points;
				this.review_points = r[this.user_id].review_points;
			}
		});
	}

	render_user_activity() {
		this.$recent_activity_list = this.wrapper.find('.recent-activity-list');

		let get_recent_energy_points_html = (field) => {
			let message_html = frappe.energy_points.format_history_log(field);
			return `<p class="recent-activity-item text-muted"> ${message_html} </p>`;
		};

		frappe.xcall('frappe.desk.page.employee_desk.employee_desk.get_energy_points_list', {
			start: this.activity_start,
			limit: this.activity_end,
			user: this.user_id
		}).then(list => {
			if (list.length < 11) {
				let activity_html = `<span class="text-muted">${__('No More Activity')}</span>`;
				this.wrapper.find('.show-more-activity').html(activity_html);
			}
			let html = list.slice(0, 10).map(get_recent_energy_points_html).join('');
			this.$recent_activity_list.append(html);
		});
	}

	setup_show_more_activity() {
		//Show 10 items at a time
		this.activity_start = 0;
		this.activity_end = 11;
		this.wrapper.find('.show-more-activity').on('click', () => this.show_more_activity());
	}

	show_more_activity() {
		this.activity_start = this.activity_end;
		this.activity_end += 11;
		this.render_user_activity();
	}
	*/

}
