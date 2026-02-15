# ACME Vault

**Category:** forensics-stegano  
**Points:** 300  
**Challenge Description:**

You’re a DFIR investigator tasked with analyzing a drive seized from a suspect. The drive appears to have a hidden partition containing sensitive data.

## Solution

### How I Solved It

#### 1. Initial Disk Analysis

First, I examined the disk image file structure and analyzed the disk layout:

```bash
cd /home/ylbaa/vault
file acme_corporation_disk.dd
ls -lh acme_corporation_disk.dd
```

This revealed:

- File type: `DOS/MBR boot sector`
- Size: `512 MiB`
- Contains a partition table with one visible partition

#### 2. Partition Table Examination

I used `fdisk` to analyze the partition layout:

```bash
fdisk -l acme_corporation_disk.dd
```

Output revealed:

```
Disk acme_corporation_disk.dd: 512 MiB, 536870912 bytes, 1048576 sectors
Units: sectors of 1 * 512 = 512 bytes

Device                    Boot Start    End Sectors  Size Id Type
acme_corporation_disk.dd1       2048 821247  819200  400M  c W95 FAT32 (LBA)
```

**Key Finding:** The visible partition ends at sector 821247, but the disk has 1048576 total sectors. This means **227,328 sectors (~111 MiB) of unallocated space** exists after the visible partition!

#### 3. Hidden Partition Discovery

I examined the unallocated space starting at sector 821248:

```bash
dd if=acme_corporation_disk.dd bs=512 skip=821248 count=16 2>/dev/null | od -A x -t x1z | head -80
```

The output showed a FAT32 boot sector signature:

```
000000 eb 58 90 6d 6b 66 73 2e 66 61 74 00 02 01 20 00  >.X.mkfs.fat... .<
...
0001f0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 55 aa  >..............U.<
```

The `55 aa` signature and FAT32 structure confirms a **hidden partition** exists in this unallocated space!

#### 4. Partition Extraction

I extracted both partitions to separate images for analysis:

```bash
# Extract visible partition (starts at sector 2048, 819200 sectors)
dd if=acme_corporation_disk.dd bs=512 skip=2048 count=819200 of=/tmp/visible_part.img

# Extract hidden partition (starts at sector 821248, remaining sectors)
dd if=acme_corporation_disk.dd bs=512 skip=821248 of=/tmp/hidden_part.img
```

#### 5. FAT32 Filesystem Parsing

Since mounting required sudo privileges, I wrote a Python script to parse the FAT32 filesystem structure directly:

```python
import struct

def read_fat32_info(img_path):
    with open(img_path, 'rb') as f:
        # Read Boot Parameter Block (BPB)
        boot = f.read(512)
        bytes_per_sector = struct.unpack_from('<H', boot, 11)[0]
        sectors_per_cluster = struct.unpack_from('<B', boot, 13)[0]
        reserved_sectors = struct.unpack_from('<H', boot, 14)[0]
        num_fats = struct.unpack_from('<B', boot, 16)[0]
        fat_size = struct.unpack_from('<I', boot, 36)[0]
        root_cluster = struct.unpack_from('<I', boot, 44)[0]

        # Calculate data region offset
        cluster_size = bytes_per_sector * sectors_per_cluster
        data_start = (reserved_sectors + num_fats * fat_size) * bytes_per_sector
        root_offset = data_start + (root_cluster - 2) * cluster_size

        # Parse directory entries...
```

**Files discovered on the visible partition:**

- `very_important.txt` (14 bytes, Cluster 3)
- `notes.txt` (35 bytes, Cluster 4)

**Files discovered on the hidden partition:**

- `secret.enc` (96 bytes, Cluster 3) ← **Encrypted file!**

#### 6. File Extraction

I extended the Python script to extract files by reading their clusters:

```python
def extract_file(img_path, cluster_num, file_size, output_path):
    with open(img_path, 'rb') as f:
        # Parse FAT32 parameters
        boot = f.read(512)
        bytes_per_sector = struct.unpack_from('<H', boot, 11)[0]
        sectors_per_cluster = struct.unpack_from('<B', boot, 13)[0]
        reserved_sectors = struct.unpack_from('<H', boot, 14)[0]
        num_fats = struct.unpack_from('<B', boot, 16)[0]
        fat_size = struct.unpack_from('<I', boot, 36)[0]

        cluster_size = bytes_per_sector * sectors_per_cluster
        data_start = (reserved_sectors + num_fats * fat_size) * bytes_per_sector

        # Calculate file offset and read data
        offset = data_start + (cluster_num - 2) * cluster_size
        f.seek(offset)
        data = f.read(file_size)

        with open(output_path, 'wb') as out:
            out.write(data)
        return data

# Extract all files
extract_file('/tmp/visible_part.img', 3, 14, '/tmp/very_important.txt')
extract_file('/tmp/visible_part.img', 4, 35, '/tmp/notes.txt')
extract_file('/tmp/hidden_part.img', 3, 96, '/tmp/secret.enc')
```

#### 7. Discovered Files Analysis

**very_important.txt:**

```
You are here!
```

Just a decoy message.

**notes.txt:**

```
AES_KEY: Z@gnoxXxs3cr3tP@ssw0rd123
```

**Critical finding:** This contains the AES encryption key!

**secret.enc (hex dump):**

```
53616c7465645f5f2df98822051d3f7c31537e32538d2696f672809a7fdda98b...
```

The file starts with `53 61 6c 74 65 64 5f 5f` which decodes to **"Salted\_\_"** - this is the signature for OpenSSL's `enc` command output format!

#### 8. Decryption and Flag Extraction

Using the key from `notes.txt`, I decrypted the file with OpenSSL:

```bash
openssl enc -aes-256-cbc -d -in /tmp/secret.enc -pass pass:'Z@gnoxXxs3cr3tP@ssw0rd123' -pbkdf2
```

**Result:** `CSC26{9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08}`

### Flag

```
CSC26{9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08}
```

### Verification

You can verify this solution by following these steps:

```bash
# 1. Analyze the disk image
fdisk -l acme_corporation_disk.dd

# 2. Check for hidden partition in unallocated space
dd if=acme_corporation_disk.dd bs=512 skip=821248 count=1 2>/dev/null | od -A x -t x1z | head -3
# Look for: eb 58 90 6d 6b 66 73 2e 66 61 74 (FAT32 boot signature)

# 3. Extract the hidden partition
dd if=acme_corporation_disk.dd bs=512 skip=821248 of=/tmp/hidden_part.img 2>&1

# 4. Search for the encryption key on the visible partition
dd if=acme_corporation_disk.dd bs=512 skip=2048 count=819200 2>/dev/null | strings | grep -i "AES_KEY"
# Output: AES_KEY: Z@gnoxXxs3cr3tP@ssw0rd123

# 5. Mount and extract secret.enc (requires appropriate tools or Python script)
# Then decrypt:
openssl enc -aes-256-cbc -d -in secret.enc -pass pass:'Z@gnoxXxs3cr3tP@ssw0rd123' -pbkdf2
```

Or use a quick one-liner to search for "CSC26" after decryption:

```bash
# Extract hidden partition and try decryption
dd if=acme_corporation_disk.dd bs=512 skip=821248 2>/dev/null | \
  dd bs=512 skip=3530 count=1 2>/dev/null | \
  openssl enc -aes-256-cbc -d -pass pass:'Z@gnoxXxs3cr3tP@ssw0rd123' -pbkdf2 2>/dev/null
```
