# RSA "Timing Attack" Challenge Writeup

**Category:** Cryptography / Scripting
**Points:**: 800
**Description**
The challenge presents a retro-themed terminal interface that claims to be vulnerable to a "Timing Side-Channel Attack". It provides the RSA parameters and allows users to decrypt messages and verify a recovered private key.

## Analysis

The challenge provides the following RSA parameters:

- **Modulus (N):** 3233
- **Public Exponent (e):** 65537

While the challenge title and description suggest a complex timing attack, a quick check of the modulus size reveals the true vulnerability: **The modulus is extremely small.**

In RSA, the security relies on the difficulty of factoring the modulus $N$ into its prime factors $p$ and $q$. Standard RSA implementations use moduli with 2048 or 4096 bits. A modulus of 3233 is only ~12 bits, which is trivial to factor even with pen and paper, let alone a computer.

Therefore, we can ignore the timing attack vector and simply break the encryption mathematically.

## Solution

### Step 1: Factor the Modulus

We need to find two prime numbers $p$ and $q$ such that $p \times q = N = 3233$.
Since $\sqrt{3233} \approx 56.8$, we only need to check primes up to 56.

Testing small primes:

- $3233 \div 53 = 61$

So, $p = 53$ and $q = 61$.

### Step 2: Calculate Euler's Totient Function $\phi(n)$

$$ \phi(n) = (p-1) \times (q-1) $$
$$ \phi(3233) = (53-1) \times (61-1) $$
$$ \phi(3233) = 52 \times 60 = 3120 $$

### Step 3: Calculate the Private Key (d)

The private key $d$ is the modular multiplicative inverse of $e$ modulo $\phi(n)$.
$$ d \equiv e^{-1} \pmod{\phi(n)} $$
$$ d \equiv 65537^{-1} \pmod{3120} $$

Since $65537 \pmod{3120} = 17$, we are looking for the inverse of 17 modulo 3120.
$$ 17 \times d \equiv 1 \pmod{3120} $$

Using the Extended Euclidean Algorithm or a simple script:
$$ d = 2753 $$

Verification:
$$ (17 \times 2753) \pmod{3120} = 46801 \pmod{3120} = 1 $$

### Step 4: Retrieve the Flag

We submit the recovered private key ($d=2753$) to the challenge server's verification endpoint.

**Recovered Flag:**
`CSC26{eb3c633260dbe45e82d91eeedf12056a}`
