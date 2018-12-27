frappe.pages['vehicle-status'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Vehicle Status',
		single_column: true
	});
	
	wrapper.vehicle_status = new erpnext.VehicleStatus(wrapper);

	frappe.breadcrumbs.add("Maintenance");
}

erpnext.VehicleStatus = Class.extend({

})
