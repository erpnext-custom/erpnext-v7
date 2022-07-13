// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors // License: GNU General Public License v3. See license.txt
/*
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
2.0		         SHIV		                        26/11/2017         * If purpose is "Material Issue", from_ware should
																			be from loggedin user's cost_center's by default,
																			as the user can issue material from only his/her
																			warehouse.
--------------------------------------------------------------------------------------------------------------------------                                                                          
*/
cur_frm.add_fetch("item_code", "item_group", "item_group")

frappe.provide("erpnext.stock");

erpnext.stock.StockEntry = erpnext.stock.StockController.extend({
	setup: function () {
		var me = this;

		this.frm.fields_dict.bom_no.get_query = function () {
			return {
				filters: {
					"docstatus": 1,
					"is_active": 1
				}
			};
		};

		this.frm.fields_dict.items.grid.get_field('item_code').get_query = function () {
			if (me.frm.doc.initial_stock_templates) {
				//var d = frappe.model.add_child(me.frm.doc, "Stock Entry Details", "items");
				//this.frm.set_value("item_code","300000");
				//this.frm.fields_dict.items.grid.get_field('item_name')
			}
			else {
				return erpnext.queries.item({ is_stock_item: 1 });
			}
		};

		this.frm.set_query("purchase_order", function () {
			return {
				"filters": {
					"docstatus": 1,
					"is_subcontracted": "Yes",
					"company": me.frm.doc.company
				}
			};
		});
		this.frm.set_query("technical_sanction", function () {
			return {
				"filters": {
					"docstatus": 1,
				}
			}
		});

		if (cint(frappe.defaults.get_default("auto_accounting_for_stock"))) {
			this.frm.add_fetch("company", "stock_adjustment_account", "expense_account");
			this.frm.fields_dict.items.grid.get_field('expense_account').get_query =
				function () {
					return {
						filters: {
							"company": me.frm.doc.company,
							"is_group": 0
						}
					}
				}
			this.frm.set_query("difference_account", function () {
				return {
					"filters": {
						"company": me.frm.doc.company,
						"is_group": 0
					}
				};
			});
		}

		this.frm.get_field('items').grid.editable_fields = [
			{ fieldname: 'item_code', columns: 3 },
			{ fieldname: 'qty', columns: 1 },
			{ fieldname: 'valuation_rate', columns: 2 },
			{ fieldname: 's_warehouse', columns: 2 },
			{ fieldname: 't_warehouse', columns: 2 }
		];

	},

	// Ver2.0 Begins, onload added by SHIV on 26/11/2017
	onload: function (frm) {
		var me = this;
		if (me.frm.doc.__islocal && me.frm.doc.purpose == "Material Issue") {
			frappe.call({
				method: "erpnext.stock.doctype.material_request.material_request.get_cc_warehouse",
				args: { "user": frappe.session.user },
				callback(r) {
					//cur_frm.set_value("temp_cc", r.message[0]);		
					//cur_frm.set_value("temp_wh", r.message[1]);		
					//cur_frm.set_value("approver", r.message[2]);		
					cur_frm.set_value("from_warehouse", r.message[1])
				}
			})


		}
		//Commented By Tashi for testing purpose		
		/*if(me.frm.doc.__islocal) {
			frappe.call({
                              method: "erpnext.custom_utils.get_user_info",
                              args: {"user": frappe.session.user},
                              callback(r) {
					if(r.message){
                                        cur_frm.set_value("branch", r.message.branch);
                                        cur_frm.set_value("from_warehouse", r.message.warehouse);
                                        cur_frm.set_value("user_cost_center", r.message.cost_center);
                             }}
                        });
		}*/
	},
	// Ver2.0 Ends

	onload_post_render: function () {
		var me = this;
		this.set_default_account(function () {
			if (me.frm.doc.__islocal && me.frm.doc.company && !me.frm.doc.amended_from) {
				cur_frm.script_manager.trigger("company");
			}
		});

		if (!this.item_selector && false) {
			this.item_selector = new erpnext.ItemSelector({ frm: this.frm });
		}
	},

	refresh: function (frm) {
		var me = this;
		erpnext.toggle_naming_series();
		this.toggle_related_fields(this.frm.doc);
		this.toggle_enable_bom();
		this.show_stock_ledger();
		if (cint(frappe.defaults.get_default("auto_accounting_for_stock"))) {
			this.show_general_ledger();
		}
		// TODO: NEED to make it so that the field basic rate is not read only when the purpose is material Receipt
		// if (me.frm.doc.purpose == "Material Receipt") {
		// 	console.log("-------->>>>>")
		// 	console.log(me.frm)
		// }
		erpnext.hide_company();

		/*if(!frm.__islocal && frm.purpose == 'Material Transfer for Manufacture' && frm.work_order){
		cur_frm.cscript.validate = function(frm) {
			 frappe.model.open_mapped_doc({
											method: "erpnext.stock.doctype.stock_entry.stock_entry.make_material_requisition",
											frm: cur_frm
									})*/
		/*cur_frm.add_custom_button("Create Material Request", function() {
									frappe.model.open_mapped_doc({
											method: "erpnext.stock.doctype.stock_entry.stock_entry.make_material_requisition",
											frm: cur_frm
									})
							});*/
		//}}

		/*cur_frm.add_custom_button(__('Make Material Request'), function() {
									frappe.model.with_doctype('Material Request', function() {
											var mr = frappe.model.get_new_doc('Material Request');
											//var items =cur_frm.get_field('items').grid.get_selected_children();
											var items = frm.doc.items;
											items.forEach(function(item) {
													var mr_item = frappe.model.add_child(cur_frm, "Material Request Item", "items");
													mr_item.item_code = item.item_code;
													mr_item.item_name = item.item_name;
													mr_item.uom = item.uom;
													mr_item.conversion_factor = item.conversion_factor;
													mr_item.item_group = item.item_group;
													mr_item.description = item.description;
													mr_item.image = item.image;
													mr_item.qty = item.qty;
													mr_item.warehouse = item.s_warehouse;
													mr_item.required_date = frappe.datetime.nowdate();
											});
											frappe.set_route('Form', 'Material Request', mr.name);
									});
							});
		}*/
		cur_frm.add_custom_button(__('Purchase Receipt'),
			function () {
				erpnext.utils.map_current_doc({
					method: "erpnext.stock.doctype.stock_entry.stock_entry.make_receipt_order",
					source_doctype: "Purchase Receipt",
					get_query_filters: {
						docstatus: 1,
						company: cur_frm.doc.company
					}
				})
			}, __("Add items from"));

	},


	on_submit: function () {
		this.clean_up();
	},

	after_cancel: function () {
		this.clean_up();
	},

	set_default_account: function (callback) {
		var me = this;

		if (cint(frappe.defaults.get_default("auto_accounting_for_stock")) && this.frm.doc.company) {
			return this.frm.call({
				method: "erpnext.accounts.utils.get_company_default",
				args: {
					"fieldname": "stock_adjustment_account",
					"company": this.frm.doc.company
				},
				callback: function (r) {
					if (!r.exc) {
						$.each(me.frm.doc.items || [], function (i, d) {
							if (!d.expense_account) d.expense_account = r.message;
						});
						if (callback) callback();
					}
				}
			});
		}
	},

	clean_up: function () {
		// Clear Work Order record from locals, because it is updated via Stock Entry
		if (this.frm.doc.work_order &&
			in_list(["Manufacture", "Material Transfer for Manufacture"], this.frm.doc.purpose)) {
			frappe.model.remove_from_locals("Work Order",
				this.frm.doc.work_order);
		}
	},

	get_items: function () {
		var me = this;
		if (!this.frm.doc.fg_completed_qty || !this.frm.doc.bom_no)
			frappe.throw(__("BOM and Manufacturing Quantity are required"));

		if (this.frm.doc.work_order || this.frm.doc.bom_no) {
			// if production order / bom is mentioned, get items
			return this.frm.call({
				doc: me.frm.doc,
				method: "get_items",
				callback: function (r) {
					if (!r.exc) refresh_field("items");
				}
			});
		}
	},

	qty: function (doc, cdt, cdn) {
		var d = locals[cdt][cdn];
		if (doc.initial_stock_templates) {
			d.conversion_factor = 1;
		}
		d.transfer_qty = flt(d.qty) * flt(d.conversion_factor);
		console.log(`this is the qty: ${d.qty}`)
		this.calculate_basic_amount(d);
	},
	
	work_order: function () {
		var me = this;
		this.toggle_enable_bom();

		return frappe.call({
			method: "erpnext.stock.doctype.stock_entry.stock_entry.get_work_order_details",
			args: { work_order: me.frm.doc.production_order },
			callback: function (r) {
				if (!r.exc) {
					$.each(["from_bom", "bom_no", "fg_completed_qty", "use_multi_level_bom"], function (i, field) {
						me.frm.set_value(field, r.message[field]);
					})

					if (me.frm.doc.purpose == "Material Transfer for Manufacture" && !me.frm.doc.to_warehouse)
						me.frm.set_value("to_warehouse", r.message["wip_warehouse"]);


					if (me.frm.doc.purpose == "Manufacture") {
						if (r.message["additional_costs"].length) {
							$.each(r.message["additional_costs"], function (i, row) {
								me.frm.add_child("additional_costs", row);
							})
							refresh_field("additional_costs");
						}

						if (!me.frm.doc.from_warehouse) me.frm.set_value("from_warehouse", r.message["wip_warehouse"]);
						if (!me.frm.doc.to_warehouse) me.frm.set_value("to_warehouse", r.message["fg_warehouse"]);
					}
					me.get_items()
				}
			}
		});
	},

	toggle_enable_bom: function () {
		this.frm.toggle_enable("bom_no", !!!this.frm.doc.work_order);
	},

	add_excise_button: function () {
		if (frappe.boot.sysdefaults.country === "India")
			this.frm.add_custom_button(__("Excise Invoice"), function () {
				var excise = frappe.model.make_new_doc_and_get_name('Journal Entry');
				excise = locals['Journal Entry'][excise];
				excise.voucher_type = 'Excise Entry';
				frappe.set_route('Form', 'Journal Entry', excise.name);
			}, __("Make"));
		cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
	},

	items_add: function (doc, cdt, cdn) {
		var row = frappe.get_doc(cdt, cdn);
		this.frm.script_manager.copy_from_first_row("items", row, ["expense_account", "cost_center"]);

		if (!row.s_warehouse) row.s_warehouse = this.frm.doc.from_warehouse;
		if (!row.t_warehouse) row.t_warehouse = this.frm.doc.to_warehouse;
	},

	source_mandatory: ["Material Issue", "Material Transfer", "Subcontract", "Material Transfer for Manufacture"],
	target_mandatory: ["Material Receipt", "Material Transfer", "Subcontract", "Material Transfer for Manufacture"],

	from_warehouse: function (doc) {
		var me = this;
		this.set_warehouse_if_different("s_warehouse", doc.from_warehouse, function (row) {
			return me.source_mandatory.indexOf(me.frm.doc.purpose) !== -1;
		});
	},

	to_warehouse: function (doc) {
		var me = this;
		this.set_warehouse_if_different("t_warehouse", doc.to_warehouse, function (row) {
			return me.target_mandatory.indexOf(me.frm.doc.purpose) !== -1;
		});
	},

	set_warehouse_if_different: function (fieldname, value, condition) {
		var changed = false;
		for (var i = 0, l = (this.frm.doc.items || []).length; i < l; i++) {
			var row = this.frm.doc.items[i];
			if (row[fieldname] != value) {
				if (condition && !condition(row)) {
					continue;
				}

				frappe.model.set_value(row.doctype, row.name, fieldname, value, "Link");
				changed = true;
			}
		}
		refresh_field("items");
	},

	items_on_form_rendered: function (doc, grid_row) {
		erpnext.setup_serial_no();
	},

	basic_rate: function (doc, cdt, cdn) {
		var item = frappe.model.get_doc(cdt, cdn);
		this.calculate_basic_amount(item);
	},

	s_warehouse: function (doc, cdt, cdn) {
		this.get_warehouse_details(doc, cdt, cdn)
	},

	t_warehouse: function (doc, cdt, cdn) {
		this.get_warehouse_details(doc, cdt, cdn)
	},

	get_warehouse_details: function (doc, cdt, cdn) {
		var me = this;
		var d = locals[cdt][cdn];
		if (!doc.initial_stock_templates) {
			if (!d.bom_no) {
				frappe.call({
					method: "erpnext.stock.doctype.stock_entry.stock_entry.get_warehouse_details",
					args: {
						"args": {
							'item_code': d.item_code,
							'warehouse': cstr(d.s_warehouse) || cstr(d.t_warehouse),
							'transfer_qty': d.transfer_qty,
							'serial_no': d.serial_no,
							'qty': d.s_warehouse ? -1 * d.qty : d.qty,
							'posting_date': this.frm.doc.posting_date,
							'posting_time': this.frm.doc.posting_time
						}
					},
					callback: function (r) {
						if (!r.exc) {
							$.extend(d, r.message);
							me.calculate_basic_amount(d);
						}
					}
				});
			}
		}//end check initial stock template
		else {
			me.calculate_basic_amount(d);
		}
	},

	calculate_basic_amount: function (item) {
		// commented by phuntsho
		// item.basic_amount = flt(flt(item.transfer_qty) * flt(item.basic_rate),
		// 	precision("basic_amount", item));
		// added by phuntsho
		item.basic_amount = flt(flt(item.qty) * flt(item.basic_rate),
			precision("basic_amount", item));
		this.calculate_amount();
	},

	calculate_amount: function () {
		this.calculate_total_additional_costs();

		var total_basic_amount = frappe.utils.sum(
			(this.frm.doc.items || []).map(function (i) { return i.t_warehouse ? flt(i.basic_amount) : 0; })
		);

		for (var i in this.frm.doc.items) {
			var item = this.frm.doc.items[i];

			if (item.t_warehouse && total_basic_amount) {
				item.additional_cost = (flt(item.basic_amount) / total_basic_amount) * this.frm.doc.total_additional_costs;
			} else {
				item.additional_cost = 0;
			}

			item.amount = flt(item.basic_amount + flt(item.additional_cost),
				precision("amount", item));

			item.valuation_rate = flt(flt(item.basic_rate)
				+ (flt(item.additional_cost) / flt(item.transfer_qty)),
				precision("valuation_rate", item));
		}

		refresh_field('items');
	},

	calculate_total_additional_costs: function () {
		var total_additional_costs = frappe.utils.sum(
			(this.frm.doc.additional_costs || []).map(function (c) { return flt(c.amount); })
		);

		this.frm.set_value("total_additional_costs", flt(total_additional_costs, precision("total_additional_costs")));
	},
});

