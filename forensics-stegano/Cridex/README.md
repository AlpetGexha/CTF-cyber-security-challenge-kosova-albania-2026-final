# Cridex

**Category:** Cryptography  
**Points:** 400
**Challenge Description:**

_Memory forensics challenge analyzing Cridex malware using Volatility_

## Challenge Description

Cridex malware has infected a Windows host. Use Volatility to investigate the compromised system and find the full path of comctl32.dll.

**Flag Format:** `CSC26{full_path_here}`

## Solution

### Step 1: Identify Memory Profile

```bash
python2 vol.py -f cridex.vmem imageinfo
```

**Result:** Profile is WinXPSP2x86 (Windows XP SP2)

### Step 2: List Processes

```bash
python2 vol.py -f cridex.vmem --profile=WinXPSP2x86 pslist
```

**Finding:** Suspicious process `reader_sl.exe` (PID 228) with unreadable PEB (indicator of malware).

### Step 3: Analyze Virtual Address Descriptors

Since the PEB couldn't be read, use VAD to examine memory regions:

```bash
python2 vol.py -f cridex.vmem --profile=WinXPSP2x86 vadinfo -p 228
```

**Key Finding:** The malware loaded comctl32.dll from the WinSxS directory:

```
\Device\HarddiskVolume1\WINDOWS\WinSxS\x86_Microsoft.Windows.Common-Controls_6595b64144ccf1df_6.0.2600.2180_x-ww_a84f1ff9\comctl32.dll
```

### Step 4: Format the Flag

Convert the device path to DOS format (C:\ instead of \Device\HarddiskVolume1\):

**Flag:** `CSC26{C:\WINDOWS\WinSxS\x86_Microsoft.Windows.Common-Controls_6595b64144ccf1df_6.0.2600.2180_x-ww_a84f1ff9\comctl32.dll}`

## Key Commands

```bash
# Identify OS profile
python2 vol.py -f cridex.vmem imageinfo

# List processes
python2 vol.py -f cridex.vmem --profile=WinXPSP2x86 pslist

# Analyze Virtual Address Descriptors for a process
python2 vol.py -f cridex.vmem --profile=WinXPSP2x86 vadinfo -p <PID>
```

## Tools Used

- **Volatility 2** - Memory forensics framework
- **Linux terminal** - Command execution

## Notes

- Windows XP uses WinSxS (Side-by-Side) for DLL versioning
- The malware hid by making its PEB unreadable
- VAD analysis reveals mapped files when standard methods fail

---

**Flag:** `CSC26{C:\WINDOWS\WinSxS\x86_Microsoft.Windows.Common-Controls_6595b64144ccf1df_6.0.2600.2180_x-ww_a84f1ff9\comctl32.dll}`
