import requests
import sys

def main():
    # RSA Parameters
    n = 3233
    e = 65537

    print(f"[*] Target Parameters: n={n}, e={e}")
    print("[*] Attempting to factor n (since it's small)...")

    # Factor n
    p = 0
    q = 0
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            p = i
            q = n // i
            # Confirm p, q are prime?
            # 53, 61 are prime.
            break
    
    if p == 0:
        print("[-] Failed to factor n")
        sys.exit(1)
        
    print(f"[+] Factors found: p={p}, q={q}")

    # Calculate phi(n)
    phi = (p - 1) * (q - 1)
    print(f"[*] phi(n) = {phi}")

    # Calculate private key d
    def mod_inverse(a, m):
        m0 = m
        y = 0
        x = 1
        if m == 1: return 0
        while a > 1:
            q = a // m
            t = m
            m = a % m
            a = t
            t = y
            y = x - q * y
            x = t
        if x < 0: x += m0
        return x

    d = mod_inverse(e, phi)
    print(f"[+] Recovered Private Key (d): {d}")

    

if __name__ == "__main__":
    main()
