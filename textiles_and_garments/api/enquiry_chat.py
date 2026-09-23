"""
Enquiry Chat APIs.

Enquiry Chat (parent, autoincrement ID = enquiry_id)
  └── messages  (child table: Enquiry Message)

All endpoints are called with Frappe token auth:
    Authorization: token <api_key>:<api_secret>

Customer side  (role: Enquiry Chat API)
    POST /api/method/textiles_and_garments.api.enquiry_chat.create_enquiry
    POST /api/method/textiles_and_garments.api.enquiry_chat.send_message
    GET  /api/method/textiles_and_garments.api.enquiry_chat.get_messages?enquiry_id=101

Admin side     (role: Enquiry Chat Admin)
    POST /api/method/textiles_and_garments.api.enquiry_chat.admin_reply
    GET  /api/method/textiles_and_garments.api.enquiry_chat.admin_get_messages?enquiry_id=101

Responses are written at the top level of the JSON body (not wrapped
in Frappe's usual {"message": ...}) to match the agreed API contract.
"""

import json
from datetime import timezone
from zoneinfo import ZoneInfo

import frappe
from frappe import _
from frappe.utils import get_datetime, get_system_timezone

PARENT = "Enquiry Chat"
CHILD = "Enquiry Message"
CUSTOMER_ROLES = {"Enquiry Chat API", "System Manager"}
ADMIN_ROLES = {"Enquiry Chat Admin", "System Manager"}


# ---------------------------------------------------------------- helpers

def _require_roles(allowed):
	if not allowed.intersection(frappe.get_roles()):
		frappe.throw(_("Not permitted"), frappe.PermissionError)


def _get_enquiry_id(enquiry_id):
	if not enquiry_id:
		frappe.throw(_("enquiry_id is required"))
	try:
		enquiry_id = int(enquiry_id)
	except (TypeError, ValueError):
		frappe.throw(_("enquiry_id must be a number"))
	if not frappe.db.exists(PARENT, enquiry_id):
		frappe.throw(_("Enquiry {0} not found").format(enquiry_id), frappe.DoesNotExistError)
	return enquiry_id


def _to_utc_iso(dt):
	"""Frappe stores naive datetimes in the system timezone; return UTC ISO-8601."""
	if not dt:
		return None
	dt = get_datetime(dt).replace(microsecond=0)
	local = dt.replace(tzinfo=ZoneInfo(get_system_timezone()))
	return local.astimezone(timezone.utc).isoformat()


def _parse_files(value):
	if not value:
		return []
	if isinstance(value, str):
		try:
			value = json.loads(value)
		except ValueError:
			return []
	return value if isinstance(value, list) else []


def _serialize(row, enquiry_id=None):
	data = {
		"sender": row.sender,
		"message": row.message or "",
		"files": _parse_files(row.files),
		"created_at": _to_utc_iso(row.sent_at),
		"seen_by": {
			"customer": bool(row.seen_by_customer),
			"admin": bool(row.seen_by_admin),
		},
	}
	if enquiry_id is not None:
		data = {"doctype": CHILD, "enquiry_id": int(enquiry_id), **data}
	return data


def _uploaded_files():
	request = getattr(frappe.local, "request", None)
	if not request or not getattr(request, "files", None):
		return []
	return [f for f in request.files.getlist("files") if f and f.filename]


def _save_files(enquiry_id, uploads):
	"""Save uploads as private Files attached to the parent Enquiry Chat."""
	saved = []
	for f in uploads:
		file_doc = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": f.filename,
				"content": f.stream.read(),
				"attached_to_doctype": PARENT,
				"attached_to_name": str(enquiry_id),
				"is_private": 1,
			}
		).insert(ignore_permissions=True)
		saved.append({"file_name": file_doc.file_name, "file_url": file_doc.file_url})
	return saved


