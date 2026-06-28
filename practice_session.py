"""Practice session state machine — timing, scoring, question sequencing."""

import time
from typing import Optional

from question_engine import Question
from constants import MODE_TIMED, MODE_FIXED


class PracticeSession:
    """Manages a single practice session.

    Args:
        questions: Pre-generated list of Question objects.
        mode: "timed" or "fixed".
        time_limit: Time limit in seconds (for timed mode).
        question_count: Number of questions (for fixed mode).
    """

    def __init__(
        self,
        questions: list[Question],
        mode: str,
        time_limit: int = 0,
        question_count: int = 0,
    ):
        self.questions = questions
        self.mode = mode
        self.time_limit = time_limit      # seconds
        self.question_count = question_count or len(questions)

        # Ensure we don't go past available questions in fixed mode
        if mode == MODE_FIXED:
            self.active_questions = questions[:self.question_count]
        else:
            self.active_questions = questions

        self._start_time: Optional[float] = None
        self._current_index: int = 0
        self._correct_count: int = 0
        self._wrong_records: list[dict] = []
        self._answers: list[Optional[int]] = []
        self._finished: bool = False

    # ── Public API ──

    def start(self) -> None:
        """Start the session timer."""
        self._start_time = time.monotonic()
        self._current_index = 0
        self._correct_count = 0
        self._wrong_records = []
        self._answers = [None] * len(self.active_questions)
        self._finished = False

    @property
    def current_question(self) -> Optional[Question]:
        """Return the current question, or None if session is complete."""
        if self._finished or self._current_index >= len(self.active_questions):
            return None
        return self.active_questions[self._current_index]

    @property
    def current_index(self) -> int:
        """1-based index of the current question."""
        return self._current_index + 1

    @property
    def total_questions(self) -> int:
        """Total number of questions in this session."""
        return len(self.active_questions)

    def submit_answer(self, answer: int) -> tuple[bool, Optional[int]]:
        """Check the user's answer against the current question.

        Returns:
            (is_correct, correct_answer_if_wrong) — correct_answer is None when correct.
        """
        if self._finished or self._current_index >= len(self.active_questions):
            return False, None

        q = self.active_questions[self._current_index]
        self._answers[self._current_index] = answer

        if answer == q.correct_answer:
            self._correct_count += 1
            return True, None
        else:
            self._wrong_records.append({
                "index": self._current_index + 1,
                "question": q.display_text,
                "user_answer": answer,
                "correct_answer": q.correct_answer,
            })
            return False, q.correct_answer

    def advance(self) -> Optional[Question]:
        """Move to the next question. Returns the new current question or None."""
        self._current_index += 1
        # Check completion
        if self.mode == MODE_FIXED:
            if self._current_index >= len(self.active_questions):
                self._finished = True
                return None
        return self.current_question

    def check_timed_expiry(self) -> bool:
        """Check if time has run out in timed mode. Returns True if session should end."""
        if self.mode != MODE_TIMED or self._finished:
            return False
        if self.elapsed_seconds >= self.time_limit:
            self._finished = True
            return True
        return False

    # ── Time / Progress ──

    @property
    def elapsed_seconds(self) -> int:
        """Elapsed time in seconds since start()."""
        if self._start_time is None:
            return 0
        return max(0, int(time.monotonic() - self._start_time))

    @property
    def remaining_seconds(self) -> int:
        """Remaining time in seconds (timed mode only)."""
        if self.mode != MODE_TIMED:
            return 0
        return max(0, self.time_limit - self.elapsed_seconds)

    @property
    def is_complete(self) -> bool:
        """Whether the session has finished (pure check, no side effects)."""
        if self._finished:
            return True
        if self.mode == MODE_TIMED and self.elapsed_seconds >= self.time_limit:
            return True
        if self._current_index >= len(self.active_questions):
            return True
        return False

    def mark_finished(self) -> None:
        """Explicitly mark the session as finished (e.g., user quit early)."""
        self._finished = True

    @property
    def progress(self) -> tuple[int, int]:
        """(current_index, total_questions)."""
        return (self._current_index + 1, len(self.active_questions))

    # ── Results ──

    @property
    def score(self) -> tuple[int, int, int]:
        """Returns (correct_count, wrong_count, unanswered_count)."""
        answered = self._current_index
        wrong = answered - self._correct_count
        total = len(self.active_questions)
        unanswered = total - answered
        return self._correct_count, wrong, max(0, unanswered)

    @property
    def accuracy(self) -> float:
        """Accuracy as a fraction 0.0–1.0."""
        answered = self._current_index
        if answered == 0:
            return 0.0
        return self._correct_count / answered

    def get_wrong_questions(self) -> list[dict]:
        """Return records of incorrectly answered questions."""
        return list(self._wrong_records)

    def get_all_results(self) -> list[dict]:
        """Return per-question results for detailed review."""
        results = []
        for i, q in enumerate(self.active_questions[:self._current_index]):
            user_ans = self._answers[i]
            results.append({
                "index": i + 1,
                "question": q.display_text,
                "user_answer": user_ans,
                "correct_answer": q.correct_answer,
                "is_correct": user_ans == q.correct_answer,
            })
        return results