cur_frm.script_manager.make(erpnext.stock.StockEntry);

cur_frm.cscript.toggle_related_fields = function (doc) {
	cur_frm.toggle_enable("from_warehouse", doc.purpose != 'Material Receipt');
	cur_frm.toggle_enable("to_warehouse", doc.purpose != 'Material Issue');

	cur_frm.fields_dict["items"].grid.set_column_disp("s_warehouse", doc.purpose != 'Material Receipt');
	cur_frm.fields_dict["items"].grid.set_column_disp("t_warehouse", doc.purpose != 'Material Issue');
	cur_frm.fields_dict["items"].grid.set_column_disp("issue_to_employee", doc.purpose == 'Material Issue');

	cur_frm.cscript.toggle_enable_bom();

	if (doc.purpose == 'Subcontract') {
		doc.customer = doc.customer_name = doc.customer_address =
			doc.delivery_note_no = doc.sales_invoice_no = null;
	} else {
		doc.customer = doc.customer_name = doc.customer_address =
			doc.delivery_note_no = doc.sales_invoice_no = doc.supplier =
			doc.supplier_name = doc.supplier_address = doc.purchase_receipt_no = null;
	}
	if (doc.purpose == "Material Receipt") {
		cur_frm.set_value("from_bom", 0);
	}

	// Addition costs based on purpose
	cur_frm.toggle_display(["additional_costs", "total_additional_costs", "additional_costs_section"],
		doc.purpose != 'Material Issue');

	cur_frm.fields_dict["items"].grid.set_column_disp("additional_cost", doc.purpose != 'Material Issue');
}