def _add_message(enquiry_id, sender, message):
	message = (message or "").strip()
	uploads = _uploaded_files()
	if not message and not uploads:
		frappe.throw(_("message is required"))

	# Lock the parent row so simultaneous customer/admin posts don't collide
	chat = frappe.get_doc(PARENT, enquiry_id, for_update=True)
	files = _save_files(enquiry_id, uploads)

	row = chat.append(
		"messages",
		{
			"sender": sender,
			"message": message,
			"files": json.dumps(files) if files else None,
		},
	)
	chat.save(ignore_permissions=True)  # EnquiryChat.validate sets sent_at / seen flags / status
	return row


def _respond_sent(enquiry_id, row):
	frappe.response["success"] = True
	frappe.response["message"] = "Message sent."
	frappe.response["chat_message"] = _serialize(row, enquiry_id)


def _respond_list(enquiry_id, viewer):
	rows = frappe.get_all(
		CHILD,
		filters={"parenttype": PARENT, "parent": str(enquiry_id), "parentfield": "messages"},
		fields=["name", "sender", "message", "files", "sent_at",
		        "seen_by_customer", "seen_by_admin"],
		order_by="idx asc",
	)

	frappe.response["success"] = True
	frappe.response["doctype"] = CHILD
	frappe.response["enquiry_id"] = enquiry_id
	frappe.response["messages"] = [_serialize(r) for r in rows]

	# After returning the current state, mark the other side's messages as seen
	other = "admin" if viewer == "customer" else "customer"
	seen_field = f"seen_by_{viewer}"
	unseen = [r.name for r in rows if r.sender == other and not r[seen_field]]
	if unseen:
		frappe.db.set_value(CHILD, {"name": ["in", unseen]}, seen_field, 1, update_modified=False)
		frappe.db.commit()  # GET requests are not auto-committed


# ---------------------------------------------------------------- customer

@frappe.whitelist(methods=["POST"])
def create_enquiry(subject=None, message=None, customer_name=None,
                   customer_email=None, external_customer_id=None):
	"""Create a new Enquiry Chat, optionally with a first customer message."""
	_require_roles(CUSTOMER_ROLES)

	chat = frappe.get_doc(
		{
			"doctype": PARENT,
			"subject": subject,
			"customer_name": customer_name,
			"customer_email": customer_email,
			"external_customer_id": external_customer_id,
		}
	).insert(ignore_permissions=True)
	enquiry_id = int(chat.name)

	frappe.response["success"] = True
	frappe.response["message"] = "Enquiry created."
	frappe.response["enquiry_id"] = enquiry_id

	if (message or "").strip() or _uploaded_files():
		row = _add_message(enquiry_id, "customer", message)
		frappe.response["chat_message"] = _serialize(row, enquiry_id)


@frappe.whitelist(methods=["POST"])
def send_message(enquiry_id=None, message=None):
	"""Customer -> admin.  Contract: POST /api/enquiries/{enquiryId}/messages"""
	_require_roles(CUSTOMER_ROLES)
	enquiry_id = _get_enquiry_id(enquiry_id)
	row = _add_message(enquiry_id, "customer", message)
	_respond_sent(enquiry_id, row)


@frappe.whitelist(methods=["GET"])
def get_messages(enquiry_id=None):
	"""Contract: GET /api/enquiries/{enquiryId}/messages"""
	_require_roles(CUSTOMER_ROLES)
	enquiry_id = _get_enquiry_id(enquiry_id)
	_respond_list(enquiry_id, viewer="customer")


# ---------------------------------------------------------------- admin

@frappe.whitelist(methods=["POST"])
def admin_reply(enquiry_id=None, message=None):
	"""Admin -> customer.  Contract: POST /api/admin/enquiries/{enquiryId}/reply"""
	_require_roles(ADMIN_ROLES)
	enquiry_id = _get_enquiry_id(enquiry_id)
	row = _add_message(enquiry_id, "admin", message)
	_respond_sent(enquiry_id, row)


@frappe.whitelist(methods=["GET"])
def admin_get_messages(enquiry_id=None):
	"""Contract: GET /api/admin/enquiries/{enquiryId}/message"""
	_require_roles(ADMIN_ROLES)
	enquiry_id = _get_enquiry_id(enquiry_id)
	_respond_list(enquiry_id, viewer="admin")
