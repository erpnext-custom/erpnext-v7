frappe.listview_settings['Transport Request'] = {
        add_fields: ["name","docstatus", "status", "approval_status"],
        get_indicator: function(doc) {
                if(doc.status == "Pending") {
                        return ["Pending", "orange"];
                }
                else if(doc.status == "Approved"){
                        return ["Approved", "green"];
                }
                else if(doc.status == "Rejected")
                {
                        return ["Rejected", "black"];
                }
                else{
                        return ["Deregistered","blue"];
                }
        }
};
