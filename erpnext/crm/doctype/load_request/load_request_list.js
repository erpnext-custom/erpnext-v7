frappe.listview_settings['Load Request'] = {
        add_fields: ["name", "load_status"],
        get_indicator: function(doc) {
                if(doc.load_status == "Queued") {
                        return ["Queued", "orange"];
                }
                else if(doc.load_status == "Loaded") {
                        return ["Loaded", "blue"]
                }
                else if(doc.load_status == "Delivered") {
                        return ["Completed", "green"];
                }
                else if(doc.load_status == "Cancelled") {
                        return ["Cancelled", "grey"]
                }
                else{
                        return ["Draft"]
                }
        }
};
