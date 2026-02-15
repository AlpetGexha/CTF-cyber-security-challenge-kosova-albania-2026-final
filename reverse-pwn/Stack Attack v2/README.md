# Stack Attack v2 - CTF Writeup

**Category:** Reverse Engineering & Binary Exploitation  
**Points:** 500
**Description** A vulnerable program with buffer overflow protection has been discovered. The challenge requires exploiting the binary to retrieve the flag despite active canary protection.

**Files Provided:**

- `stack_attack_v2` - 64-bit ELF executable

---

## Initial Reconnaissance

### File Analysis

```bash
file stack_attack_v2
stack_attack_v2: ELF 64-bit LSB executable, x86-64, version 1 (SYSV),
dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
for GNU/Linux 3.2.0, with debug_info, not stripped
```

### Security Protections

```bash
$ checksec --file=stack_attack_v2
[*] '/path/to/stack_attack_v2'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX unknown - GNU_STACK missing
    PIE:        No PIE (0x400000)
    Stack:      Executable
    RWX:        Has RWX segments
    Stripped:   No
    Debuginfo:  Yes
```

**Key Observations:**

- No PIE (fixed addresses)
- Stack is executable
- Binary is not stripped (symbols available)
- Despite "No canary found" message, the binary implements a custom canary

### Running the Binary

```bash
$ ./stack_attack_v2
=== RETRO BUFFER OVERFLOW CHALLENGE ===
A vulnerable program has been discovered.
Your task: Exploit the buffer overflow to get the flg.

Useful information:
- Buffer size: 64 bytes
- Canary protection: Active
- ASLR: Disabled for this challenge
- Stack executable: No

Enter your payload: test
Input received: test
Canary intact: CANARY1
Program completed normally.
```

The binary reveals it has a **custom canary implementation** using the value `CANARY1`.

---

## Reverse Engineering

### Function Discovery

Using `nm` to list symbols:

```bash
$ nm stack_attack_v2 | grep -E " T "
0000000000401459 T main
00000000004011b6 T process_prt1
0000000000401209 T process_prt2
00000000004013c6 T show_info
00000000004012c7 T vulnerable_function
000000000040125c T win_function
```

**Interesting functions:**

- `vulnerable_function()` - Likely contains the overflow
- `win_function()` - Probably prints the flag
- `process_prt1()` and `process_prt2()` - Flag processing functions

### Analyzing vulnerable_function()

Disassembling with objdump:

```assembly
vulnerable_function:
   ; Function prologue
   push   %rbp
   mov    %rsp,%rbp
   sub    $0x120,%rsp              ; Allocate 288 bytes on stack

   ; Initialize canary at rbp-0x8
   movabs $0x315952414e4143,%rax  ; "CANARY1" in hex
   mov    %rax,-0x8(%rbp)          ; Store canary

   ; Read input into buffer at rbp-0x120 (200 bytes max)
   lea    -0x120(%rbp),%rax
   mov    $0xc8,%esi               ; size = 200
   call   fgets@plt

   ; Strip newline
   call   strcspn@plt
   movb   $0x0,-0x120(%rbp,%rax,1)

   ; VULNERABLE: strcpy to smaller buffer!
   lea    -0x120(%rbp),%rdx        ; Source (input)
   lea    -0x50(%rbp),%rax         ; Dest (80 bytes from rbp)
   call   strcpy@plt

   ; Check canary
   lea    -0x8(%rbp),%rax
   lea    "CANARY1",%rdx
   call   strcmp@plt
   test   %eax,%eax
   je     canary_ok

   ; Canary check failed
   call   puts@plt                 ; "Stack smashing detected!"
   mov    $0x1,%edi
   call   exit@plt

canary_ok:
   ; Print buffer and canary, then return
   ...
   leave
   ret
```

**Stack Layout:**

```
+------------------+
| Return Address   | <- rbp+8
+------------------+
| Saved RBP        | <- rbp
+------------------+
| Canary (8 bytes) | <- rbp-0x8  ("CANARY1\x00")
+------------------+
| ...              |
+------------------+
| Dest Buffer      | <- rbp-0x50 (80 bytes available)
| (80 bytes)       |
+------------------+
| ...              |
+------------------+
| Input Buffer     | <- rbp-0x120 (288 bytes)
| (200 bytes max)  |
+------------------+
```

**Vulnerability:**
`strcpy()` copies from the large input buffer at `rbp-0x120` to the smaller destination buffer at `rbp-0x50`, allowing overflow to reach the canary, saved RBP, and return address.

### Analyzing win_function()

