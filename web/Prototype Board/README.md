# Prototype Board

**Category:** Web Exploitation
**Points:** 1000
**Description** The bulletin board is online but locked down. User accounts can only be registered from the internal servers, and the operators refuse to add anyone new. Still, users whisper that persistence and creativity can bend the system in ways its designers never intended.

**Available endpoints:**

- `/` - Home page
- `/register` - User registration (restricted to localhost:9937)
- `/login` - User login
- `/blogs` - Blog listing
- `/blog/[id]` - Individual blog posts
- `/support` - Support ticket submission
- `/profile` - User profile page
- `/admin` - Admin console (requires privileges)

## Solution

### Step 1: Initial Reconnaissance

Explored the application and discovered:

- Registration is restricted to `localhost:9937` only
- Support page at `/support` accepts links that a bot will visit
- Blog posts hint at prototype pollution vulnerabilities
- Application built with Express.js/Node.js

### Step 2: Finding XSS Vulnerability

Tested the `/register?error=` parameter and found it reflects input without sanitization. This XSS vulnerability can be exploited through the support bot.

### Step 3: Bypassing Registration Restriction

Created an XSS payload that registers a user when the support bot visits it:

- Crafted a malicious URL: `/register?error=<script>fetch('/register', {method:'POST', ...})</script>`
- Submitted this URL through the support form
- The bot, running from `localhost:9937`, executed the XSS and registered the user
- Successfully logged in with the new credentials

### Step 4: Finding Profile Update Endpoint

After logging in, discovered the `/profile/update` endpoint accepts JSON payloads for updating user profiles.

### Step 5: Exploiting Prototype Pollution

Tested prototype pollution vectors:

- `__proto__` was blocked (403 Forbidden)
- `constructor.prototype` was NOT blocked ✅
- Sending payload: `{"constructor": {"prototype": {"isAdmin": true}}}`
- This polluted the prototype chain, giving all objects an `isAdmin` property

### Step 6: Accessing Admin Panel

With the polluted prototype granting admin privileges, accessed `/admin` and retrieved the flag.

🚩 **Flag:** `CSC26{f64358b882ac20b8fd75fee5120e3b95963162ee3ef616fde58b5dd70dc9ce23}`
