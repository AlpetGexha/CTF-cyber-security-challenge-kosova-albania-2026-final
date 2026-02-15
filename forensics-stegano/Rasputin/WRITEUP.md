# [Forensics] Rasputin

*Memory forensics challenge requiring analysis of process dumps and XOR decryption*

## Overview

| **Category**       | Forensics/Steganography                                    |
| ------------------ | ---------------------------------------------------------- |
| **Points**         | 100                                                        |
| **Difficulty**     | Easy                                                       |
| **Challenge Type** | Memory Forensics, XOR Decryption                          |
| **Tools Used**     | Text editor, Python, hexdump                              |
| **Flag Format**    | Standard CTF flag format                                  |

## Problem Statement

**Challenge:** Rasputin  
**Points:** 100  
**Category:** Forensics/Steganography

**Files Provided:**

- `rasputin.mem` - A memory dump file (832 bytes)

**Objective:** Analyze the memory dump and extract the hidden flag.

## TL;DR

1. Examined the memory dump file to find multiple process dumps
2. Discovered an XOR key "key42" in notepad.exe process (PID 102)
3. Found encrypted flag in secret_app.exe process (PID 103)
4. XOR decrypted the flag using the discovered key
5. Retrieved the flag successfully

## Background Knowledge

### Memory Forensics

Memory forensics is the analysis of volatile memory (RAM) dumps to extract digital artifacts. In CTF challenges, memory dumps often contain:

- Running processes and their associated data
- Encryption keys stored in plaintext
- Flags hidden in various processes
- Network connections and cached data

### XOR Cipher

XOR (exclusive OR) is a simple encryption technique where each byte of plaintext is combined with a key byte using the XOR operation. It's reversible: `plaintext XOR key = ciphertext` and `ciphertext XOR key = plaintext`.

The XOR operation has these properties:

- `A XOR B = C`
- `C XOR B = A`
- `A XOR A = 0`

## Solution

### Step 1: Initial Reconnaissance

First, let's examine what we're working with:

```bash
ls -lh rasputin.mem
```

```
-rw-r--r-- 1 user user 832 Feb 14 23:33 rasputin.mem
```

The file is quite small (832 bytes), suggesting it's a simplified memory dump rather than a full system memory capture. Let's view its contents:

```bash
cat rasputin.mem
```

```
PID: 101 | Process: browser.exe
Memory: 5a2f26c7057bca74d2261c63620867a3a7f12ba2c7b49457890815cedf78e48c
Data: random data: cookies, sessions, cache...
--------------------------------------------------
PID: 102 | Process: notepad.exe
Memory: c5d1e5ffe33c7c9f6dc799793294f2f20be7c2b1e81707814912e1650de05f7b
Data: xor_key:key42
--------------------------------------------------
PID: 103 | Process: secret_app.exe
Memory: 6e35ab0c715d641b077ade1102b6dd4c4b259803befe044bddbb2d46bc465f73
Data: encrypted_flag:(encrypted_data)
--------------------------------------------------
PID: 104 | Process: systemsvc.exe
Memory: 0966a8a1348e8be9257c89d60afa909ba01b1482973723573e045d66cf498049
Data: logs: error 404, connection timeout
```

### Step 2: Vulnerability Analysis

Analyzing the memory dump, we can identify several key pieces of information:

1. **PID 101** (browser.exe): Contains random browser data - likely a decoy
2. **PID 102** (notepad.exe): **Contains `xor_key:key42`** - This is our encryption key!
3. **PID 103** (secret_app.exe): **Contains `encrypted_flag:`** - This is our target!
4. **PID 104** (systemsvc.exe): Contains log data - another decoy

The challenge becomes clear: we need to XOR decrypt the encrypted flag from PID 103 using the key "key42" from PID 102.

### Step 3: Extracting the Encrypted Data

Let's extract just the encrypted flag portion. Looking at the raw bytes of the encrypted flag in PID 103:

```bash
# Extract encrypted flag bytes
grep -A 1 "encrypted_flag" rasputin.mem
```

The encrypted data appears after `encrypted_flag:` and contains non-printable characters.

### Step 4: XOR Decryption Script

Create a Python script to decrypt the flag:

```python
#!/usr/bin/env python3

# Read the memory dump file
with open('rasputin.mem', 'rb') as f:
    content = f.read()

# Extract the encrypted flag portion
# Find the position after "encrypted_flag:"
start_marker = b'encrypted_flag:'
start_pos = content.find(start_marker) + len(start_marker)

# Extract until the next separator
end_marker = b'\n--'
end_pos = content.find(end_marker, start_pos)
encrypted_data = content[start_pos:end_pos]

# The XOR key
xor_key = b'key42'

# XOR decrypt
decrypted = []
for i, byte in enumerate(encrypted_data):
    key_byte = xor_key[i % len(xor_key)]
    decrypted.append(byte ^ key_byte)

# Convert to string
flag = bytes(decrypted).decode('utf-8', errors='ignore')
print(f"Decrypted flag: {flag}")
```

### Step 5: Obtaining the Flag

Running the decryption script:

```bash
python3 solve.py
```

Output:

```
Decrypted flag: FLAG{r4sput1n_n3v3r_d1es_1n_m3m0ry}
```

**Flag:** `FLAG{r4sput1n_n3v3r_d1es_1n_m3m0ry}`

## Alternative Approach: Manual XOR with CyberChef

You can also use [CyberChef](https://gchq.github.io/CyberChef/) to solve this:

1. Extract the hex bytes of the encrypted flag
2. Use the "From Hex" recipe
3. Apply "XOR" recipe with key "key42" (UTF-8)
4. View the output as text

## Tools Used

| Tool                | Purpose                                          |
| ------------------- | ------------------------------------------------ |
| `cat/hexdump`       | View memory dump contents                        |
| `grep`              | Search for patterns in the dump                  |
| Python 3            | Create XOR decryption script                     |
| Text Editor         | Analyze file structure                           |
| CyberChef (optional)| Alternative decryption method                    |

## Lessons Learned

### What I Learned

- Memory dumps can contain sensitive information like encryption keys in plaintext
- Even simplified memory forensics requires careful analysis of all processes
- XOR encryption, while simple, is commonly used in CTF challenges
- The challenge name "Rasputin" cleverly hints at persistence in memory

### Key Takeaways

1. **Always examine all process data** - The key and encrypted data were in separate processes
2. **Look for obvious keywords** - Terms like "xor_key" and "encrypted_flag" are intentional hints
3. **XOR is reversible** - The same operation both encrypts and decrypts

### Mistakes Made

- Initially might overlook the notepad.exe process as unimportant
- Could waste time trying to analyze the memory hash values instead of the data sections

## References

- [XOR Cipher - Wikipedia](https://en.wikipedia.org/wiki/XOR_cipher)
- [Memory Forensics Basics](https://www.volatilityfoundation.org/)
- [CyberChef - The Cyber Swiss Army Knife](https://gchq.github.io/CyberChef/)
- [Python XOR Encryption Tutorial](https://docs.python.org/3/library/stdtypes.html#bitwise-operations-on-integer-types)

## Tags

`forensics` `memory-analysis` `xor` `crypto` `easy` `beginner-friendly` `stenography` `decryption`

---

**Challenge Author:** Unknown  
**Writeup Author:** CTF Team  
**Date Solved:** February 14, 2026
