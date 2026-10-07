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


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key="mobile", limit=5, seconds=60 * 60)
def send_otp(mobile):
    mobile = _normalize(mobile)
    res = _post("/Verifications", {"To": mobile, "Channel": "sms"})
    return {"success": True, "status": res.get("status"), "mobile": mobile}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key="mobile", limit=10, seconds=60 * 60)
def verify_otp(mobile, code):
    mobile = _normalize(mobile)
    code = str(code or "").strip()
    if not code.isdigit():
        frappe.throw(_("Invalid OTP"))

    res = _post("/VerificationCheck", {"To": mobile, "Code": code})
    approved = res.get("status") == "approved"

    # Post-verification hook: e.g. mark a challan delivered, verify a Contact,
    # or log the user in.
    return {"success": approved, "status": res.get("status")}
