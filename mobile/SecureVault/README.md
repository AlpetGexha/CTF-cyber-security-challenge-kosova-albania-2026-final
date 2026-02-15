# SecureVault - Mobile Security CTF Challenge

**Challenge Name:** SecureVault  
**Category:** Mobile Security / Reverse Engineering  
**Points:** 400  
**Difficulty:** Medium

## Challenge Description

You've discovered a suspicious banking application called "Secure Vault" that claims to provide military-grade encryption for storing sensitive financial data. The app appears to be used by high-profile clients, and there are rumors that it contains hidden vulnerabilities.

**Objective:** Analyze the APK and find the hidden flag.

## Solution

### Overview

This challenge involves reverse engineering an Android APK to discover a critical cryptographic vulnerability. The application stores encrypted data but exposes its encryption keys in the application resources, allowing attackers to decrypt sensitive information.

### Tools Required

- `apktool` - APK decompilation tool
- Python 3 with `pycryptodome` library
- Basic understanding of Android application structure
- Knowledge of AES encryption

### Step-by-Step Solution

#### 1. Initial Analysis

First, verify the file type:

```bash
file SecureVault.apk
# Output: Android package (APK), with gradle app-metadata.properties, with APK Signing Block
```

#### 2. Decompile the APK

Use apktool to decompile the APK into smali code and resources:

```bash
apktool d SecureVault.apk -o SecureVault_decoded
```

This extracts:

- `smali/` - Decompiled Java bytecode (smali format)
- `res/` - Application resources
- `AndroidManifest.xml` - Application manifest

#### 3. Identify Key Components

Explore the application package structure:

```bash
find SecureVault_decoded -path "*/com/securevault/*.smali" -type f
```

Key files discovered:

- `MainActivity.smali` - Main application entry point
- `CryptoUtils.smali` - Encryption/decryption utilities
- `DatabaseHelper.smali` - Database operations
- `VaultManager.smali` - Vault management logic

#### 4. Analyze CryptoUtils.smali

Examining `CryptoUtils.smali` reveals critical information:

```smali
.field private static final ALGORITHM:Ljava/lang/String; = "AES"
.field private static final TRANSFORMATION:Ljava/lang/String; = "AES/CBC/PKCS5Padding"
```

The code references encryption keys from string resources:

```smali
sget v3, Lcom/securevault/R$string;->hidden_key:I
invoke-virtual {p1, v3}, Landroid/content/Context;->getString(I)Ljava/lang/String;

sget v4, Lcom/securevault/R$string;->hidden_iv:I
invoke-virtual {p1, v4}, Landroid/content/Context;->getString(I)Ljava/lang/String;
```

**Vulnerability Found:** Encryption keys are stored in `strings.xml`!

#### 5. Extract Encryption Credentials

Check `res/values/strings.xml`:

```bash
grep -E "hidden_key|hidden_iv" SecureVault_decoded/res/values/strings.xml
```

Output:

```xml
<string name="hidden_iv">SW5pdFZlY3RvckZvckFlcw==</string>
<string name="hidden_key">U2VjdXJlVmF1bHRLZXkyMA==</string>
```

Decode the Base64 values:

```bash
echo "U2VjdXJlVmF1bHRLZXkyMA==" | base64 -d
# Output: SecureVaultKey20

echo "SW5pdFZlY3RvckZvckFlcw==" | base64 -d
# Output: InitVectorForAes
```

**Encryption Parameters:**

- Algorithm: AES-128-CBC
- Key: `SecureVaultKey20` (16 bytes)
- IV: `InitVectorForAes` (16 bytes)
- Padding: PKCS5

#### 6. Find Encrypted Flag Data

Analyze `DatabaseHelper.smali` to find the encrypted flag:

```smali
.line 60
const/16 v3, 0x30
new-array v3, v3, [I
fill-array-data v3, :array_0

.line 63
.local v3, "encryptedFlagBytes":[I
```

The array contains 48 bytes (0x30 in hex) of encrypted data. Find the array definition:

```smali
:array_0
.array-data 4
    0x5e
    0x87
    0x6
    0x61
    0xe5
    0xec
    0x9b
    0xb9
    # ... (48 bytes total)
.end array-data
```

## Flag

```
CSC26{s3cur3_v4ult_4ndr01d_r3v3rs3_3ng1n33r1ng}
```
