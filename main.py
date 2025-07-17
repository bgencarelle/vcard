#!/usr/bin/env python3
"""
vcf_qr_generator.py
-------------------
Create QR codes from a vCard (.vcf) file.
Optionally embeds a logo and saves three standard sizes.

Dependencies (install once):
    pip install qrcode[pil] Pillow
"""

import os
import sys
import qrcode
from PIL import Image

STANDARD_SIZES = (300, 600, 1000)       # pixels
LOGO_SCALE     = 0.20                    # logo occupies 20 % of QR side
EC_LEVEL       = qrcode.constants.ERROR_CORRECT_H  # High (30 % recovery)

def read_vcf(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        sys.exit(f"❌ VCF not found: {path}")

def load_logo(path: str, target_px: int) -> Image.Image:
    try:
        logo = Image.open(path).convert("RGBA")
    except Exception as e:
        sys.exit(f"❌ Failed to load logo ({e})")

    # Resize logo proportionally
    side = int(target_px * LOGO_SCALE)
    return logo.resize((side, side), Image.LANCZOS)

def make_qr_image(data: str, size_px: int) -> Image.Image:
    qr = qrcode.QRCode(error_correction=EC_LEVEL, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    return img.resize((size_px, size_px), Image.LANCZOS)

def embed_logo(qr_img: Image.Image, logo_img: Image.Image) -> Image.Image:
    qr = qr_img.copy()
    lx = (qr.width  - logo_img.width)  // 2
    ly = (qr.height - logo_img.height) // 2
    qr.paste(logo_img, (lx, ly), mask=logo_img)   # transparency-aware paste
    return qr

def main():
    vcf_path = input("Path to .vcf file: ").strip()
    vcard_text = read_vcf(vcf_path)

    logo_path = input("Path to logo image (leave blank for none): ").strip()
    use_logo  = bool(logo_path)

    base = os.path.splitext(os.path.basename(vcf_path))[0]

    for size in STANDARD_SIZES:
        qr_img = make_qr_image(vcard_text, size)
        if use_logo:
            logo_img = load_logo(logo_path, size)
            qr_img   = embed_logo(qr_img, logo_img)

        out_name = f"{base}_{size}px.png"
        qr_img.save(out_name, format="PNG")
        print(f"✅ Saved {out_name}")

    print("Done. Test scannability on a phone before distributing.")

if __name__ == "__main__":
    main()
