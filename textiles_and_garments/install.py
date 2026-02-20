import subprocess
import sys
import os
import frappe

def after_migrate():
    _install_requirements()

def _install_requirements():
    req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_file):
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", req_file],
            check=True
        )

