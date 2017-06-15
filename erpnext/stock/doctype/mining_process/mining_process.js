// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mining Process', {
	refresh: function(frm) {

	}
});

// additional validation on dates
frappe.ui.form.on("Mining Process", "coal_mining_to_date", function(frm) {
    if (!frm.doc.coal_mining_process) {msgprint("From Date should not be Null"); cur_frm.set_value("coal_mining_to_date", "");}
    if (frm.doc.coal_mining_process > frm.doc.coal_mining_to_date) {
        cur_frm.set_value("coal_mining_to_date", "")
        msgprint("To Date should be greater than From Date");
    }
});

// additional validation on dates
frappe.ui.form.on("Mining Process", "coal_mining_process", function(frm) {
    if (frm.doc.coal_mining_to_date) {
      if (frm.doc.coal_mining_process > frm.doc.coal_mining_to_date) {
         cur_frm.set_value("coal_mining_to_date", "")
         msgprint("To Date should be greater than From Date");
      }
    }
});

frappe.ui.form.on("Mining items", "material", function(frm, cdt, cdn) {
   var item = frappe.get_doc(cdt, cdn);
   frappe.call({
        method: "erpnext.stock.doctype.mining_process.mining_process.get_item_details",
        args: {
            "item_code": item.material
        },
        callback: function(r)  {
            frappe.model.set_value(cdt, cdn, "item_name", r.message[0].item_name)
            frappe.model.set_value(cdt, cdn, "uom", r.message[0].stock_uom)
        }
   })
})

frappe.ui.form.on("Mining items", "qty", function(frm, cdt, cdn) {
   var item = frappe.get_doc(cdt, cdn);
   if(item.mine_entry_rate) {
       frappe.model.set_value(cdt, cdn, "amount_mined", item.mine_entry_rate * item.qty)
   }
})

frappe.ui.form.on("Mining items", "mine_entry_rate", function(frm, cdt, cdn) {
   var item = frappe.get_doc(cdt, cdn);
   if(item.qty) {
       frappe.model.set_value(cdt, cdn, "amount_mined", item.mine_entry_rate * item.qty)
   }
})
