frappe.listview_settings['Vehicle'] = {
        add_fields: ["name", "vehicle_status"],
        get_indicator: function(doc) {
                if(doc.vehicle_status == "Active") {
                        return ["Active", "green"];
                }
                else if(doc.vehicle_status == "Suspended"){
                        return ["Suspended", "orange"];
                }
                else if(doc.vehicle_status == "Deregistered")
                {
                        return ["Deregistered", "red"];
                }
        }
};
