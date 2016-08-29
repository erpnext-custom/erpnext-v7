// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt



frappe.provide("erpnext.accounts");

erpnext.accounts.BRSControlPanel = frappe.ui.form.Controller.extend({
	refresh: function() {
		this.frm.disable_save();
		this.show_upload();
	},

	get_template:function() {
		window.location.href = repl(frappe.request.url +
			'?cmd=%(cmd)s', {
				cmd: "erpnext.accounts.doctype.upload_brs_entries.upload_brs_entries.get_template",
			});
	},

	show_upload: function() {
		var me = this;
		var $wrapper = $(cur_frm.fields_dict.upload_html.wrapper).empty();
		// upload
		frappe.upload.make({
			parent: $wrapper,
			args: {
				method: 'erpnext.accounts.doctype.upload_brs_entries.upload_brs_entries.upload'
			},
			sample_url: "e.g. http://emines.smcl.bt/somefile.csv",
			callback: function(attachment, r) {
				var $log_wrapper = $(cur_frm.fields_dict.import_log.wrapper).empty();

				if(!r.messages) r.messages = [];
				// replace links if error has occured
				if(r.exc || r.error) {
					r.messages = $.map(r.message.messages, function(v) {
						var msg = v.replace("Inserted", "Valid")
							.replace("Updated", "Valid").split("<");
						if (msg.length > 1) {
							v = msg[0] + (msg[1].split(">").slice(-1)[0]);
						} else {
							v = msg[0];
						}
						return v;
					});

					r.messages = ["<h4 style='color:red'>"+__("Import Failed!")+"</h4>"]
						.concat(r.messages)
				} else {
					r.messages = ["<h4 style='color:green'>"+__("Import Successful!")+"</h4>"].
						concat(r.message.messages)
				}

				$.each(r.messages, function(i, v) {
					var $p = $('<p>').html(v).appendTo($log_wrapper);
					if(v.substr(0,5)=='Error') {
						$p.css('color', 'red');
					} else if(v.substr(0,8)=='Inserted') {
						$p.css('color', 'green');
					} else if(v.substr(0,7)=='Updated') {
						$p.css('color', 'green');
					} else if(v.substr(0,5)=='Valid') {
						$p.css('color', '#777');
					}
				});
			}
		});

		// rename button
		$wrapper.find('form input[type="submit"]')
			.attr('value', 'Upload and Import')
	}
})

cur_frm.cscript = new erpnext.accounts.BRSControlPanel({frm: cur_frm});
