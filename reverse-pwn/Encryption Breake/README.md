# 8-Bit Encryption Breaker

**Category:** Reverse Engineering / Cryptography  
**Points:** 350  
**Description:** A retro arcade machine uses a custom 8-bit encryption to protect its high score save files. Find the encryption key and decrypt the hidden flag.

## The Challenge Explained

This challenge involves breaking a **rotating XOR cipher** - a simple but clever encryption method:

### How the Encryption Works

1. **XOR Cipher**: Each character is XORed with a key byte
2. **Rotating Key**: The key changes for each position using the formula:

   ```
   key_at_position[i] = (base_key[i % key_length] + i) % 256
   ```

3. **Base64 Encoding**: The encrypted bytes are then encoded in Base64

### What We're Given

The website provides:

- **Known plaintext-ciphertext pairs** (high scores):
  - `PLAYER1:999999` → `AgoXDBYFemFjYWVpWWY=`
  - `GAMER2:888888` → `FQcbEAFlcWNiYGRoWA==`
  - `PRO3:777777` → `AhQZZmlgfGxtb2s=`

- **Encrypted flag**: `ERUVZ2UsczkzLAM1DjwvGCURDQ0IBQcIFB86HTFeQFZADg==`

### The Solution Strategy

**Step 1: Known-Plaintext Attack**
Since we know both the plaintext (`PLAYER1:999999`) and its ciphertext, we can:

- XOR them together to get the key stream
- Example: `'P' XOR 0x02 = 0x52 ('R')`

**Step 2: Extract the Base Key**
The key stream shows a pattern because of the rotation formula. By testing different key lengths (3, 4, 5, etc.) and reversing the rotation formula, we find:

- **Base key**: `RETRO` (5 characters - fitting the arcade theme!)

**Step 3: Decrypt the Flag**
Using the key "RETRO", decrypt the encrypted flag to get the answer.

## Solution

Run the solve script:

```bash
python solve.py
```

The script will:

1. Extract the encryption key from the known plaintext-ciphertext pair
2. Verify the key is correct
3. Key Concepts

### XOR Cipher Weakness

XOR ciphers are vulnerable to known-plaintext attacks because:

- `plaintext XOR key = ciphertext`
- Therefore: `plaintext XOR ciphertext = key`

### Rotating Key Pattern

The key rotation adds complexity but doesn't prevent the attack:

- Once we have the key stream, we can reverse the rotation formula
- Testing different key lengths reveals which one produces a consistent base keyt key lengths systematically helped identify the 5-character base key
- **XOR cipher properties**: The bidirectional property of XOR (`A ⊕ B = C → A ⊕ C = B`) is fundamental to cryptanalysis
- **Position-based key rotation**: Understanding that `key[i] = (base_key[i % len] + i) % 256` allowed reversing the algorithm to extract the base key

### Mistakes Made

- **Initial approach**: I first tried automated tools like `ciphey` which didn't work because this was a custom cipher
- **Overthinking**: Initially I tried to brute-force different XOR keys before realizing the known-plaintext pair was intentionally provided
- **Pattern analysis**: Spent time analyzing the encrypted strings before utilizing the most valuable resource - the known plaintext

### Future Improvements

- Study more complex key rotation schemes (e.g., Vigenère cipher with offset)
- Practice frequency analysis techniques for unknown-plaintext scenarios
- Learn about stream ciphers and their cryptanalytic techniques
- Explore side-channel attacks on encryption implementations

## Key Takeaways

- **Known-plaintext attacks** are powerful against XOR ciphers
- **Key rotation** doesn't protect weak encryption if the base key is short
- **Pattern analysis** helps identify the correct key length
- Always look for known plaintext-ciphertext pairs in challenges

## Tags

`crypto` `xor-cipher` `known-plaintext-attack` `rotating-key` `base64` `reverse-engineering`
