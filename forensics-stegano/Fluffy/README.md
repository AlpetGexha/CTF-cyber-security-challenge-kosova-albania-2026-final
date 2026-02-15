# Fluffy

**Category:** Forensics/Steganography  
**Points:** 250
**Challenge Description:**

<https://drive.google.com/file/d/1MqWfpuja6ZukDX25AJvxgLjx2x2q1GDY/view?usp=sharing>

# [Forensics] Fluffy

> Recovering encrypted notes hidden inside a vacation photo by combining steganography extraction with EXIF-derived AES key reconstruction.

## Overview

| Item       | Value                                                                     |
| ---------- | ------------------------------------------------------------------------- |
| Platform   | CSC26                                                                     |
| Event      | CTF - Final                                                               |
| Category   | Forensics & Steganography                                                 |
| Difficulty | ★★★☆☆                                                                     |
| Date       | 2026-02-15                                                                |
| Flag       | `CSC26{08a25c8cca28c3bb6d99207f457f33847a192972f15b75a822ac87c9fbfe200b}` |

## Problem Statement

> We are given a file named `vacation_photo.png` that appears to be a PNG image. The goal is to find the hidden flag.

**Provided files:**

- `vacation_photo.png` — A 473-byte file disguised as a PNG image

## TL;DR

- The PNG is a fake — it has a valid PNG magic header followed by null bytes, with a **ZIP archive appended** at offset `0x48`
- The ZIP contains two hidden files: `Pictures/.metadata.txt` (EXIF info) and `Documents/.notes.enc` (encrypted notes)
- The metadata reveals `camera_model=Nikon-D750` and `date=2019-08-25`
- The encryption key is derived as `SHA256("Nikon-D750-2019-08-25")` — the model and date joined with a hyphen
- Decryption uses **AES-256-CBC** with the first 16 bytes of the ciphertext as IV

## Background Knowledge

### Steganography via File Appending

A common forensics technique is hiding data by appending one file format to another. Since PNG parsers stop reading at the `IEND` chunk, any data appended after it is ignored by image viewers. In this challenge, the approach is even simpler — the PNG header is followed by null padding, with a ZIP file embedded at a fixed offset.

### ZIP Detection in Binary Files

ZIP files always begin with the magic bytes `PK\x03\x04` (hex `504b0304`). Tools like `binwalk`, `foremost`, or even a manual hex dump can spot these signatures inside other files. The `file` command on this PNG actually reports it as _"Zip archive, with extra data prepended"_.

### AES-CBC with Prepended IV

A standard pattern for AES-CBC encryption is to prepend the random IV (Initialization Vector) to the ciphertext. During decryption, the first 16 bytes are split off as the IV, and the remaining bytes are the actual ciphertext. The key in this challenge is derived by hashing a passphrase with SHA-256 to produce a 32-byte AES-256 key.

### Key Derivation from EXIF Metadata

EXIF metadata embedded in photos often contains camera model, date, GPS coordinates, etc. In this challenge, the metadata file serves as a hint for reconstructing the encryption passphrase. The trick is figuring out the **exact format** — specifically that the camera model and date are joined with a `-` separator.

## Solution

### Step 1: Initial Reconnaissance

Examining the provided file reveals it's not a real PNG:

```bash
$ file vacation_photo.png
vacation_photo.png: Zip archive, with extra data prepended

$ wc -c vacation_photo.png
473 vacation_photo.png

$ xxd vacation_photo.png | head -6
00000000: 8950 4e47 0d0a 1a0a 0000 0000 0000 0000  .PNG............
00000010: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000020: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000030: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000040: 0000 0000 0000 0000 504b 0304 1400 0000  ........PK......
00000050: 0800 8b7e 255c 4e08 99e8 2a00 0000 2800  ...~%\N...*...(.
```

The file starts with a PNG signature (`89 50 4E 47`) but is followed by null bytes — no valid IHDR chunk. At offset `0x48`, we see `PK\x03\x04`: a ZIP archive.

### Step 2: Extracting the Hidden ZIP

The ZIP can be extracted directly since `unzip` and Python's `zipfile` both handle the prepended data:

```bash
$ unzip -l vacation_photo.png
Archive:  vacation_photo.png
  Length      Date    Time    Name
---------  ---------- -----   ----
       40  2026-01-05 15:52   Pictures/.metadata.txt
       96  2026-01-05 15:52   Documents/.notes.enc
---------                     -------
      136                     2 files
```

Two hidden files are revealed:

- `Pictures/.metadata.txt` — 40 bytes of camera metadata
- `Documents/.notes.enc` — 96 bytes of encrypted data

### Step 3: Analyzing the Metadata

```bash
$ cat Pictures/.metadata.txt
camera_model=Nikon-D750
date=2019-08-25
```

This gives us two pieces of information that likely form the encryption key:

- **Camera model:** `Nikon-D750`
- **Date:** `2019-08-25`

### Step 4: Analyzing the Ciphertext

