# Data Corruption

**Category:** Cryptography  
**Points:** 250  
**Challenge Description:**

It looks like our message got scrambled during transmission! Fortunately, all the characters are still there just every group of three has been mixed up.

Flag: `CSC26{8797934c8157ae5b88a5985eb5c1d62051f7cb625b26ce0}`

## Analysis

The message is almost correct but clearly scrambled:

- Should start with `CSC26{` but shows `SCC6{2`
- The hex string appears jumbled
- Has a stray `0` at the end

The challenge hints that characters are shuffled in groups of 3.

## Solution

1. **Identified the pattern**: The first 12 characters (`"The flag is "`) are unscrambled. After that, every 3 characters are shuffled.

2. **Recognized the scrambling method**: Since the scrambling is deterministic, it likely uses Python's `random.shuffle()` with a fixed seed.

3. **Brute forced the seed**: Using the known flag format `CSC26{...}`, we tested different seeds until finding one that produces the correct permutation sequence.

4. **Found seed = 6**: This seed correctly unscrambles the message.

5. **Reversed the permutations**: For each 3-character chunk, we applied the inverse permutation to recover the original message.
