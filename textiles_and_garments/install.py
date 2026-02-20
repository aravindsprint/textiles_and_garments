import subprocess
import sys
import os
import frappe

def after_migrate():
    _install_requirements()
    _set_r2_config()

def _install_requirements():
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_file):
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", req_file],
            check=True
        )

def _set_r2_config():
    # Only set if not already configured
    if not frappe.conf.get("r2_access_key"):
        access_key = os.environ.get("R2_ACCESS_KEY")
        if access_key:
            frappe.set_value("System Settings", "System Settings", "r2_access_key", access_key)
            subprocess.run(["bench", "set-config", "r2_access_key", access_key], check=True)

    if not frappe.conf.get("r2_secret_key"):
        secret_key = os.environ.get("R2_SECRET_KEY")
        if secret_key:
            subprocess.run(["bench", "set-config", "r2_secret_key", secret_key], check=True)