#!/usr/bin/env python3
"""
vcf_qr_generator.py – vCard ➜ QR (three sizes, optional logo)

Usage:
    python vcf_qr_generator.py
"""

import os
import sys
import qrcode
from pathlib import Path            # stdlib, safe path handling
from PIL import Image

STANDARD_SIZES = (300, 600, 1000)   # pixels
LOGO_SCALE     = 0.30               # logo covers 20 %
EC_LEVEL       = qrcode.constants.ERROR_CORRECT_H


# ---- helpers ---------------------------------------------------------------
def clean_path(raw: str) -> Path:
    """Trim whitespace and surrounding quotes, return a pathlib.Path."""
    raw = raw.strip()
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        raw = raw[1:-1]             # drop surrounding quotes the user pasted
    return Path(raw).expanduser().resolve()

def read_vcf(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        sys.exit(f"❌ VCF not found: {path}")

def load_logo(path: Path, target_px: int) -> Image.Image:
    try:
        logo = Image.open(path).convert("RGBA")
    except Exception as e:
        sys.exit(f"❌ Failed to load logo ({e})")
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
    qr.paste(logo_img, (lx, ly), mask=logo_img)
    return qr
# ---------------------------------------------------------------------------


def main():
    vcf_raw = input("Path to .vcf file: ")
    vcf_path = clean_path(vcf_raw)
    vcard_text = read_vcf(vcf_path)

    logo_raw = input("Path to logo image (leave blank for none): ")
    logo_path = clean_path(logo_raw) if logo_raw.strip() else None

    base = vcf_path.stem

    for size in STANDARD_SIZES:
        qr_img = make_qr_image(vcard_text, size)
        if logo_path:
            logo_img = load_logo(logo_path, size)
            qr_img   = embed_logo(qr_img, logo_img)

        out_name = f"{base}_{size}px.png"
        qr_img.save(out_name, format="PNG")
        print(f"✅ Saved {out_name}")

    print("All done—test the QR codes on a phone before printing.")


if __name__ == "__main__":
    main()
