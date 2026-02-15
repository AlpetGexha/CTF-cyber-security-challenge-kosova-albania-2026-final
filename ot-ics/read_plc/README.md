# read_plc

**Category:** OT-ICS
**Points:** 200  
**Challenge Description:**

## Challenge Description

The goal of this challenge was to connect to a Siemens PLC and read sensitive data (the flag) from one of its internal databases (Data Blocks).

## Solution

### 1. Protocol Identification

The challenge specifies a Siemens PLC. Siemens PLCs typically communicate using the **S7 Protocol** over **ISO-on-TCP (RFC 1006)** on port 102. In this challenge, the service was mapped to port **10023**.

### 2. Connection Handshake

To communicate with the PLC, a two-step handshake is required:

- **COTP (Connection-Oriented Transport Protocol)**: Establishing a connection to a specific Rack/Slot (TSAP). In this case, the standard **Rack 0, Slot 2** (TSAP `01 02`) was accepted.
- **S7 Setup Communication**: Negotiating PDU lengths and permissions. While some setups timed out, the PLC allowed direct "Job" requests (ROSCTR 0x01) after the COTP phase.

### 3. Data Extraction

The flag was discovered by scanning for **Data Blocks (DB)**.

- **DB 1** was found to contain the flag string.
- Reading 100 bytes from DB 1 starting at offset 0 revealed the full flag hash.

## Flag

`CSC26{ee36d402b65c98b7fffc4b337ab934ff149086f66a0ed01cf4d6fa231abe5ef1}`

## Scripts

- **`s7_final.py`**: A standalone Python implementation of the S7 read request used to bypass the need for external libraries like `snap7`. It manually constructs the TPKT, COTP, and S7 headers.
- **`s7_brute_force.py`**: A utility script created to scan multiple TSAPs and DB ranges to locate the data.

---

_Solved by Antigravity_
