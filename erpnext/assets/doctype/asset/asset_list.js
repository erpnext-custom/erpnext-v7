frappe.listview_settings['Asset'] = {
	add_fields: ['status'],
	get_indicator: function (doc) {
		if (doc.status === "Fully Depreciated") {
			return [__("Fully Depreciated"), "green", "status,=,Fully Depreciated"];

		} else if (doc.status === "Partially Depreciated") {
			return [__("Partially Depreciated"), "grey", "status,=,Partially Depreciated"];

		} else if (doc.status === "Sold") {
			return [__("Sold"), "green", "status,=,Sold"];

		} else if (doc.status === "Scrapped") {
			return [__("Scrapped"), "grey", "status,=,Scrapped"];

		} else if (doc.status === "In Maintenance") {
			return [__("In Maintenance"), "orange", "status,=,In Maintenance"];

		} else if (doc.status === "Out of Order") {
			return [__("Out of Order"), "grey", "status,=,Out of Order"];

		} else if (doc.status === "Issue") {
			return [__("Issue"), "orange", "status,=,Issue"];

		} else if (doc.status === "Receipt") {
			return [__("Receipt"), "green", "status,=,Receipt"];

		} else if (doc.status === "Submitted") {
			return [__("Submitted"), "blue", "status,=,Submitted"];

		} else if (doc.status === "Draft") {
			return [__("Draft"), "red", "status,=,Draft"];
		}
	},
	onload: function(doc) {
        /*
		me.page.add_action_item('Make Asset Movement', function() {
			const assets = me.get_checked_items();
			frappe.call({
				method: "erpnext.assets.doctype.asset.asset.make_asset_movement",
				freeze: true,
				args:{
					"assets": assets
				},
				callback: function (r) {
					if (r.message) {
						var doc = frappe.model.sync(r.message)[0];
						frappe.set_route("Form", doc.doctype, doc.name);
					}
				}
			});
		}); */
	},
}
$.extend(frappe.listview_settings['Asset'], {
	onload: function(listview) {
		listview.page.add_menu_item(__("Submit"), function() {
			console.log(getIdsFromList());
			frappe.call({
				method: "erpnext.assets.doctype.asset.submit_assets",
				args: {
					assets_list: getIdsFromList()
				}
			});
			console.log(listview.page);
		});
	}
});

var getIdsFromList = function(){
	var docids = null;
	var route = frappe.get_route();
	var len = route.length;
	if (len > 1 && route[0] === "List"){
		var doctype = route[1];
		var page = [route[0], doctype].join("/");
		docids = getCheckedNames(page);
	}

	return docids;
};

getChecked = function(name){
	return $(frappe.pages[name]).find("input:checked");
};

getCheckedNames = function(page){
	var names = [];
	var checked = getChecked(page);
	var elems_a = checked.siblings("a");
	elems_a.each(function(i,el){
		var t = unescape($(el).attr("href")).slice(1);
		var s = t.split("/");
		names.push(s[s.length - 1]);
	});

	return names;
};