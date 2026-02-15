# Assembly Line Debugger

**500 Points**  
**Description:**
A corrupted game ROM has been discovered from a classic arcade machine. The binary contains a bug that prevents access to the secret level. Your task is to analyze the assembly code, identify the bug, and patch it.

## Overview

| Item       | Value                                   |
| ---------- | --------------------------------------- |
| Platform   | CTF Challenge                           |
| Event      | CTF - Final                             |
| Category   | Reverse Engineering & PWN               |
| Difficulty | ★★☆☆☆                                   |
| Date       | 2026-02-13                              |
| Flag       | `CSC26{assembly_debugging_master_2024}` |

## Problem Statement

> **Assembly Line Debugger**
>
> A corrupted game ROM has been discovered from a classic arcade machine. The binary contains a bug that prevents access to the secret level. Your task is to analyze the assembly code, identify the bug, and patch it.

**Files Provided:**

- `corrupted_rom.exe` - PE32+ executable (console) x86-64, for MS Windows
- `challange` - Challenge description text file

## TL;DR

- Analyze a Windows PE executable with a hidden flag encrypted in the `.data` section
- The binary checks for an 8-character password starting with "ASM\_" to unlock the secret level
- Instead of brute-forcing the password, extract the encrypted data and decrypt it using the hardcoded XOR key (0x04)
- The `decrypt_secret` function reveals the flag by XORing encrypted bytes with the key
- Flag obtained through static analysis without needing to run or patch the binary

## Background Knowledge

### PE Executable Format

PE (Portable Executable) is the file format for executables, DLLs, and other binaries on Windows systems. It contains several sections:

- **.text** - Contains the executable code
- **.data** - Contains initialized global and static variables
- **.rdata** - Contains read-only data like string literals
- **.bss** - Contains uninitialized data

### x86-64 Assembly Basics

Key concepts used in this challenge:

1. **Registers**: `%rax`, `%rbp`, `%rsp`, `%rcx`, `%rdx` are 64-bit general-purpose registers
2. **Stack Operations**: `push` and `pop` for saving/restoring values
3. **Comparison**: `cmp` compares two values, followed by conditional jumps like `je` (jump if equal)
4. **XOR Encryption**: Simple cipher where `plaintext ^ key = ciphertext` and `ciphertext ^ key = plaintext`

### Objdump and Binary Analysis Tools

- **objdump**: Displays information about object files, can disassemble machine code into assembly
- **strings**: Extracts printable strings from binary files
- **nm**: Lists symbols from object files
- **file**: Determines file type

## Solution

### Step 1: Initial Reconnaissance

First, let's examine what files we have and their types:

```bash
cd "/home/kali/Desktop/CTF - Final/Reverse engineering & pwn/Assembly Line Debugger"
ls -la
```

```
challange
corrupted_rom.exe
```

Check the file types:

```bash
file challange corrupted_rom.exe
```

```
challange:         ASCII text
corrupted_rom.exe: PE32+ executable (console) x86-64, for MS Windows, 19 sections
```

Read the challenge description:

```bash
cat challange
```

```
Assembly Line Debugger

A corrupted game ROM has been discovered from a classic arcade machine. The binary contains a bug that prevents access to the secret level. Your task is to analyze the assembly code, identify the bug, and patch it.
```

Now let's search for interesting strings in the binary:

```bash
strings corrupted_rom.exe | grep -iE "flag|secret|level|ctf"
```

```
Access granted! Secret: %s
Your task: Patch the binary to reveal the secret level.
=== SECRET LEVEL UNLOCKED ===
Flag: %s
The binary needs to be patched to work correctly.
secret_data_encrypted
decrypt_secret
decrypted_secret
```

Great! We can see there's a `decrypt_secret` function and `secret_data_encrypted` data.

### Step 2: Analyzing the Binary Structure

Let's find the relevant functions using `nm`:

```bash
nm corrupted_rom.exe 2>/dev/null | grep -E "main|decrypt|secret"
```

```
0000000140001591 T decrypt_secret
00000001400016b8 T main
0000000140008020 D secret_data_encrypted
```

Now let's disassemble the `decrypt_secret` function to understand how it works:

```bash
objdump -d corrupted_rom.exe 2>/dev/null | grep -A 50 "decrypt_secret"
```

The key part of the `decrypt_secret` function:

```asm
0000000140001591 <decrypt_secret>:
   140001591:   push   %rbp
   140001592:   mov    %rsp,%rbp
   140001595:   sub    $0x10,%rsp
   140001599:   mov    %rcx,0x10(%rbp)
   14000159d:   movb   $0x4,-0x5(%rbp)        # XOR key = 0x04
   1400015a1:   movl   $0x0,-0x4(%rbp)        # counter = 0
   1400015a8:   jmp    1400015d0
   1400015aa:   mov    -0x4(%rbp),%eax        # load counter
   1400015ad:   cltq
   1400015af:   lea    0x6a6a(%rip),%rdx      # load address of secret_data_encrypted
   1400015b6:   movzbl (%rax,%rdx,1),%eax    # load encrypted byte
   1400015ba:   mov    -0x4(%rbp),%edx
   1400015bd:   movslq %edx,%rcx
   1400015c0:   mov    0x10(%rbp),%rdx
   1400015c4:   add    %rcx,%rdx
   1400015c7:   xor    -0x5(%rbp),%al         # XOR with 0x04
   1400015ca:   mov    %al,(%rdx)             # store decrypted byte
   1400015cc:   addl   $0x1,-0x4(%rbp)        # counter++
   1400015d0:   cmpl   $0x24,-0x4(%rbp)       # compare counter with 0x24 (36 decimal)
   1400015d4:   jle    1400015aa              # loop if counter <= 36
```

