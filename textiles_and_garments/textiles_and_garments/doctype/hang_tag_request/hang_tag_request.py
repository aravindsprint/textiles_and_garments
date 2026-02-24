# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt
# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.query_builder.functions import Sum
from frappe.utils import flt, today
import json
import re
import base64
import os


class HangTagRequest(Document):
    def on_submit(self):
        self.upload_certificate_to_r2()

    def get_image_as_base64(self, src, flatten_bg=None):
        """Convert image src to base64 data URI.
        flatten_bg: tuple (R,G,B) to use as background when flattening transparency.
                    Use (0,169,143) for green background, (255,255,255) for white.
                    None = keep transparency as-is.
        """
        site_path = frappe.get_site_path()
        image_data = None

        # Try local file first
        files_match = re.search(r'(/files/.+)$', src)
        if files_match:
            relative_path = files_match.group(1)
            file_path = os.path.join(site_path, "public", relative_path.lstrip("/"))
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    image_data = f.read()

        # Fallback: download via HTTP
        if not image_data and src.startswith("http"):
            try:
                import requests
                response = requests.get(src, timeout=10, verify=False)
                if response.status_code == 200:
                    image_data = response.content
            except Exception:
                pass

        if not image_data:
            return src

        try:
            from PIL import Image
            import io as pil_io

            img = Image.open(pil_io.BytesIO(image_data))

            # Flatten transparency onto specified background color
            if flatten_bg and img.mode in ('RGBA', 'LA', 'PA'):
                background = Image.new('RGB', img.size, flatten_bg)
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode == 'RGBA':
                # Default: flatten onto white
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background

            # Convert CMYK or other modes to RGB
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')

            # Save as high-quality PNG
            buffer = pil_io.BytesIO()
            img.save(buffer, format="PNG", optimize=False)
            buffer.seek(0)
            b64 = base64.b64encode(buffer.read()).decode("utf-8")
            return f"data:image/png;base64,{b64}"

        except ImportError:
            b64 = base64.b64encode(image_data).decode("utf-8")
            ext = os.path.splitext(src)[1].lower()
            mime_map = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
            }
            mime_type = mime_map.get(ext, "image/png")
            return f"data:{mime_type};base64,{b64}"

    def generate_certificate_html(self):
        """Generate certificate HTML directly without Frappe's print wrapper."""

        

        seal_b63 = self.get_image_as_base64(
            "https://erp.pranera.in/files/1508232.png",
            flatten_bg=(0, 169, 143)  # Match #00A98F green
        )

        # Seal image - flatten onto green so it blends perfectly
        seal_b64 = self.get_image_as_base64(
            "https://erp.pranera.in/files/20b6a52.png",
            flatten_bg=(0, 169, 143)  # Match #00A98F green
        )

        brand_name = getattr(self, 'brand_name', None) or self.customer
        year = str(self.validity_of_the_year)[:4]
        cert_number = self.name

        html = f"""<!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <style>
            @page {{
              size: A4 portrait;
              margin: 0;
            }}

            * {{ margin: 0; padding: 0; box-sizing: border-box; }}

            html, body {{
              width: 210mm;
              height: 270mm;
              margin: 0;
              padding: 0;
              font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
              background: #fff;
            }}

            .page {{
              width: 210mm;
              height: 270mm;
              padding: 8mm;
              background: #fff;
            }}

            .certificate {{
              width: 100%;
              height: 100%;
              background-color: #00A98F;
              border-radius: 6px;
              position: relative;
              text-align: center;
              padding: 0 40px 28px;
              overflow: hidden;
            }}


            .content {{
              position: relative;
              z-index: 1;
              padding-top: 20px;
            }}

            .corner {{
              position: absolute;
              width: 36px;
              height: 36px;
              border: 3px solid rgba(255,255,255,0.5);
              z-index: 2;
            }}
            .corner-tl {{ top: 10px; left: 10px; border-right: none; border-bottom: none; border-radius: 5px 0 0 0; }}
            .corner-tr {{ top: 10px; right: 10px; border-left: none; border-bottom: none; border-radius: 0 5px 0 0; }}
            .corner-bl {{ bottom: 10px; left: 10px; border-right: none; border-top: none; border-radius: 0 0 0 5px; }}
            .corner-br {{ bottom: 10px; right: 10px; border-left: none; border-top: none; border-radius: 0 0 5px 0; }}

            .flextra-text {{
              font-size: 36px;
              font-weight: 800;
              color: #fff;
              letter-spacing: 8px;
              text-transform: uppercase;
              margin-bottom: 2px;
              font-style: italic;
            }}

            .flextra-sub {{
              font-size: 8px;
              font-weight: 600;
              color: #fff;
              letter-spacing: 4px;
              text-transform: uppercase;
              margin-bottom: 14px;
            }}

            .seal {{
              display: block;
              width: 180px;
              margin: 0 auto 12px;
            }}

            .tagline {{
              font-size: 10px;
              font-weight: 700;
              color: #fff;
              text-transform: uppercase;
              text-align: center;
              margin: 0 auto 16px;
              border-top: 1px solid rgba(255,255,255,0.4);
              border-bottom: 1px solid rgba(255,255,255,0.4);
              padding: 8px 0;
              width: 80%;
            }}

            .body-text {{
              font-size: 13px;
              color: #fff;
              text-align: center;
              line-height: 1.7;
              margin-bottom: 16px;
            }}

            .brand-name {{
              font-weight: 700;
              text-transform: uppercase;
              border-bottom: 2px solid #fff;
              padding-bottom: 1px;
            }}

            .section-title {{
              font-size: 10px;
              font-weight: 700;
              color: #fff;
              text-transform: uppercase;
              text-align: center;
              margin-bottom: 8px;
            }}

            .auth-text {{
              font-size: 13px;
              color: #fff;
              text-align: center;
              line-height: 1.7;
              margin-bottom: 20px;
            }}

            .validity-label {{
              font-size: 10px;
              font-weight: 700;
              color: #fff;
              text-transform: uppercase;
              text-align: center;
              margin-bottom: 2px;
            }}

            .validity-year {{
              font-size: 48px;
              font-weight: 800;
              color: #fff;
              text-align: center;
              line-height: 1;
              margin-bottom: 8px;
            }}

            .cert-number {{
              font-size: 11px;
              color: rgba(255,255,255,0.85);
              text-align: center;
              font-style: italic;
            }}
            </style>
            </head>
            <body>
            <div class="page">
              <div class="certificate">
                <div class="corner corner-tl"></div>
                <div class="corner corner-tr"></div>
                <div class="corner corner-bl"></div>
                <div class="corner corner-br"></div>

                <!-- Background image at top (faded) -->
                

                <!-- All content -->
                <div class="content">
                  <!-- Flextra Logo as text (always crisp) -->
                  <div class="flextra-text">&nbsp;</div>
                  <div class="flextra-sub"></div>

                  

                  <img class="seal" src="{seal_b63}" alt="Certificate of Authenticity">
                  <br><br>
                  <!-- Certificate of Authenticity Seal -->
                  <img class="seal" src="{seal_b64}" alt="Certificate of Authenticity">

                  <div class="tagline">Trusted Fabrics for Institutional Excellence</div>

                  <div class="body-text"><br><br>
                    This is to certify that garments manufactured under the<br>
                    brand <span class="brand-name">{brand_name}</span> use authentic Flextra fabric.<br><br>
                    The fabric is produced, tested, and supplied by Flextra and<br>
                    meets our established quality standards.
                  </div>
                  <br><br>
                  <div class="section-title">Authenticity &amp; Traceability</div>
                  <div class="auth-text">
                    All Flextra fabrics supplied to <strong>{brand_name}</strong>
                    are genuine and fully traceable.
                  </div>
                  <br><br>
                  <div class="validity-label">This Certificate is Valid for the Year</div>
                  <div class="validity-year">{year}</div>

                  <div class="cert-number">{cert_number}</div>
                </div>
              </div>
            </div>
            </body>
            </html>"""

        return html

    def upload_certificate_to_r2(self):
        try:
            import boto3
            import qrcode
            import io
            from botocore.config import Config
            from frappe.utils.pdf import get_pdf

            # ── 1. Generate PDF directly (bypass Frappe wrapper) ──
            html = self.generate_certificate_html()

            pdf_options = {
                "page-size": "A4",
                "margin-top": "0mm",
                "margin-right": "0mm",
                "margin-bottom": "0mm",
                "margin-left": "0mm",
                "encoding": "UTF-8",
                "no-outline": None,
                "print-media-type": None,
                "disable-smart-shrinking": None,
                "image-quality": "100",
                "image-dpi": "600",
                "dpi": "600",
            }
            pdf_content = get_pdf(html, options=pdf_options)

            # ── 2. R2 Credentials ─────────────────────────────
            R2_ACCOUNT_ID  = "80f14c0d1e3dfd1585dc66327614f067"
            R2_ACCESS_KEY  = "bca0d1c95fe99c19d446e04ffc2d5123"
            R2_SECRET_KEY  = "abb563fc99b50e7a1986099590f96cc3f30727134cbc071eb5761c8bb83b2b5e"
            R2_BUCKET_NAME = "certificates"
            R2_ENDPOINT    = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
            R2_PUBLIC_URL  = "https://certificates.goflextra.com"

            # ── 3. Upload PDF to R2 ───────────────────────────
            s3 = boto3.client(
                "s3",
                endpoint_url=R2_ENDPOINT,
                aws_access_key_id=R2_ACCESS_KEY,
                aws_secret_access_key=R2_SECRET_KEY,
                config=Config(signature_version="s3v4"),
                region_name="auto"
            )

            safe_name = self.name.replace("/", "")
            file_name = f"{safe_name}.pdf"

            s3.put_object(
                Bucket=R2_BUCKET_NAME,
                Key=file_name,
                Body=pdf_content,
                ContentType="application/pdf"
            )

            r2_url = f"{R2_PUBLIC_URL}/{file_name}"

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

            qr_bytes = io.BytesIO()
            qr_image.save(qr_bytes, format="PNG")
            qr_bytes.seek(0)

            # ── 5. Save QR as Frappe File & attach to doc ─────
            qr_filename = f"qr_{safe_name}.png"

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

            qr_file_url = file_doc.file_url

            # ── 6. Update document fields ─────────────────────
            frappe.db.set_value("Hang Tag Request", self.name, {
                "r2_certificate_url": r2_url,
                "qr_code": qr_file_url
            })
            frappe.db.commit()

            frappe.msgprint(
                "Certificate uploaded & QR Code generated successfully!",
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