```assembly
win_function:
   push   %rbp
   mov    %rsp,%rbp
   sub    $0x60,%rsp

   ; Call process_prt1
   lea    -0x10(%rbp),%rax
   mov    %rax,%rdi
   call   process_prt1

   ; Call process_prt2
   lea    -0x18(%rbp),%rax
   mov    %rax,%rdi
   call   process_prt2

   ; Combine and print
   ...
   lea    "Access granted! flg: %s",%rax
   call   printf@plt
   call   exit@plt
```

The `win_function()` decrypts the flag using two helper functions and prints it.

### Analyzing process_prt1()

```assembly
process_prt1:
   movb   $0x4,-0x5(%rbp)          ; key = 0x04
   movl   $0x0,-0x4(%rbp)          ; i = 0

loop:
   cmp    $0xe,-0x4(%rbp)          ; while i <= 14
   jle    decrypt

decrypt:
   mov    -0x4(%rbp),%eax
   lea    flg_prt1,%rdx            ; Load encrypted data @ 0x404060
   movzbl (%rax,%rdx,1),%eax
   xor    -0x5(%rbp),%al           ; XOR with 0x04
   mov    %al,(%rdx)               ; Store decrypted byte
   addl   $0x1,-0x4(%rbp)          ; i++
```

**Algorithm:** XOR decryption with key `0x04` on 15 bytes at address `0x404060`

### Analyzing process_prt2()

Similar to `process_prt1()`:

- XOR decryption with key `0x04`
- Processes 7 bytes at address `0x404070`
- Adds null terminator

---

## Exploitation Attempts

### Attempt 1: Traditional Buffer Overflow

**Goal:** Overflow the buffer to overwrite the return address with `win_function()` address.

```python
payload = b"A" * 72         # Fill to canary
payload += b"CANARY1\x00"   # Preserve canary
payload += b"B" * 8         # Overwrite saved RBP
payload += p64(0x40125c)    # win_function address
```

**Result:** ❌ Failed

**Reason:** The `strcpy()` function terminates at the first null byte (`\x00`) it encounters. Since the canary is `"CANARY1\x00"`, `strcpy()` stops copying at byte 79, never reaching the return address at byte 88.

```
Payload: AAAA...AAAA (72) + CANARY1\x00 + BBBBBBBB + <addr>
                                      ^
                                      strcpy stops here!
```

### Attempt 2: Bypass Without Null Byte

```python
payload = b"A" * 72
payload += b"CANARY1"      # Without null byte
payload += b"B" * 9
payload += p64(0x40125c)
```

**Result:** ❌ Failed - "Stack smashing detected!"

**Reason:** The canary check uses `strcmp()` which expects `"CANARY1\x00"`. Without the null terminator, the canary check fails.

### The Catch-22

- **With `\x00` in payload:** `strcpy()` stops early, can't reach return address
- **Without `\x00` in payload:** Canary check fails, program exits

This is by design! The challenge prevents traditional exploitation.

---

## Solution: Static Flag Extraction

Since we can't exploit the binary dynamically, we extract and decrypt the flag directly from the binary's data section.

### Step 1: Locate Encrypted Flag Data

Using `nm` to find data symbols:

```bash
$ nm stack_attack_v2 | grep flg
0000000000404060 D flg_prt1
0000000000404070 D flg_prt2
```

### Step 2: Extract Encrypted Data

```python
from pwn import *

elf = ELF('./stack_attack_v2', checksec=False)

flg_prt1 = elf.read(0x404060, 15)  # 15 bytes
flg_prt2 = elf.read(0x404070, 7)   # 7 bytes

print("Encrypted part 1:", flg_prt1.hex())
print("Encrypted part 2:", flg_prt2.hex())
```

**Output:**

```
Encrypted part 1: 47574736327f67306a30767d5b356a
Encrypted part 2: 706567707904
```

### Step 3: Decrypt Using XOR

From our analysis, both parts use XOR encryption with key `0x04`:

```python
key = 0x04

# Decrypt part 1
decrypted1 = bytes([b ^ key for b in flg_prt1])
print("Part 1:", decrypted1)  # b'CSC26{c4n4ry_1n'

# Decrypt part 2
decrypted2 = bytes([b ^ key for b in flg_prt2])
print("Part 2:", decrypted2)  # b'tact}\x00\x00'

# Combine
flag = (decrypted1 + decrypted2).rstrip(b'\x00')
print("Flag:", flag.decode())
```

### Step 4: Get the Flag

**Flag:** `CSC26{c4n4ry_1ntact}`
