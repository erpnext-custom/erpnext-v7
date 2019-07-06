frappe.listview_settings['Lot List'] = {
        add_fields: ["name","sales_order","docstatus", "posting_date"],
	get_indicator: function(doc) {
                if(doc.sales_order) {
                        return ["Sold", "orange"];
                }
                else {
                        return ["Unsold", "green"];
                }
        }
};