cur_frm.fields_dict['work_order'].get_query = function (doc) {
	return {
		filters: [
			['Work Order', 'docstatus', '=', 1],
			['Work Order', 'qty', '>', '`tabProduction Order`.produced_qty'],
			['Work Order', 'company', '=', cur_frm.doc.company]
		]
	}
}

cur_frm.cscript.purpose = function (doc, cdt, cdn) {
	cur_frm.cscript.toggle_related_fields(doc);
}

// Overloaded query for link batch_no
cur_frm.fields_dict['items'].grid.get_field('batch_no').get_query = function (doc, cdt, cdn) {
	var item = locals[cdt][cdn];
	if (!item.item_code) {
		frappe.throw(__("Please enter Item Code to get batch no"));
	}
	else {
		if (in_list(["Material Transfer for Manufacture", "Manufacture", "Repack", "Subcontract"], doc.purpose)) {
			var filters = {
				'item_code': item.item_code,
				'posting_date': me.frm.doc.posting_date || nowdate()
			}
		} else {
			var filters = {
				'item_code': item.item_code
			}
		}


		if (item.s_warehouse) filters["warehouse"] = item.s_warehouse
		return {
			query: "erpnext.controllers.queries.get_batch_no",
			filters: filters
		}
	}
}

cur_frm.cscript.item_code = function (doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (!doc.initial_stock_templates) {
		if (d.item_code) {
			args = {
				'item_code': d.item_code,
				'warehouse': cstr(d.s_warehouse) || cstr(d.t_warehouse),
				'transfer_qty': d.transfer_qty,
				'serial_no	': d.serial_no,
				'bom_no': d.bom_no,
				'expense_account': d.expense_account,
				'cost_center': d.cost_center,
				'company': cur_frm.doc.company
			};
			return frappe.call({
				doc: cur_frm.doc,
				method: "get_item_details",
				args: args,
				callback: function (r) {
					if (r.message) {
						var d = locals[cdt][cdn];
						var item_group = ''
						$.each(r.message, function (k, v) {
							if (k == 'item_group') {
								item_group = v
							}
							else if (k == 'uom') {
								//don't populate the uom 
								d[k] = null
							}
							else {
								d[k] = v;
							}
						});
						cur_frm.fields_dict["items"].grid.get_field("expense_account").get_query = function (doc) { return { "filters": { "item_group": item_group } } }
						refresh_field("items");
					}
				}
			});
		}
	}
}