**Key observations:**

1. The function XORs each byte with `0x04`
2. It processes 37 bytes (0 to 36, or 0x24 in hex)
3. The encrypted data is at address `0x140008020` (based on the lea instruction offset)

### Step 3: Extracting and Decrypting the Secret

Let's extract the encrypted data from the `.data` section:

```bash
objdump -s -j .data corrupted_rom.exe 2>/dev/null | head -10
```

```
Contents of section .data:
 140008000 0a000000 00000000 00000000 00000000  ................
 140008010 00000000 00000000 00000000 00000000  ................
 140008020 47574736 327f6577 77616966 687d5b60  GWG62.ewwaifh}[`
 140008030 61667163 636d6a63 5b696577 7061765b  afqccmjc[iewpav[
 140008040 36343630 79000000 00000000 00000000  6460y...........
```

The encrypted data starts at `0x140008020`:

```
47 57 47 36 32 7f 65 77 77 61 69 66 68 7d 5b 60
61 66 71 63 63 6d 6a 63 5b 69 65 77 70 61 76 5b
36 34 36 30 79
```

Now let's decrypt it using Python:

```python
# The decrypt_secret function XORs each byte with 0x04
encrypted_hex = "47574736327f657777616966687d5b6061667163636d6a635b69657770617656343630679"
encrypted_hex = "47574736327f657777616966687d5b6061667163636d6a635b696577706176563434363079"

# Convert to bytes
encrypted = bytes.fromhex(encrypted_hex)

# XOR key
xor_key = 0x04

# Decrypt
decrypted = ""
for byte in encrypted:
    decrypted += chr(byte ^ xor_key)

print(f"Decrypted: {decrypted}")
```

Output:

```
Decrypted: CSC26{assembly_debugging_master_2024}
```

### Step 4: Understanding the Complete Flow

Let's also look at the `main` function to understand the intended solution:

```asm
00000001400016b8 <main>:
   1400016f9:   cmpl   $0x2,0x10(%rbp)    # Check if argc == 2
   1400016fd:   je     140001731           # Jump if argc == 2
   ...
   140001731:   # Code that calls corrupted_function
   140001778:   call   1400015e8 <corrupted_function>
   ...
```

The `corrupted_function` checks for a password:

- Length must be 8 characters
- First character: 0x41 = 'A'
- Second character: 0x53 = 'S'
- Third character: 0x4d = 'M'
- Fourth character: 0x5f = '\_'

So the password starts with "ASM\_" and needs 4 more characters. However, we don't need to find the full password because we can directly decrypt the flag using the hardcoded XOR key!

### Step 5: Capturing the Flag

The flag is successfully decrypted through static analysis:

```
CSC26{assembly_debugging_master_2024}
```

## Alternative Solution: Finding the Password

If we wanted to patch the binary and run it with the correct password, we would need to determine the last 4 characters. Looking at the theme (assembly debugging), common possibilities would be:

- `ASM_D3BG` (ASM DEBUG)
- `ASM_2024`
- `ASM_BUG1`
- `ASM_FIX1`

However, since we can decrypt the flag directly through static analysis, finding the exact password is unnecessary for this challenge.

## Tools Used

| Tool      | Purpose                                 |
| --------- | --------------------------------------- |
| `file`    | Identify file types                     |
| `strings` | Extract printable strings from binaries |
| `nm`      | List symbols from object files          |
| `objdump` | Disassemble binary and display sections |
| `python3` | Script the XOR decryption algorithm     |

## Lessons Learned

### What I Learned

1. **Static Analysis is Powerful**: Sometimes you don't need to run or patch a binary to extract the flag. Static analysis alone can reveal hardcoded secrets.

2. **Understanding XOR Encryption**: XOR with a constant key is symmetric - the same operation both encrypts and decrypts. This makes it easy to reverse if the key is known.

3. **Reading x86-64 Assembly**: Practice reading assembly code helps identify:
   - Loop structures (counter initialization, increment, comparison, conditional jump)
   - Encryption operations (XOR, shift operations)
   - Memory addresses and data locations

4. **PE Binary Structure**: Understanding how Windows executables organize code (.text) and data (.data) sections helps locate encrypted information.

### Mistakes Made

1. **Initial Wine Attempt**: First tried to run the Windows binary with Wine (which wasn't installed) before realizing static analysis would be sufficient.

2. **Overthinking the Password**: Spent time analyzing the password validation logic when we could simply extract and decrypt the data directly.

### Future Improvements

1. **Learn Binary Patching**: Practice using tools like `radare2` or `Ghidra` to patch binaries and change program flow.

2. **Automate Extraction**: Write scripts to automatically extract and decrypt data from binaries based on detected encryption patterns.

3. **Dynamic Analysis Skills**: Learn to use debuggers like `gdb` or `x64dbg` to step through execution and observe runtime behavior.

## References

- [x86-64 Assembly Reference](https://www.cs.virginia.edu/~evans/cs216/guides/x86.html) - Instruction set reference
- [PE Format Documentation](https://docs.microsoft.com/en-us/windows/win32/debug/pe-format) - Microsoft's PE format specification
- [Objdump Manual](https://man7.org/linux/man-pages/man1/objdump.1.html) - GNU binutils documentation
- [XOR Encryption](https://en.wikipedia.org/wiki/XOR_cipher) - Understanding XOR ciphers

## Tags

`reverse-engineering` `x86-64` `assembly` `static-analysis` `xor-encryption` `pe-binary` `objdump` `binary-analysis` `decryption`
