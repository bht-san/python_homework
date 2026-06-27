"""Comprehensive automated test of core logic — no GUI required."""

from question_engine import QuestionEngine, Question
from practice_session import PracticeSession
from file_generator import FileGenerator
from constants import MODE_TIMED, MODE_FIXED
import tempfile, os, time, sys

errors = []

def check(condition, msg):
    if not condition:
        errors.append(f"FAIL: {msg}")
        print(f"  FAIL: {msg}")
    else:
        print(f"  PASS: {msg}")

# =====================================================================
print("=" * 60)
print("TEST 1: QuestionEngine — operation correctness")
print("=" * 60)

config = {
    "operations": ["+", "-", "x", "÷"],
    "addsub_min": 1, "addsub_max": 20,
    "mul_min": 1, "mul_max": 9,
    "div_min": 1, "div_max": 9,
}
engine = QuestionEngine(config)

for i in range(100):
    q = engine.generate_one()
    if q.operator == "÷":
        check(q.operand_b != 0, f"Division by zero: {q.display_text}")
        check(q.operand_a % q.operand_b == 0, f"Non-int division: {q.display_text}")
        check(q.operand_a == q.operand_b * q.correct_answer, f"Wrong div: {q.display_text}")
    if q.operator == "-":
        check(q.operand_a >= q.operand_b, f"Negative sub: {q.display_text}")
        check(q.operand_a - q.operand_b == q.correct_answer, f"Wrong sub: {q.display_text}")
    if q.operator == "+":
        check(q.operand_a + q.operand_b == q.correct_answer, f"Wrong add: {q.display_text}")
    if q.operator == "x":
        check(q.operand_a * q.operand_b == q.correct_answer, f"Wrong mul: {q.display_text}")

print()
print("=" * 60)
print("TEST 2: QuestionEngine — batch generation")
print("=" * 60)

batch = engine.generate_batch(10, allow_duplicates=False)
check(len(batch) == 10, f"Batch size: {len(batch)}")
keys = [(q.operand_a, q.operand_b, q.operator) for q in batch]
check(len(keys) == len(set(keys)), "No duplicates in unique batch")

batch2 = engine.generate_batch(20, allow_duplicates=True)
check(len(batch2) == 20, f"Batch with dupes size: {len(batch2)}")

print()
print("=" * 60)
print("TEST 3: PracticeSession — fixed mode, all correct")
print("=" * 60)

questions = engine.generate_batch(5)
session = PracticeSession(questions, mode=MODE_FIXED, question_count=5)
session.start()
for i in range(5):
    q = session.current_question
    check(q is not None, f"Question {i+1} exists")
    is_correct, ca = session.submit_answer(q.correct_answer)
    check(is_correct, f"Q{i+1} correct")
    check(ca is None, "No answer returned when correct")
    session.advance()

check(session.is_complete, "Session complete")
correct, wrong, unanswered = session.score
check(correct == 5 and wrong == 0, f"Score: {correct}/{wrong}/{unanswered}")
check(session.accuracy == 1.0, f"Accuracy: {session.accuracy}")

print()
print("=" * 60)
print("TEST 4: PracticeSession — with wrong answers")
print("=" * 60)

questions2 = engine.generate_batch(5)
session2 = PracticeSession(questions2, mode=MODE_FIXED, question_count=5)
session2.start()
# Q1: answer wrong
q = session2.current_question
is_correct, ca = session2.submit_answer(q.correct_answer + 999)
check(not is_correct, "Wrong answer detected")
check(ca == q.correct_answer, f"Correct answer returned: {ca}")
session2.advance()
# Q2-Q5: correct
for i in range(4):
    q = session2.current_question
    session2.submit_answer(q.correct_answer)
    session2.advance()

correct, wrong, unanswered = session2.score
check(correct == 4 and wrong == 1, f"Score: {correct}c/{wrong}w/{unanswered}u")
wrong_qs = session2.get_wrong_questions()
check(len(wrong_qs) == 1, f"Wrong records: {len(wrong_qs)}")

