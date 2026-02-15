# Industrial Espionage

**Points: 400**  
**Category:** OT/ICS  
**Hint:** You are a cybersecurity consultant hired to assess the security of an industrial facility. Your mission is to discover all PLCs in the network, assess their security configurations, and extract sensitive production data to compile a complete intelligence report.

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

## Key Takeaway

When dealing with HIGH security systems in CTF challenges, look beyond obvious patterns. The challenge name and context often contain crucial hints. In this case, "Espionage" + leet speak + PLC naming convention = the password.
