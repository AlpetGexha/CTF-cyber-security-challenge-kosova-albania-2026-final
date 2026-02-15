#!/usr/bin/env python3
"""
Fluffy CTF Challenge - Solve Script
Decrypts .notes.enc using metadata from the embedded ZIP in vacation_photo.png.

Key derivation:
  - Key string: "Nikon-D750-2019-08-25" (from EXIF metadata)
  - AES-256-CBC with SHA256-hashed key
  - IV = first 16 bytes of ciphertext
"""

import hashlib
import os
import sys
import zipfile
from Crypto.Cipher import AES

CHALLENGE_DIR = os.path.dirname(os.path.abspath(__file__))
FLUFFY_DIR = os.path.dirname(CHALLENGE_DIR)

# ── Step 1: Extract hidden ZIP from vacation_photo.png ──────────────────────
png_path = os.path.join(FLUFFY_DIR, "vacation_photo.png")
if not os.path.exists(png_path):
    sys.exit(f"Error: {png_path} not found.")

# The PNG has a ZIP appended at offset 0x48 (after null-padded PNG header)
ZIP_OFFSET = 0x48
with open(png_path, "rb") as f:
    f.seek(ZIP_OFFSET)
    zip_data = f.read()

# Verify ZIP magic
assert zip_data[:4] == b"PK\x03\x04", "No ZIP found at expected offset"

# Write temp ZIP and extract files
import tempfile, io
zf = zipfile.ZipFile(io.BytesIO(zip_data))
print(f"[*] Extracted ZIP contents: {zf.namelist()}")

# ── Step 2: Read metadata ───────────────────────────────────────────────────
metadata = zf.read("Pictures/.metadata.txt").decode()
print(f"[*] Metadata:\n{metadata.strip()}")

meta = {}
for line in metadata.strip().splitlines():
    k, v = line.split("=", 1)
    meta[k] = v

camera = meta["camera_model"]  # Nikon-D750
date = meta["date"]            # 2019-08-25

# ── Step 3: Read encrypted notes ────────────────────────────────────────────
ciphertext = zf.read("Documents/.notes.enc")
print(f"[*] Loaded {len(ciphertext)} bytes of ciphertext")

# ── Step 4: Derive key and decrypt ──────────────────────────────────────────
# Key = SHA256("Nikon-D750-2019-08-25") → 32 bytes for AES-256
# IV  = first 16 bytes of ciphertext (prepended IV)
key_string = f"{camera}-{date}"
key = hashlib.sha256(key_string.encode()).digest()
iv = ciphertext[:16]
ct = ciphertext[16:]

cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = cipher.decrypt(ct)

# Strip PKCS7 padding
pad_len = plaintext[-1]
if 1 <= pad_len <= 16 and plaintext[-pad_len:] == bytes([pad_len]) * pad_len:
    plaintext = plaintext[:-pad_len]

flag = plaintext.decode()
print(f"\n[+] Key string: '{key_string}'")
print(f"[+] Cipher:     AES-256-CBC (SHA256 key, IV prepended)")
print(f"[+] Flag:       {flag}")