print()
print("=" * 60)
print("TEST 5: PracticeSession — timed mode")
print("=" * 60)

big_batch = engine.generate_batch(50)
session3 = PracticeSession(big_batch, mode=MODE_TIMED, time_limit=2)
session3.start()
for i in range(3):
    q = session3.current_question
    if q:
        session3.submit_answer(q.correct_answer)
        session3.advance()
check(not session3.is_complete, "Not complete before timeout")
time.sleep(2.1)
check(session3.check_timed_expiry(), "Timed expiry detected")
check(session3.is_complete, "Session complete after timeout")

print()
print("=" * 60)
print("TEST 6: FileGenerator — TXT and CSV")
print("=" * 60)

engine2 = QuestionEngine({
    "operations": ["+", "-", "x", "÷"],
    "addsub_min": 1, "addsub_max": 10,
    "mul_min": 1, "mul_max": 6,
    "div_min": 1, "div_max": 6,
})
qs = engine2.generate_batch(8)

# TXT
tmp_txt = os.path.join(tempfile.gettempdir(), "test_qmzy.txt")
FileGenerator.generate_txt(qs, tmp_txt, None)
check(os.path.exists(tmp_txt), "TXT file created")
with open(tmp_txt, "r", encoding="utf-8") as f:
    txt_content = f.read()
check("小学生算术练习题" in txt_content, "TXT title (Chinese)")
check("______" in txt_content, "TXT has blanks")
os.unlink(tmp_txt)

# CSV
tmp_csv = os.path.join(tempfile.gettempdir(), "test_qmzy.csv")
FileGenerator.generate_csv(qs, tmp_csv, include_answers=True)
check(os.path.exists(tmp_csv), "CSV file created")
with open(tmp_csv, "r", encoding="utf-8-sig") as f:
    csv_content = f.read()
check("正确答案" in csv_content, "CSV has answer column (Chinese)")
os.unlink(tmp_csv)

print()
print("=" * 60)
print("TEST 7: Edge cases")
print("=" * 60)

# Single operation
e1 = QuestionEngine({**config, "operations": ["÷"]})
q = e1.generate_one()
check(q.operator == "÷", "Single op (division)")

# Subtraction-only
e2 = QuestionEngine({**config, "operations": ["-"]})
for _ in range(20):
    q = e2.generate_one()
    check(q.operand_a >= q.operand_b, "No negative subtraction")

# Large ranges
e3 = QuestionEngine({
    "operations": ["+", "x"],
    "addsub_min": 50, "addsub_max": 100,
    "mul_min": 10, "mul_max": 20,
    "div_min": 1, "div_max": 9,
})
qs = e3.generate_batch(10)
for q in qs:
    if q.operator == "+":
        check(50 <= q.operand_a <= 100, f"Add 'a' in range: {q.operand_a}")
        check(50 <= q.operand_b <= 100, f"Add 'b' in range: {q.operand_b}")
    if q.operator == "x":
        check(10 <= q.operand_a <= 20, f"Mul 'a' in range: {q.operand_a}")

# mark_finished()
session4 = PracticeSession(engine.generate_batch(5), mode=MODE_FIXED, question_count=5)
session4.start()
check(not session4.is_complete, "Not complete initially")
session4.mark_finished()
check(session4.is_complete, "mark_finished() works")

# Empty operation list raises ValueError
try:
    QuestionEngine({**config, "operations": []})
    check(False, "Should have raised ValueError for empty ops")
except ValueError:
    check(True, "Empty operations raises ValueError")

# Progress tracking
session5 = PracticeSession(engine.generate_batch(10), mode=MODE_FIXED, question_count=10)
session5.start()
current, total = session5.progress
check(current == 1 and total == 10, f"Initial progress: {current}/{total}")
session5.submit_answer(session5.current_question.correct_answer)
session5.advance()
current, total = session5.progress
check(current == 2, f"Progress after 1 answer: {current}")

# =====================================================================
print()
print("=" * 60)
if errors:
    print(f"RESULTS: {len(errors)} FAILURES")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print("RESULTS: ALL TESTS PASSED")
print("=" * 60)