cur_frm.cscript.barcode = function (doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.barcode) {
		frappe.call({
			method: "erpnext.stock.get_item_details.get_item_code",
			args: { "barcode": d.barcode },
			callback: function (r) {
				if (!r.exe) {
					frappe.model.set_value(cdt, cdn, "item_code", r.message);
				}
			}
		});
	}
}

cur_frm.cscript.uom = function (doc, cdt, cdn) {
	var d = locals[cdt][cdn];
	if (d.uom && d.item_code) {
		var arg = { 'item_code': d.item_code, 'uom': d.uom, 'qty': d.qty }
		return get_server_fields('get_uom_details', JSON.stringify(arg),
			'items', doc, cdt, cdn, 1);
	}
}

cur_frm.cscript.validate = function (doc, cdt, cdn) {
	cur_frm.cscript.validate_items(doc);
}

cur_frm.cscript.validate_items = function (doc) {
	cl = doc.items || [];
	if (!cl.length) {
		msgprint(__("Item table can not be blank"));
		validated = false;
	}
}

cur_frm.cscript.expense_account = function (doc, cdt, cdn) {
	erpnext.utils.copy_value_in_all_row(doc, cdt, cdn, "items", "expense_account");
}

cur_frm.cscript.cost_center = function (doc, cdt, cdn) {
	erpnext.utils.copy_value_in_all_row(doc, cdt, cdn, "items", "cost_center");
}

