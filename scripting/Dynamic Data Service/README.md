# Dynamic Data Service

**Points:** 400  
**Category:** Scripting  
**URL:** <https://asdfghjklzxcvbn-csc26.cybersecuritychallenge.al/>

## Challenge Description

A web service that provides dynamic data that changes on every request.

**Available Endpoints:**

- `/data` - Get current dynamic data
- `/history` - View data history (last 10 entries)
- `/stats` - Service statistics

## Solution

### Analysis

The service returns random JSON data with each request to the `/data` endpoint:

```json
{
  "data_type": "alpha",
  "hash": "45be2310",
  "hint": "Flag part 1 of 7",
  "pattern": "C",
  "random_number": 7282,
  "random_string": "xcjxkSMNGA0ryM7P",
  "request_id": 8,
  "sequence": 8,
  "special_data": "Flag part 1: 'CSC26{'",
  "timestamp": "2026-02-13T09:22:25.225568"
}
```

**Key observations:**

- Flag is split into 7 parts revealed randomly
- `hint` field shows "Flag part X of 7"
- `special_data` field contains the actual flag fragment
- Each flag part appears sporadically across hundreds of requests

### Strategy

1. Make repeated requests to `/data` endpoint
2. Extract flag parts from `special_data` field using regex
3. Continue until all 7 parts are collected
4. Assemble parts in order to construct the complete flag

### Flag Parts

Running the script collects all 7 parts:

```
Part 1: CSC26{
Part 2: scr1pt1ng
Part 3: _m4st3r
Part 4: _2026
Part 5: _1337
Part 6: _h4ck3r
Part 7: }
```

### Flag

```
CSC26{scr1pt1ng_m4st3r_2026_1337_h4ck3r}
```
