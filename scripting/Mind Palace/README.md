# Mind Palace

**Points: 600**  
**Category:** Scripting  
**Hint:** Welcome to the Mind Palace, where your memory is your greatest weapon!

**URL:** `https://lkjhgfdsaqwertyu-csc26.cybersecuritychallenge.al`

## Solution

### How I Solved It

#### 1. Initial Reconnaissance

I accessed the web interface through my browser to understand the challenge. The homepage revealed three endpoints:

- `/data` - Returns current data (may include memory questions)
- `/answer` - Submit answers to memory questions
- `/stats` - Service statistics

When visiting the `/data` endpoint in the browser, I received responses like:

```json
{
  "animal": "dog",
  "city": "Chicago",
  "color": "red",
  "data_type": "gamma",
  "hash": "88cd4f9a",
  "pattern": "D",
  "random_number": 1864,
  "random_string": "Xa6vjj3aO4hKt8s4",
  "request_id": 7904,
  "sequence": 4,
  "timestamp": "2026-02-13T13:05:59.269333"
}
```

#### 2. Understanding the Challenge Mechanism

By refreshing the `/data` endpoint multiple times in my browser, I identified several response types:

**Type 1: Regular Data**

```json
{
  "request_id": 13211,
  "sequence": 3,
  "data_type": "beta",
  "color": "purple",
  "city": "NYC",
  "animal": "cat",
  "pattern": "A",
  "hash": "32177f71",
  "random_number": 4563,
  "random_string": "kL2m9pQr",
  "timestamp": "2026-02-14T..."
}
```

**Type 2: Memory Questions**

```json
{
  "request_id": 13235,
  "question_id": 1891,
  "question": "What was the color in request 13211?",
  "correct_answer": "purple",
  "status": "success"
}
```

**Type 3: Flag Parts**

```json
{
  "request_id": 13237,
  "special_data": "Flag part 2 of 5: Flag part 2: 'm3m0ry_'"
}
```

**Type 4: HTTP 500 Errors** (occasional server errors to simulate unreliability)

#### 3. Analyzing the Memory System

The challenge tests **memory persistence** across HTTP requests:

1. Server returns data with unique `request_id` values
2. Later, server asks questions referencing **previous** `request_id` values
3. Must answer using data from the **correct historical request**
4. Correct answers unlock flag parts

**Example flow:**

```
Request #10  → request_id=13211, color="purple"
Request #25  → "What was the color in request 13211?"
Answer       → Submit "purple" to /answer?question_id=1891&answer=purple
Response     → Flag part revealed!
```

#### 4. Protocol Analysis

**Answer submission format:**

```
GET /answer?question_id=<ID>&answer=<VALUE>
```

**Successful response:**

```json
{
  "correct_answer": "purple",
  "message": "Correct answer!",
  "question": "What was the color in request 13211?",
  "status": "success"
}
```

**Failed response:**

```json
{
  "message": "Missing question_id or answer parameter",
  "status": "error"
}
```

#### 5. Challenge Requirements

To capture the flag, I needed to:

- **Store all data** from every `/data` request keyed by `request_id`
- **Parse memory questions** to identify which `request_id` and field are being asked about
- **Look up stored data** to find the correct answer
- **Submit answers** immediately to collect flag parts
- **Handle errors** (HTTP 500) gracefully and continue
- **Assemble flag parts** in the correct order (1-5)

#### 6. Manual Solution Process

I kept a text document open to track all the data I received. Each time I refreshed `/data` in the browser, I copied the JSON response and saved it with its `request_id`.

When I encountered a memory question, I would:

1. Note the `question_id` and the question text
2. Parse which `request_id` it was asking about
3. Look up that `request_id` in my saved data
4. Find the specific field value being asked about
5. Navigate to `/answer?question_id=<ID>&answer=<VALUE>` in the browser

**Example progression:**

```
[10/200] Fetching data...
  req_id=13211, type=beta, seq=3
[25/200] Fetching data...
  [QUESTION] ID:1891 - What was the color in request 13211?
  [ANSWER AVAILABLE] purple
  [SUBMIT] q_id=1891, answer=purple -> {"status": "success"}
[26/200] Fetching data...
  [FLAG] Flag part 2 of 5: 'm3m0ry_'
```

**Flag parts collected:**

```
Part 1: CSC26{
Part 2: m3m0ry_
Part 3: m45ter_
Part 4: 2026}
Part 5: (empty)
```

**Final output:**

```
=== FLAG RECONSTRUCTION ===
  Part 1: CSC26{
  Part 2: m3m0ry_
  Part 3: m45ter_
  Part 4: 2026}
  Part 5:

Reconstructed flag: CSC26{m3m0ry_m45ter_2026}
```

### Flag

```
CSC26{m3m0ry_m45ter_2026}
```
