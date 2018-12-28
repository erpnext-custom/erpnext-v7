frappe.listview_settings['Equipment Request'] = {
        add_fields: ["percent_completed", "docstatus"],
        get_indicator: function(doc) {
                if(doc.percent_completed == 0) {
                        return ["Requested", "orange", "docstatus,=,1|percent_completed,=,0"];
                }
                else if(doc.percent_completed < 100) {
                        return ["Partially Completed", "blue", "docstatus,=,1|percent_completed,>,0|percent_completed,<,100"];
                }
                else {
                        return ["Completed", "green", "docstatus,=,1|percent_completed,=,100"];
                }
        }
}

