"""
8-Bit Encryption Breaker - Solution Script
Performs known-plaintext attack on rotating XOR cipher
"""

import base64

def extract_key(plaintext, ciphertext_b64):
    """
    Extract base key using known-plaintext attack.
    
    Args:
        plaintext: Known plaintext string
        ciphertext_b64: Corresponding Base64-encoded ciphertext
    
    Returns:
        Base key (bytes)
    """
    ciphertext = base64.b64decode(ciphertext_b64)
    
    # Extract key stream by XORing plaintext with ciphertext
    key_stream = []
    for i in range(len(plaintext)):
        key_byte = ord(plaintext[i]) ^ ciphertext[i]
        key_stream.append(key_byte)
    
    print("[*] Extracted key stream:")
    for i, byte in enumerate(key_stream):
        print(f"    Position {i:2d}: 0x{byte:02x} ('{chr(byte) if 32 <= byte < 127 else '?'}')")
    
    # Try different key lengths to find the base key
    print("\n[*] Testing different key lengths...")
    for key_len in range(3, 10):
        base_key = []
        consistent = True
        
        for pos in range(key_len):
            # Extract base key value for this position
            base_values = set()
            for i in range(pos, len(key_stream), key_len):
                # Reverse rotation: base = (stream - position) % 256
                base_value = (key_stream[i] - i) % 256
                base_values.add(base_value)
            
            # All positions should yield same base value
            if len(base_values) == 1:
                base_key.append(base_values.pop())
            else:
                consistent = False
                break
        
        if consistent and len(base_key) == key_len:
            key_str = bytes(base_key).decode('ascii', errors='ignore')
            print(f"    Length {key_len}: {key_str} ✓")
            return bytes(base_key)
        else:
            print(f"    Length {key_len}: Inconsistent")
    
    return None

def decrypt_rotating_xor(ciphertext_b64, base_key):
    """
    Decrypt data encrypted with rotating XOR cipher.
    
    Encryption formula: ciphertext[i] = plaintext[i] XOR (base_key[i % len] + i) % 256
    
    Args:
        ciphertext_b64: Base64-encoded ciphertext
        base_key: Base key (bytes)
    
    Returns:
        Decrypted plaintext string
    """
    ciphertext = base64.b64decode(ciphertext_b64)
    plaintext = []
    
    for i, byte in enumerate(ciphertext):
        # Calculate rotating key: (base_key[i % len] + position) % 256
        key_byte = (base_key[i % len(base_key)] + i) % 256
        plain_byte = byte ^ key_byte
        plaintext.append(plain_byte)
    
    return bytes(plaintext).decode('utf-8', errors='ignore')

def main():
    print("=" * 60)
    print("8-Bit Encryption Breaker - Known-Plaintext Attack")
    print("=" * 60)
    
    # Known plaintext-ciphertext pair from the website
    known_plaintext = "PLAYER1:999999"
    known_ciphertext = "AgoXDBYFemFjYWVpWWY="
    
    print(f"\n[+] Known plaintext: {known_plaintext}")
    print(f"[+] Known ciphertext: {known_ciphertext}")
    
    # Extract the base key
    print("\n" + "=" * 60)
    print("STEP 1: Extracting Encryption Key")
    print("=" * 60)
    base_key = extract_key(known_plaintext, known_ciphertext)
    
    if not base_key:
        print("[-] Failed to extract key!")
        return
    
    print(f"\n[+] Base key found: {base_key.decode('ascii')}")
    print(f"[+] Key (hex): {base_key.hex()}")
    
    # Verify the key
    print("\n" + "=" * 60)
    print("STEP 2: Verifying Key")
    print("=" * 60)
    test_encrypted = bytes([
        ord(known_plaintext[i]) ^ ((base_key[i % len(base_key)] + i) % 256)
        for i in range(len(known_plaintext))
    ])
    test_b64 = base64.b64encode(test_encrypted).decode()
    
    print(f"Original:  {known_ciphertext}")
    print(f"Generated: {test_b64}")
    
    if test_b64 == known_ciphertext:
        print("\n[+] ✓✓✓ KEY VERIFIED! ✓✓✓")
    else:
        print("\n[-] Key verification failed!")
        return
    
    # Decrypt the flag
    print("\n" + "=" * 60)
    print("STEP 3: Decrypting the Flag")
    print("=" * 60)
    encrypted_flag = "ERUVZ2UsczkzLAM1DjwvGCURDQ0IBQcIFB86HTFeQFZADg=="
    
    print(f"[+] Encrypted flag: {encrypted_flag}")
    decrypted_flag = decrypt_rotating_xor(encrypted_flag, base_key)
    
    print(f"\n[+] Decrypted flag: {decrypted_flag}")
    
    # Test with other known ciphertexts
    print("\n" + "=" * 60)
    print("BONUS: Decrypting Other Entries")
    print("=" * 60)
    
    other_entries = [
        ("GAMER2:888888", "FQcbEAFlcWNiYGRoWA=="),
        ("PRO3:777777", "AhQZZmlgfGxtb2s=")
    ]
    
    for expected, ciphertext in other_entries:
        decrypted = decrypt_rotating_xor(ciphertext, base_key)
        match = "✓" if decrypted == expected else "✗"
        print(f"{match} {ciphertext} -> {decrypted}")
    
    print("\n" + "=" * 60)
    print(f"Submit the key '{base_key.decode('ascii')}' to the website to get the actual flag!")
    print("=" * 60)

if __name__ == "__main__":
    main()
