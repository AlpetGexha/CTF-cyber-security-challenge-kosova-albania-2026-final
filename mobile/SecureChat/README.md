# SecureChat

**Points Unknown**  
**Hint:** A military-grade communication platform that claims to provide end-to-end encryption for secure conversations. Extract the hidden flag.

## Solution

### How I Solved It

#### 1. Analyzed the APK Structure

The challenge provided `SecureChat.apk`, an Android application file. Initial inspection revealed:

- **Package:** `com.securechat`
- **Main Activity:** `com.securechat.MainActivity`
- **Version:** 2.0
- **Files:** `classes.dex`, `classes2.dex`, `resources.arsc`, `AndroidManifest.xml`

#### 2. Extracted String Resources

Using `androguard` to parse the APK and extract string resources:

```bash
python -m pip install androguard
```

```python
from loguru import logger
logger.remove()
from androguard.core.apk import APK

apk = APK('SecureChat.apk')
package = apk.get_package()
strings = apk.get_android_resources().get_string_resources(package)
print(strings)
```

**Output:**

```xml
<string name="encrypted_flag_part">Q1NDMjZ7c2VjdXJlX2NoYXQ=</string>
<string name="remote_server_url">http://192.168.0.227:8000</string>
<string name="api_endpoint">/config</string>
```

The resource named `encrypted_flag_part` contained a Base64-encoded value.

#### 3. Decoded the Flag Fragment

```bash
echo "Q1NDMjZ7c2VjdXJlX2NoYXQ=" | base64 -d
```

**Output:**

```
CSC26{secure_chat
```

#### 4. Investigated Network Logic

Decompiled `MainActivity$NetworkTask` using androguard to understand the app's behavior:

```python
from androguard.misc import AnalyzeAPK
apk, d, dx = AnalyzeAPK('SecureChat.apk')
```

The app attempts to contact a remote server that was **unreachable** during analysis (connection timeout).

#### 5. Result

⚠️ **Incomplete Flag Extracted**

The Base64-decoded resource gives only: **`CSC26{secure_chat`**

**Missing:** Closing brace `}` and potentially additional characters

**Analysis:** The remote server endpoint (`http://192.168.0.227:8000/config`) was unreachable and likely contains the remaining flag portion or validation logic.

### Flag (Partial)

```
CSC26{secure_chat
```

### Extraction Script

```python
import base64
from androguard.core.apk import APK

# Parse APK
apk = APK('SecureChat.apk')
package = apk.get_package()
strings = apk.get_android_resources().get_string_resources(package)

# Decode Base64 flag part
encrypted_part = "Q1NDMjZ7c2VjdXJlX2NoYXQ="
flag_fragment = base64.b64decode(encrypted_part).decode()

print(f"Flag (incomplete): {flag_fragment}")
```

**Flag found (incomplete):** `CSC26{secure_chat`
