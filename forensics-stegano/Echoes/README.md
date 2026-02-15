# Echoes

**Category:** Forensics/Steganography  
**Points:** 400
**Challenge Description:**

## Problem Statement

- Extracted three JPEG images from the zip: `image1.jpg`, `image2.jpg`, and `image3_corrupted.jpg`
- Found a hidden password `P1x3l5h4d0wK3y!` embedded in `image2.jpg`'s JPEG comment metadata
- Extracted two base64 chunks from `image1.jpg` and `image2.jpg` using **steghide** with an empty passphrase
- Concatenated the chunks to form an OpenSSL "Salted\_\_" encrypted blob
- Decrypted using AES-128-CBC with PBKDF2 key derivation (SHA-256 digest) and the recovered password

## Solution

### Step 1: Extracting and Identifying the Files

Unzip the archive and identify the contents:

```bash
$ unzip phantom_images.zip
Archive:  phantom_images.zip
  inflating: phantom_images/image1.jpg
  inflating: phantom_images/image2.jpg
  inflating: phantom_images/image3_corrupted.jpg

$ file phantom_images/*
image1.jpg:           JPEG image data, JFIF standard 1.01, 512x512
image2.jpg:           JPEG image data, JFIF standard 1.01, comment: "P1x3l5h4d0wK3y!", 512x512
image3_corrupted.jpg: JPEG image data, JFIF standard 1.01, 512x512
```

Key observation: the `file` command immediately reveals that `image2.jpg` has a **JPEG comment** containing `P1x3l5h4d0wK3y!`. This looks like a password — note the leetspeak: "PixelShadowKey!".

### Step 2: Metadata & Structural Analysis

Run `exiftool` to get full metadata and compare file sizes:

```bash
$ exiftool image1.jpg image2.jpg image3_corrupted.jpg | grep -E "File Name|File Size|Comment"
File Name : image1.jpg
File Size : 4.9 kB
File Name : image2.jpg
File Size : 4.9 kB
Comment   : P1x3l5h4d0wK3y!
File Name : image3_corrupted.jpg
File Size : 2.4 kB
```

Observations:

- **image1** and **image2** are ~4.9 kB each — normal for a 512×512 solid-color JPEG
- **image3** is only 2.4 kB — significantly truncated
- **image3** is missing the JPEG EOI marker (`FFD9`), confirming it's corrupted/truncated

Opening the images reveals they are solid single-color images:

- `image1.jpg`: RGB(84, 147, 30) — green
- `image2.jpg`: RGB(88, 29, 195) — purple
- `image3_corrupted.jpg`: RGB(248, 79, 58) — red/orange (confirmed by creating a reference JPEG)

### Step 3: Extracting Hidden Data with Steghide

Try steghide extraction on each image. Starting with an **empty passphrase**:

```bash
$ steghide extract -sf image1.jpg -p ""
wrote extracted data to "chunk1.txt".

$ steghide extract -sf image2.jpg -p ""
wrote extracted data to "chunk2.txt".

$ steghide extract -sf image3_corrupted.jpg -p ""
Premature end of JPEG file
steghide: could not extract any data with that passphrase!
```

**image3** is too corrupted for steghide to process. Let's examine the extracted chunks:

```bash
$ cat chunk1.txt
U2FsdGVkX18vOVMg1+njSFwRpVgv6J0+aqQ2SeMPRt7ScsZInG4yZI

$ cat chunk2.txt
QIJfuzgx7TnoCmpWjnfubVR+oLddbW3YhCJu9LuAh5YgU+b2K728I=
```

Both chunks are base64 fragments. The first chunk starts with `U2FsdGVkX1` which decodes to `Salted__` — the signature of OpenSSL encrypted data.

### Step 5: Assembling and Decrypting the Flag

Concatenate the two chunks and decrypt:

```bash
# Combine chunks into a single base64 blob
$ cat chunk1.txt chunk2.txt > combined.b64

# Decode from base64 to binary
$ base64 -d combined.b64 > combined.enc

# Verify the Salted__ header
$ xxd combined.enc | head -1
00000000: 5361 6c74 6564 5f5f 2f39 5320 d7e9 e348  Salted__/9S ...H
```

The encrypted blob is 80 bytes: 8 (`Salted__`) + 8 (salt) + 64 (ciphertext = 4 AES blocks).

Decrypt using **AES-128-CBC** with **PBKDF2** key derivation and the password from image2's comment:

```bash
$ openssl enc -aes-128-cbc -d -pbkdf2 -md sha256 \
    -in combined.enc \
    -pass pass:P1x3l5h4d0wK3y!
CSC26{9b2f4e7a1d3c6b8f2e9a7d4b1f3e6c8a2d9b7f4e1c3a6d8f2b9e5}
```

> **Flag:** `CSC26{9b2f4e7a1d3c6b8f2e9a7d4b1f3e6c8a2d9b7f4e1c3a6d8f2b9e5}`
