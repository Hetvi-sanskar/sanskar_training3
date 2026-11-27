# Copyright (c) 2026, Hetvi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class ServiceRequest(Document):
	def before_validate(self):
		# fill a default before the checks run
		if not self.request_date:
			self.request_date = today()

	def validate(self):
		# Task 13 rules
		if self.sla_date and self.request_date and getdate(self.sla_date) < getdate(self.request_date):
			frappe.throw(_("SLA Date cannot be before Request Date"))
		for row in self.spare_parts:
			row.amount = (row.qty or 0) * (row.rate or 0)

		# Task 14 rules
		self.validate_priority_needs_assignee()
		self.validate_status_flow()

	def validate_priority_needs_assignee(self):
		if self.priority == "High" and not self.assigned_to:
			frappe.throw(_("High priority requests must be assigned to someone"))

	def validate_status_flow(self):
		old = self.get_doc_before_save()
		if old and old.status == "In Progress" and self.status == "Open":
			frappe.throw(_("Status cannot go back from In Progress to Open"))

	def before_save(self):
		# last step before the database write
		frappe.logger().info(f"Saving Service Request {self.name}")

	def after_insert(self):
		# runs only once, when the document is first created
		frappe.msgprint(_("Service Request {0} created").format(self.name))

	def on_update(self):
		# runs after every successful save
		if self.has_value_changed("status"):
			frappe.log_error(
				title="Service Request status changed",
				message=f"{self.name} is now {self.status}",
			)

	def before_submit(self):
		if not self.assigned_to:
			frappe.throw(_("Assign the request to an Employee before submitting"))

	def on_submit(self):
		frappe.msgprint(_("Service Request {0} submitted").format(self.name))

	def on_cancel(self):
		frappe.msgprint(_("Service Request {0} cancelled").format(self.name))
