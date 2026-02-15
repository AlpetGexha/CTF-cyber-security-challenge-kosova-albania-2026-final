import random

def solve():
    with open('message.txt', 'r') as f:
        content = f.read().strip()

    prefix = content[:12]
    scrambled = content[12:]
    
    # Use Seed 6 which was found to work with cumulative permutation state
    random.seed(6)
    
    decrypted_full = ""
    chunks = [scrambled[i:i+3] for i in range(0, len(scrambled), 3)]
    
    # Initialize permutation state ONCE
    p = [0, 1, 2]
    
    for chunk in chunks:
        # Update permutation cumulatively
        random.shuffle(p)
        
        orig = [''] * 3
        chunk_list = list(chunk)

        for j in range(3):
            orig[p[j]] = chunk_list[j]
        
        decrypted_full += "".join(orig)
            
    final_msg = prefix + decrypted_full
    
    print(final_msg)
    
if __name__ == "__main__":
    solve()
