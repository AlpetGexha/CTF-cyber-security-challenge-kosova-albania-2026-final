# Pandora Box

**Category:** Cryptography  
**Points:** 300  
**Challenge Description:**

They said Pandora’s Box was sealed forever, yet someone left a trace in the code. Can you find the secret hidden in it?

Reminder: The flag starts with CSC26{}

## Soulution

> THIS SOULUTION ITS MAKE BY GEMINI

Based on the visual clues in the image, here is the solution to the challenge.

The Decryption Logic
The secret is hidden using a simple shift cipher based on the combination lock dials.

Read the Code: Look at the row of characters printed directly below the dials.

Read the Key: Look at the numbers displayed on the middle row of each corresponding dial.

Decrypt: Subtract the dial number from the ASCII value of the character below it to reveal the true character.

Group,Character (Code),ASCII Value,Dial Number,Operation,Result ASCII,Result Char
1,S,83,3,83 - 3,80,P
,:,58,6,58 - 6,52,4
,v,118,8,118 - 8,110,n
,j,106,6,106 - 6,100,d
2,5,53,5,53 - 5,48,0
,t,116,2,116 - 2,114,r
,:,58,6,58 - 6,52,4
3,J,74,8,74 - 8,66,B
,1,49,1,49 - 1,48,0
,|,124,4,124 - 4,120,x
4,P,80,5,80 - 5,75,K
,4,52,1,52 - 1,51,3
,~,126,5,126 - 5,121,y

The Hidden Secret
The decoded string spells out: P4nd0r4B0xK3y
