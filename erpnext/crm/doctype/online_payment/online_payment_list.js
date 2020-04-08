frappe.listview_settings['Online Payment']={
	add_fields: ["status"],
	get_indicator: function(doc){
		var colors = {
			"Draft": "orange",
			"Pending": "orange",
			"Successful": "green",
			"Failed": "red",
			"Cancelled": "darkgrey"
		};		

		if(colors[doc.status]){
			return [__(doc.status), colors[doc.status], "status,=," + doc.status];
		}else{
			
			return [__(doc.status), "darkgrey", "status,=," + doc.status];
		}
		
	}
};
