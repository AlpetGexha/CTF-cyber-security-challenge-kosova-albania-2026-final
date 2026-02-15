# Rasputin

## Problem Statement

**Challenge:** Rasputin  
**Points:** 100  
**Category:** Forensics/Steganography

## SOULUTION

1. Examined the memory dump file to find multiple process dumps
2. Discovered an XOR key "key42" in notepad.exe process (PID 102)
3. Found encrypted flag in secret_app.exe process (PID 103)
4. XOR decrypted the flag using the discovered key
5. Retrieved the flag successfully

### Vulnerability Analysis

Analyzing the memory dump, we can identify several key pieces of information:

1. **PID 101** (browser.exe): Contains random browser data - likely a decoy
2. **PID 102** (notepad.exe): **Contains `xor_key:key42`** - This is our encryption key!
3. **PID 103** (secret_app.exe): **Contains `encrypted_flag:`** - This is our target!
4. **PID 104** (systemsvc.exe): Contains log data - another decoy
