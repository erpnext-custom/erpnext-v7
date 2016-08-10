# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
'''
--------------------------------------------------------------------------------------------------------------------------
Version          Author          CreatedOn          ModifiedOn          Remarks
------------ --------------- ------------------ -------------------  -----------------------------------------------------
1.0		  SSK		                   08/08/2016         DocumentNaming standard is introduced
--------------------------------------------------------------------------------------------------------------------------                                                                          
'''

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

# Ver 1.0 by SSK on 09/08/2016, Following datetime, make_autoname imports are included
import datetime
from frappe.model.naming import make_autoname
from frappe import msgprint, _, scrub

class DSARates(Document):
        # Ver 1.0 by SSK on 09/08/2016, autoname() method is added
	def autoname(self):
                #msgprint(_("{0}").format(series_seq))
                #self.name = make_autoname(str(self.country)+'-'+str(self.dsa_rate))
                self.name = str(self.country)+'-'+str(self.dsa_rate)


        def validate(self):
                #msgprint(_("{0}").format("What is goingon..."))
                pass