cur_frm.cscript.company = function (doc, cdt, cdn) {
	if (doc.company) {
		var company_doc = frappe.get_doc(":Company", doc.company);
		if (company_doc.default_letter_head) {
			cur_frm.set_value("letter_head", company_doc.default_letter_head);
		}
	}
}


frappe.ui.form.on('Landed Cost Taxes and Charges', {
	amount: function (frm) {
		frm.cscript.calculate_amount();
	}
})

//custom Scripts
//Set select option for "Initial Stock Templates"
cur_frm.fields_dict['initial_stock_templates'].get_query = function (doc, dt, dn) {
	return {
		query: "erpnext.stock.doctype.stock_price_template.stock_price_template.get_template_list",
		filters: { naming_series: doc.naming_series, posting_date: doc.posting_date, purpose: 'COP' },
		searchfield: "template_name"
	};
}

//Auto add items based on the values created in the "Initial Stock Template" Setting
cur_frm.cscript.initial_stock_templates = function (doc) {
	cur_frm.call({
		method: "erpnext.stock.doctype.stock_price_template.stock_price_template.get_initial_values",
		args: {
			name: doc.initial_stock_templates
		},
		callback: function (r) {
			if (r.message) {
				cur_frm.clear_table("items");
				var new_row = frappe.model.add_child(cur_frm.doc, "Stock Entry Detail", "items");
				new_row.item_code = r.message[0]['item_code'];
				new_row.item_name = r.message[0]['item_name'];
				new_row.uom = r.message[0]['uom'];
				new_row.stock_uom = r.message[0]['stock_uom'];
				new_row.qty = 0;
				new_row.basic_rate = r.message[0]['rate_amount'];
				new_row.expense_account = r.message[0]['expense_account'];
				new_row.cost_center = r.message[0]['selling_cost_center'];
				new_row.t_warehouse = doc.to_warehouse;
				refresh_field("items");
			}
		}
	});
	if (doc.initial_stock_templates) {
		//Set item table read only
		cur_frm.set_df_property("items", "read_only", 1);
		frappe.meta.get_docfield("Stock Entry Detail", "basic_rate", cur_frm.doc.name).read_only = 1;
		frappe.meta.get_docfield("Stock Entry Detail", "item_code", cur_frm.doc.name).read_only = 1;
		frappe.meta.get_docfield("Stock Entry Detail", "uom", cur_frm.doc.name).read_only = 1;
		refresh_field("items");
	}
	else {
		cur_frm.set_df_property("items", "read_only", 0);
		refresh_field("items");
	}
}

