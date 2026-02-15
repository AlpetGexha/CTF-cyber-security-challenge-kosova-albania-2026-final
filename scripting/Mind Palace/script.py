import requests
import json
import re
import time

BASE_URL = "https://lkjhgfdsaqwertyu-csc26.cybersecuritychallenge.al"

session = requests.Session()

history = {}
flag_parts = {}
TOTAL_PARTS = 5
MAX_REQUESTS = 1000

def answer_question(question_data):
    qid = question_data["question_id"]
    q_type = question_data.get("question_type", "")
    target_id = question_data.get("target_request_id")
    
    answer = None
    if target_id and target_id in history:
        answer = history[target_id].get(q_type, "")
    if not answer and "correct_answer" in question_data:
        answer = question_data["correct_answer"]
    if not answer:
        return None
    
    r = session.get(f"{BASE_URL}/answer", params={"question_id": qid, "answer": answer})
    try:
        result = r.json()
        # Print full answer response to see everything
        if any(k in result for k in ["flag_part", "special_data", "flag", "bonus"]):
            print(f"  [ANSWER-SPECIAL] {json.dumps(result)}")
        return result
    except:
        return None

print(f"=== Mind Palace Solver v3 ===\n")

r = session.get(f"{BASE_URL}/stats")
print(f"Stats: {json.dumps(r.json(), indent=2)}\n")

for i in range(MAX_REQUESTS):
    try:
        r = session.get(f"{BASE_URL}/data")
        if r.status_code != 200:
            continue
        try:
            data = r.json()
        except:
            continue
        
        req_id = data.get("request_id")
        if req_id:
            history[req_id] = data
        
        # Print EVERY response that has special_data, hint, flag_part, or any flag-like field
        if "special_data" in data:
            print(f"[{i}] SPECIAL_DATA: {data['special_data']}")
            # Extract flag part - be very careful with regex
            m = re.search(r"Flag part (\d+):\s*'([^']*)'", data['special_data'])
            if m:
                pnum, pval = int(m.group(1)), m.group(2)
                if pnum not in flag_parts:
                    flag_parts[pnum] = pval
                    print(f"  >>> PART {pnum}: '{pval}' <<<")
        
        if "hint" in data:
            print(f"[{i}] HINT: {data['hint']}")
            m = re.search(r"Flag part (\d+):\s*'([^']*)'", data['hint'])
            if m:
                pnum, pval = int(m.group(1)), m.group(2)
                if pnum not in flag_parts:
                    flag_parts[pnum] = pval
                    print(f"  >>> PART {pnum}: '{pval}' <<<")
        
        if "flag_part" in data:
            print(f"[{i}] FLAG_PART: {data['flag_part']}")
        
        if "flag" in data:
            print(f"[{i}] FLAG: {data['flag']}")
        
        # Handle memory questions
        if "memory_question" in data:
            result = answer_question(data["memory_question"])
            if result:
                # Check answer result for flag info
                for key in ["special_data", "hint", "flag_part", "flag", "bonus", "message"]:
                    if key in result:
                        val = str(result[key])
                        if "flag" in val.lower() or "part" in val.lower():
                            print(f"  [ANSWER {key}]: {val}")
                        m = re.search(r"Flag part (\d+):\s*'([^']*)'", val)
                        if m:
                            pnum, pval = int(m.group(1)), m.group(2)
                            if pnum not in flag_parts:
                                flag_parts[pnum] = pval
                                print(f"  >>> PART {pnum} (from answer): '{pval}' <<<")
        
        if (i + 1) % 100 == 0:
            print(f"\n[PROGRESS {i+1}] history={len(history)} | parts={dict(sorted(flag_parts.items()))}\n")
        
        if len(flag_parts) >= TOTAL_PARTS:
            print(f"\n*** ALL {TOTAL_PARTS} PARTS FOUND ***")
            break
            
    except Exception as e:
        print(f"[{i}] Error: {e}")
        time.sleep(0.5)

print(f"\n=== FINAL FLAG ===")
for k in sorted(flag_parts.keys()):
    print(f"  Part {k}: '{flag_parts[k]}'")

assembled = "".join(flag_parts[k] for k in sorted(flag_parts.keys()))
print(f"\nAssembled: {assembled}")

# Stats
r = session.get(f"{BASE_URL}/stats")
print(f"\nFinal stats: {json.dumps(r.json(), indent=2)}")
