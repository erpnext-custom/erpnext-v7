frappe.treeview_settings["Item"] = {
        breadcrumbs: "Stock",
        get_tree_root: false,
	root_label: "Items",
        get_tree_nodes: 'erpnext.stock.doctype.item.item.get_item_list',
        add_tree_node: 'erpnext.accounts.utils.add_cc',
}


