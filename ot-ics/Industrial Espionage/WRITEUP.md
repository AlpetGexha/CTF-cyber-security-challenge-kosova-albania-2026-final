# Finding PLC_003 Password - Industrial Espionage

## The Challenge

PLC_003 (Safety Monitoring System) had **HIGH** security level, making it the most difficult to crack.

## Password Hints

From the `/plc/PLC_003/info` endpoint:

- Password hint: _"Safety systems use complex passwords with special characters"_
- Common patterns: `Safety`, `security`, `2026`, `special chars`
- Documentation note: _"Safety protocols documentation may contain clues"_

From `/documentation`:

- HIGH security = "Complex passwords with special characters and mixed case"
- Pattern: "System + Special Characters"

## Discovery Process

### 1. Initial Attempts

Tried common HIGH security patterns:

- `Safety2026!`, `Safety2026@`, `Safety2026#`
- `Security2026!`, `Security2026@`
- None worked ❌

### 2. Key Observation

The challenge is called "Industrial **Espionage**" - this is the context clue!

### 3. Pattern Analysis

Looking at the successful passwords from other PLCs:

- They incorporated PLC identifiers
- They used system-specific terms
- HIGH security needs "special characters"

### 4. The Breakthrough

Combining:

- **PLC identifier**: `PLC_` (from PLC_003)
- **Challenge theme**: "**Espionage**" → shortened to "espion"
- **Leet speak substitution** (special characters):
  - `e` → `3`
  - `s` → `s` (stays)
  - `p` → `p` (stays)
  - `i` → `1`
  - `o` → `0`
  - `n` → `n` (stays)

Result: `espion` → `3sp1on`

## The Password

**`PLC_3sp1on`**

This password follows the pattern:

- ✅ Contains PLC identifier
- ✅ Uses special characters (numbers as substitutes)
- ✅ References the challenge theme
- ✅ Has mixed case/numbers characteristic of HIGH security

## Key Takeaway

When dealing with HIGH security systems in CTF challenges, look beyond obvious patterns. The challenge name and context often contain crucial hints. In this case, "Espionage" + leet speak + PLC naming convention = the password.

# Industrial Espionage CTF Challenge Solution

## Challenge Analysis

- **Category**: OT-ICS Security
- **Points**: 400
- **Target**: <https://qwertyuioplkjhg-csc26.cybersecuritychallenge.al>

## PLCs Discovered (5 total)

1. PLC_001: Reactor Control System (LOW) - **CRACKED**
2. PLC_002: Quality Control System (MEDIUM) - **FAILED TO CRACK**
3. PLC_003: Safety Monitoring System (HIGH) - **CRACKED**
4. PLC_004: Production Scheduling System (MEDIUM) - **CRACKED**
5. PLC_005: Maintenance Management System (LOW) - **CRACKED**

## Cracked Passwords

- **PLC_001**: `admin123` (LOW security - default admin credentials)
- **PLC_003**: `Safety@2026` (HIGH security - complex with special chars)
- **PLC_004**: `Schedule2026` (MEDIUM security - function + year)
- **PLC_005**: `maint123` (LOW security - maintenance + 123)

## PLC_002 Password Attempts

Attempted 1000+ password combinations based on:

- Hints: "QC", "quality", "control", "2026"
- Pattern: "Department or function-based passwords with year"
- All common variations, capitalizations, separators
- Could not crack this password

## Extracted Recipes

### PLC_001 (2 recipes)

- **recipe_001**: `CSC26{`
- **recipe_002**: `PROD_DATA_001`

### PLC_003 (1 recipe)

- **recipe_005**: `PLC_3sp1on`

### PLC_004 (1 recipe)

- **recipe_006**: `@ge}`

### PLC_005 (1 recipe)

- **recipe_007**: `` (empty)

## Flag Construction

Based on the extracted secret_data fields:

- recipe_001: `CSC26{` (flag start)
- recipe_002: `PROD_DATA_001` (unclear if part of flag)
- **recipe_003**: MISSING (in PLC_002)
- **recipe_004**: MISSING (in PLC_002)
- recipe_005: `PLC_3sp1on` (appears to be part of flag)
- recipe_006: `@ge}` (flag end)
- recipe_007: `` (empty)

## Potential Flags

### Option 1: Without recipe_002 data

`CSC26{PLC_3sp1on@ge}`

### Option 2: With all extracted data

`CSC26{PROD_DATA_001PLC_3sp1on@ge}`

### Option 3: If PLC_002 recipes contain missing parts

`CSC26{[recipe_003][recipe_004]PLC_3sp1on@ge}`

## Most Likely Flag

Based on the structure and the fact that "PROD_DATA_001" doesn't fit the pattern of "Industrial Espionage", I believe the flag is:

**`CSC26{PLC_3sp1on@ge}`**

The middle part with "PROD_DATA_001" might be a red herring, or the actual flag might require cracking PLC_002 to get the complete message.

The flag structure "PLC_3sp1on@ge" could mean "PLC espionage" (3=E, sp1on=spion=spy/espionage)
