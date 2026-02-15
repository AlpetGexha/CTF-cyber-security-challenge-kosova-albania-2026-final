
import requests
import time
import sys
import re

base_url = "https://asdfghjklzxcvbn-csc26.cybersecuritychallenge.al"
parts = {}
required_parts = 7 # Just a guess based on analyze.py logic
# But wait, analyze.py says "Flag part 1 of 7". Let's assume 7.

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

print(f"Initial Stats: {session.get(f'{base_url}/stats').text}")

found_count = 0
max_attempts = 1000

for i in range(max_attempts):
    try:
        response = session.get(f"{base_url}/data")
        if response.status_code == 200:
            d = response.json()
            # Check hint
            if 'hint' in d:
                hint = d['hint']
                # Try to extract "Flag part X: '...'"
                # Regex for "Flag part (\d+): '([^']+)'"
                match = re.search(r"Flag part (\d+): '([^']+)'", hint)
                if match:
                    p_num = int(match.group(1))
                    p_val = match.group(2)
                    if p_num not in parts:
                        parts[p_num] = p_val
                        found_count += 1
                        print(f"[{i}] Found Part {p_num}: {p_val}")
                        if found_count >= required_parts:
                            break
            # Check flag_part directly just in case
            if 'flag_part' in d:
                print(f"[{i}] Found flag_part field: {d['flag_part']}")
                
        else:
            print(f"[{i}] Error: {response.status_code}")
            
    except Exception as e:
        print(f"[{i}] Error: {e}")
        time.sleep(1)

print("\nCollected Parts:")
flag = ""
for k in sorted(parts.keys()):
    print(f"Part {k}: {parts[k]}")
    flag += parts[k]

print(f"\nFinal Flag: {flag}")
