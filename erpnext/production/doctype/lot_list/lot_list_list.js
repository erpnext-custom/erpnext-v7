frappe.listview_settings['Lot List'] = {
        add_fields: ["name","sales_order","stock_entry","production","docstatus", "posting_date"],
	get_indicator: function(doc) {
                if(doc.sales_order) {
                        return ["Sold", "orange"];
                }
		else if(doc.production){
			return ["Taken For Sawing", "orange"];
		}
                else if(doc.stock_entry)
		{
                        return ["Stock Transfered", "green"];
                }
		else{
			return ["Unsold","green"];
		}
        }
};


