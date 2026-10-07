"""
SMS OTP APIs via Twilio Verify.

Twilio generates, delivers, expires and checks the code; nothing is stored here.

    POST /api/method/textiles_and_garments.api.otp.send_otp
         {"mobile": "9876543210"}
    POST /api/method/textiles_and_garments.api.otp.verify_otp
         {"mobile": "9876543210", "code": "123456"}

Credentials live in site_config.json (never in code):
    bench --site <site> set-config twilio_account_sid "AC..."
    bench --site <site> set-config twilio_auth_token  "..."
    bench --site <site> set-config twilio_verify_sid  "VA..."
"""

import re

import frappe
import requests
from frappe import _
from frappe.rate_limiter import rate_limit

VERIFY_BASE = "https://verify.twilio.com/v2/Services/{sid}"
E164 = re.compile(r"^\+[1-9]\d{7,14}$")


def _creds():
    sid = frappe.conf.get("twilio_account_sid")
    token = frappe.conf.get("twilio_auth_token")
    service = frappe.conf.get("twilio_verify_sid")
    if not (sid and token and service):
        frappe.throw(_("Twilio is not configured on this site"))
    return sid, token, service


def _normalize(mobile):
    mobile = (mobile or "").strip().replace(" ", "").replace("-", "")
    # Bare 10-digit Indian mobile -> +91
    if re.fullmatch(r"[6-9]\d{9}", mobile):
        mobile = "+91" + mobile
    elif re.fullmatch(r"91[6-9]\d{9}", mobile):
        mobile = "+" + mobile
    if not E164.match(mobile):
        frappe.throw(_("Enter a valid mobile number, e.g. 9876543210 or +919876543210"))
    return mobile


def _post(path, data):
    sid, token, service = _creds()
    url = VERIFY_BASE.format(sid=service) + path
    try:
        r = requests.post(url, data=data, auth=(sid, token), timeout=15)
    except requests.RequestException:
        frappe.log_error(frappe.get_traceback(), "Twilio OTP request failed")
        frappe.throw(_("Could not reach SMS provider. Please try again."))

    try:
        body = r.json()
    except ValueError:
        body = {}

    if r.status_code >= 400:
        frappe.log_error(f"{r.status_code}: {body}", "Twilio OTP error")
        code = body.get("code")
        if code == 60203:  # max send attempts reached
            frappe.throw(_("Too many OTP requests. Please wait a few minutes."))
        if code == 20404:  # no pending verification / expired
            frappe.throw(_("OTP expired or not requested. Please request a new one."))
        if code == 60200:  # invalid parameter (bad number)
            frappe.throw(_("Invalid mobile number."))
        frappe.throw(_("SMS provider error. Please try again."))
    return body


def _send(mobile):
    res = _post("/Verifications", {"To": mobile, "Channel": "sms"})
    return res.get("status")


def _check(mobile, code):
    code = str(code or "").strip()
    if not (code.isdigit() and 4 <= len(code) <= 10):
        frappe.throw(_("Invalid OTP"))
    res = _post("/VerificationCheck", {"To": mobile, "Code": code})
    return res.get("status") == "approved"


def _mask(mobile):
    return mobile[:3] + "*" * (len(mobile) - 7) + mobile[-4:]


# ---------------------------------------------------------------------------
# Generic endpoints (any mobile number)
# ---------------------------------------------------------------------------

@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key="mobile", limit=5, seconds=60 * 60)
def send_otp(mobile):
    mobile = _normalize(mobile)
    status = _send(mobile)
    return {"success": True, "status": status, "mobile": mobile}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key="mobile", limit=10, seconds=60 * 60)
def verify_otp(mobile, code):
    mobile = _normalize(mobile)
    approved = _check(mobile, code)
    return {"success": approved, "status": "approved" if approved else "pending"}


# ---------------------------------------------------------------------------
# Sales Invoice delivery OTP
#   custom_otp_number                 (Data)   - code typed by the user
#   custom_otp_verified_and_delivered (Select) - No / Yes, set only by verification
# The mobile is read from the invoice on the server, never from the browser.
# ---------------------------------------------------------------------------

VERIFIED_FIELD = "custom_otp_verified_and_delivered"
OTP_FIELD = "custom_otp_number"


def _invoice_mobile(doc):
    for field in ("purchaser_mobile_no", "customers_mobileno"):
        raw = re.sub(r"[^\d+]", "", str(doc.get(field) or ""))
        if raw in ("", "0", "+"):
            continue
        try:
            return _normalize(raw)
        except frappe.ValidationError:
            frappe.clear_messages()
            continue
    frappe.throw(_("No valid Purchaser Mobile No on {0}").format(doc.name))


def _get_invoice(invoice):
    doc = frappe.get_doc("Sales Invoice", invoice)
    doc.check_permission("read")
    if doc.docstatus != 1:
        frappe.throw(_("Submit the invoice before OTP verification"))
    return doc


@frappe.whitelist(methods=["POST"])
@rate_limit(key="invoice", limit=5, seconds=60 * 60)
def send_invoice_otp(invoice):
    doc = _get_invoice(invoice)
    if doc.get(VERIFIED_FIELD) == "Yes":
        frappe.throw(_("Delivery is already OTP verified"))
    mobile = _invoice_mobile(doc)
    _send(mobile)
    doc.add_comment("Info", _("Delivery OTP sent to {0}").format(_mask(mobile)))
    return {"success": True, "mobile": _mask(mobile)}


@frappe.whitelist(methods=["POST"])
@rate_limit(key="invoice", limit=10, seconds=60 * 60)
def verify_invoice_otp(invoice, code):
    doc = _get_invoice(invoice)
    if doc.get(VERIFIED_FIELD) == "Yes":
        return {"success": True, "already_verified": True}

    mobile = _invoice_mobile(doc)
    if not _check(mobile, code):
        return {"success": False, "message": _("Incorrect OTP")}

    # db_set writes straight to the submitted doc without re-running validations
    doc.db_set({VERIFIED_FIELD: "Yes", OTP_FIELD: str(code).strip()})
    doc.add_comment(
        "Info", _("Delivery OTP verified for {0} by {1}").format(_mask(mobile), frappe.session.user)
    )
    return {"success": True}


def guard_otp_fields(doc, method=None):
    """doc_event (validate, before_update_after_submit): "Yes" can only come from verify_invoice_otp."""
    if doc.is_new():
        # Amend / Duplicate must not inherit an earlier verification
        doc.set(VERIFIED_FIELD, "No")
        doc.set(OTP_FIELD, None)
        return
    before = doc.get_doc_before_save()
    old = before.get(VERIFIED_FIELD) if before else None
    if doc.get(VERIFIED_FIELD) == "Yes" and old != "Yes":
        frappe.throw(_("OTP Verified and Delivered is set automatically after entering the correct OTP"))