frappe.ui.form.on("Stock Entry", "refresh", function (frm) {
	cur_frm.set_query("job_card", function () {
		return {
			"filters": {
				"docstatus": 0,
				"branch": frm.doc.branch
			}
		};
	});
	cur_frm.set_query("from_warehouse", function () {
		return {
			query: "erpnext.controllers.queries.filter_branch_wh",
			filters: { 'branch': frm.doc.branch }
		}
	});
})

frappe.ui.form.on("Stock Entry", "items_on_form_rendered", function (frm, grid_row, cdt, cdn) {
	var row = cur_frm.open_grid_row();
	if (!row.grid_form.fields_dict.cost_center.value) {
		row.grid_form.fields_dict.cost_center.set_value(frm.doc.user_cost_center)
		row.grid_form.fields_dict.cost_center.refresh()
	}
})

cur_frm.fields_dict['items'].grid.get_field('uom').get_query = function (frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	return {
		query: "erpnext.controllers.queries.get_item_uom",
		filters: { 'item_code': d.item_code }
	}
}

cur_frm.fields_dict['items'].grid.get_field('cost_center').get_query = function (frm, cdt, cdn) {
	var d = locals[cdt][cdn];
	return {
		query: "erpnext.controllers.queries.filter_branch_cost_center",
		filters: { 'branch': frm.branch }
	}
}