```bash
$ xxd Documents/.notes.enc
00000000: 4d50 5b4b 401a 1d69 d380 1f6d 9e55 874b  MP[K@..i...m.U.K
00000010: 6dc0 de6c 2f5d 5268 0d34 eac2 2e83 52f4  m..l/]Rh.4....R.
00000020: 1f3a 4f93 ccff c84b b00e 5186 d720 4a25  .:O....K..Q.. J%
00000030: 5cf2 39de 7bf7 14be a90a 4d6d 39cc 961c  \.9.{.....Mm9...
00000040: f40f 2081 92a9 ce88 dde8 c689 f51c f03e  .. ............>
00000050: e360 8b33 b4b7 db92 303e 193a bcaa 6533  .`.3....0>.:..e3
```

The file is exactly 96 bytes (6 × 16-byte AES blocks). The first 16 bytes are likely the **IV** for AES-CBC, leaving 80 bytes (5 blocks) of actual ciphertext.

### Step 5: Brute-Forcing the Key Format

The challenge is determining the **exact key string format**. We know the components (`Nikon-D750` and `2019-08-25`) but not how they're combined. A brute-force approach tries multiple separators and hash algorithms:

```python
# Key candidates tried:
# "Nikon-D750_2019-08-25", "Nikon-D750 2019-08-25",
# "Nikon-D7502019-08-25", "Nikon-D750-2019-08-25", ...
# Hash functions: MD5, SHA1, SHA256, SHA512
# Modes: ECB, CBC (zero IV), CBC (prepended IV), CTR
```

The winning combination:

- **Key string:** `Nikon-D750-2019-08-25` (camera-model **hyphen** date)
- **Key derivation:** `SHA256("Nikon-D750-2019-08-25")` → 32 bytes
- **Mode:** AES-256-CBC
- **IV:** First 16 bytes of ciphertext

### Step 6: Decryption and Flag Capture

```python
import hashlib
from Crypto.Cipher import AES

ciphertext = open("Documents/.notes.enc", "rb").read()

key_string = "Nikon-D750-2019-08-25"
key = hashlib.sha256(key_string.encode()).digest()  # 32 bytes → AES-256
iv = ciphertext[:16]
ct = ciphertext[16:]

cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = cipher.decrypt(ct)

# Strip PKCS7 padding
pad_len = plaintext[-1]
plaintext = plaintext[:-pad_len]

print(plaintext.decode())
```

```
$ python3 script.py
[*] Extracted ZIP contents: ['Pictures/.metadata.txt', 'Documents/.notes.enc']
[*] Metadata:
camera_model=Nikon-D750
date=2019-08-25
[*] Loaded 96 bytes of ciphertext

[+] Key string: 'Nikon-D750-2019-08-25'
[+] Cipher:     AES-256-CBC (SHA256 key, IV prepended)
[+] Flag:       CSC26{08a25c8cca28c3bb6d99207f457f33847a192972f15b75a822ac87c9fbfe200b}
```

**Flag:** `CSC26{08a25c8cca28c3bb6d99207f457f33847a192972f15b75a822ac87c9fbfe200b}`

## Tools Used

| Tool                               | Purpose                                                               |
| ---------------------------------- | --------------------------------------------------------------------- |
| `file`                             | Identify the true file type of `vacation_photo.png`                   |
| `xxd`                              | Hex dump to locate the ZIP signature and analyze ciphertext structure |
| `unzip`                            | List and extract contents of the embedded ZIP                         |
| Python `zipfile`                   | Programmatic ZIP extraction in the solve script                       |
| Python `hashlib`                   | SHA-256 key derivation from passphrase                                |
| PyCryptodome (`Crypto.Cipher.AES`) | AES-256-CBC decryption                                                |

## Lessons Learned

### What I Learned

- **Separator matters:** The key was `Nikon-D750-2019-08-25` — the camera model and date joined by a hyphen. Since the model itself contains a hyphen (`Nikon-D750`), it's easy to overlook this format when building key candidates. When brute-forcing, always include the same character that already appears in the components.
- **Prepended IV is standard:** Many real-world AES-CBC implementations prepend the IV to the ciphertext. Always try splitting the first block as IV when encountering unknown encrypted files.

### Mistakes Made

- Initially tried only `_`, space, and concatenation as separators between model and date — missing the `-` that was the correct one
- Wasted time checking for magic file headers (ZIP/PNG/PDF) in the decrypted output, when the plaintext was actually a raw flag string
- Tried XOR, RC4, DES, and Blowfish before systematically testing all AES key format permutations

### Future Improvements

- Build a more comprehensive brute-force framework upfront that tests all common separators, hash functions, and AES modes in a single pass
- When metadata hints at a passphrase, start with the simplest combinations using the natural separator already present in the data

## References

- [PyCryptodome AES Documentation](https://pycryptodome.readthedocs.io/en/latest/src/cipher/aes.html) — AES cipher usage
- [PKCS#7 Padding](<https://en.wikipedia.org/wiki/Padding_(cryptography)#PKCS#5_and_PKCS#7>) — Standard block cipher padding
- [ZIP File Format](<https://en.wikipedia.org/wiki/ZIP_(file_format)>) — PK magic bytes and structure
- [PNG File Structure](http://www.libpng.org/pub/png/spec/1.2/PNG-Structure.html) — PNG signature and chunk format

## Tags

`forensics` `steganography` `aes-cbc` `zip-in-png` `exif-metadata` `key-derivation` `sha256` `crypto`
