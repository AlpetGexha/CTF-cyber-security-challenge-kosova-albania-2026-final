"""
SecureChat/SecureVault CTF Challenge - Flag Decryption Script
Decrypts the flag using extracted AES credentials from the APK
"""

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def decrypt_flag():
    """Decrypt the flag using AES-CBC with extracted credentials"""
    
    # Encryption credentials extracted from strings.xml (Base64 decoded)
    key = b"SecureVaultKey20"  # 16 bytes
    iv = b"InitVectorForAes"   # 16 bytes
    
    # Encrypted flag bytes extracted from DatabaseHelper.smali
    encrypted_bytes = [
        0x5e, 0x87, 0x06, 0x61, 0xe5, 0xec, 0x9b, 0xb9,
        0x4a, 0x50, 0xfb, 0xe1, 0x6d, 0x35, 0xce, 0x64,
        0xca, 0x5d, 0xdc, 0x68, 0x20, 0x96, 0x31, 0x70,
        0x25, 0x2c, 0x51, 0x31, 0x51, 0xa5, 0x75, 0x97,
        0x35, 0x34, 0xae, 0xed, 0x2d, 0xe7, 0xb8, 0x66,
        0x01, 0x2b, 0xdb, 0x25, 0x13, 0xa1, 0x6a, 0x3b
    ]
    
    # Convert list to bytes
    encrypted_data = bytes(encrypted_bytes)

    # Create AES cipher in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    # Decrypt the data
    decrypted = cipher.decrypt(encrypted_data)
    
    # Remove PKCS5 padding
    flag = unpad(decrypted, AES.block_size)
    
    # Print the flag
    print(flag.decode('ascii'))
    
    return flag.decode('ascii')


if __name__ == "__main__":
    try:
        decrypt_flag()
    except Exception as e:
        print(f"[-] Error: {e}")
        print("[!] Make sure pycryptodome is installed: pip install pycryptodome")
