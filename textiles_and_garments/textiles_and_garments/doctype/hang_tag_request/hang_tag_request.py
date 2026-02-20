# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today
import json

class HangTagRequest(Document):
    def on_submit(self):
        self.upload_certificate_to_r2()

    def upload_certificate_to_r2(self):
        try:
            import boto3
            import qrcode
            import io
            from botocore.config import Config
            from frappe.utils.pdf import get_pdf

            # ── 1. Generate PDF ──────────────────────────────
            html = frappe.get_print(
                doctype="Hang Tag Request",
                name=self.name,
                print_format="Flextra Certificate",
                as_pdf=False
            )
            pdf_content = get_pdf(html)

            # ── 2. R2 Credentials ─────────────────────────────
            R2_ACCOUNT_ID  = "80f14c0d1e3dfd1585dc66327614f067"
            R2_ACCESS_KEY  = frappe.conf.get("r2_access_key")
            R2_SECRET_KEY  = frappe.conf.get("r2_secret_key")
            R2_BUCKET_NAME = "certificates"
            R2_ENDPOINT    = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

            # ── 3. Upload PDF to R2 ───────────────────────────
            s3 = boto3.client(
                "s3",
                endpoint_url=R2_ENDPOINT,
                aws_access_key_id=R2_ACCESS_KEY,
                aws_secret_access_key=R2_SECRET_KEY,
                config=Config(signature_version="s3v4"),
                region_name="auto"
            )

            file_name = f"{self.name}.pdf"
            s3.put_object(
                Bucket=R2_BUCKET_NAME,
                Key=file_name,
                Body=pdf_content,
                ContentType="application/pdf"
            )

            r2_url = f"{R2_ENDPOINT}/{R2_BUCKET_NAME}/{file_name}"

            # ── 4. Generate QR Code for the R2 URL ───────────
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(r2_url)
            qr.make(fit=True)

            qr_image = qr.make_image(fill_color="black", back_color="white")

            # Save QR image to bytes
            qr_bytes = io.BytesIO()
            qr_image.save(qr_bytes, format="PNG")
            qr_bytes.seek(0)

            # ── 5. Save QR as Frappe File & attach to doc ─────
            qr_filename = f"qr_{self.name}.png"

            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": qr_filename,
                "attached_to_doctype": "Hang Tag Request",
                "attached_to_name": self.name,
                "attached_to_field": "qr_code",
                "is_private": 0,
                "content": qr_bytes.read(),
            })
            file_doc.save(ignore_permissions=True)

            qr_file_url = file_doc.file_url  # e.g./files/qr_HTR-0001.png

            # ── 6. Update document fields ─────────────────────
            frappe.db.set_value("Hang Tag Request", self.name, {
                "r2_certificate_url": r2_url,
                "qr_code": qr_file_url
            })
            frappe.db.commit()

            frappe.msgprint(
                f"Certificate uploaded & QR Code generated successfully!",
                alert=True
            )

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "R2 Certificate Upload Failed")
            frappe.throw(f"Certificate upload failed: {str(e)}")


@frappe.whitelist()
def get_sales_invoice_items(sales_invoice):
    """Fetch all items from the given sales invoice."""
    if not sales_invoice:
        return []
    items = frappe.get_all(
        "Sales Invoice Item",
        filters={"parent": sales_invoice},
        fields=["item_code", "warehouse", "qty", "rate", "amount"]
    )
    return items