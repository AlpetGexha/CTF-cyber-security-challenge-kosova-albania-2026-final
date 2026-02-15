def solve():
    # Read the memory dump file
    with open('rasputin.mem', 'rb') as f:
        content = f.read()
        
    start_marker = b'encrypted_flag:'
    start_pos = content.find(start_marker) + len(start_marker)

    end_marker = b'\n--'
    end_pos = content.find(end_marker, start_pos)
    encrypted_data = content[start_pos:end_pos]

    xor_key = b'key42'

    # XOR decrypt
    decrypted = []
    for i, byte in enumerate(encrypted_data):
        key_byte = xor_key[i % len(xor_key)]
        decrypted_byte = byte ^ key_byte
        decrypted.append(decrypted_byte)

    # Convert to string
    flag = bytes(decrypted).decode('utf-8', errors='ignore').strip()
    
    print(f"{flag}")
    return flag

if __name__ == "__main__":
    print("=" * 60)
    print("Rasputin Challenge - Memory Forensics XOR Decryption")
    print("=" * 60)
    print()
    
    try:
        flag = solve()
    except Exception as e:
        print(f"\n Error: {e}")
        import traceback
        traceback.print_exc()
