"""Question generation engine — pure logic, no UI dependency."""

import random
from dataclasses import dataclass

from constants import MAX_DIVIDEND, MAX_RETRY_DUPLICATE


@dataclass
class Question:
    """A single arithmetic question."""
    operand_a: int
    operand_b: int
    operator: str          # "+", "-", "x", "÷"
    correct_answer: int
    display_text: str      # e.g., "15 ÷ 3 = ?"


class QuestionEngine:
    """Generates arithmetic questions based on configuration.

    Configuration keys:
        operations: list[str]     — which operations to include ("+","-","x","÷")
        addsub_min: int
        addsub_max: int
        mul_min: int
        mul_max: int
        div_min: int
        div_max: int
    """

    def __init__(self, config: dict):
        self.operations = config["operations"]
        if not self.operations:
            raise ValueError("At least one operation must be selected.")

        self.addsub_min = config.get("addsub_min", 1)
        self.addsub_max = config.get("addsub_max", 20)
        self.mul_min = config.get("mul_min", 1)
        self.mul_max = config.get("mul_max", 9)
        self.div_min = config.get("div_min", 1)
        self.div_max = config.get("div_max", 9)

    def generate_one(self) -> Question:
        """Randomly select an operation and generate a valid question."""
        op = random.choice(self.operations)
        if op == "+":
            return self._generate_addition()
        elif op == "-":
            return self._generate_subtraction()
        elif op == "x":
            return self._generate_multiplication()
        elif op == "÷":
            return self._generate_division()
        else:
            raise ValueError(f"Unknown operator: {op}")

    def generate_batch(self, count: int, allow_duplicates: bool = False) -> list[Question]:
        """Generate `count` questions. If not allow_duplicates, tries to avoid repeats."""
        questions = []
        seen = set()

        for _ in range(count):
            q = None
            for _retry in range(MAX_RETRY_DUPLICATE):
                q = self.generate_one()
                key = (q.operand_a, q.operand_b, q.operator)
                if allow_duplicates or key not in seen:
                    break
            # Even if we hit max retries, use the last generated question
            if q is not None:
                seen.add((q.operand_a, q.operand_b, q.operator))
                questions.append(q)

        return questions

    # ── Private generation helpers ──

    def _generate_addition(self) -> Question:
        a = random.randint(self.addsub_min, self.addsub_max)
        b = random.randint(self.addsub_min, self.addsub_max)
        answer = a + b
        return Question(
            operand_a=a, operand_b=b, operator="+",
            correct_answer=answer,
            display_text=f"{a} + {b} = ?",
        )

    def _generate_subtraction(self) -> Question:
        """Reverse-generation: pick a, then b ≤ a so result is non-negative."""
        a = random.randint(self.addsub_min, self.addsub_max)
        # b can be at most a, but also at least addsub_min
        max_b = max(self.addsub_min, a)
        if max_b < self.addsub_min:
            # Edge case: a < addsub_min should never happen, but guard anyway
            b = self.addsub_min
        else:
            b = random.randint(self.addsub_min, max_b)
        answer = a - b
        return Question(
            operand_a=a, operand_b=b, operator="-",
            correct_answer=answer,
            display_text=f"{a} - {b} = ?",
        )

    def _generate_multiplication(self) -> Question:
        a = random.randint(self.mul_min, self.mul_max)
        b = random.randint(self.mul_min, self.mul_max)
        answer = a * b
        return Question(
            operand_a=a, operand_b=b, operator="x",
            correct_answer=answer,
            display_text=f"{a} × {b} = ?",
        )

    def _generate_division(self) -> Question:
        """Reverse-generation: pick divisor b and quotient c, compute dividend a = b*c.
        This guarantees integer results and no division-by-zero."""
        for _ in range(MAX_RETRY_DUPLICATE):
            b = random.randint(max(self.div_min, 1), max(self.div_max, 1))
            c = random.randint(max(self.div_min, 1), max(self.div_max, 1))
            a = b * c
            if a <= MAX_DIVIDEND:
                return Question(
                    operand_a=a, operand_b=b, operator="÷",
                    correct_answer=c,
                    display_text=f"{a} ÷ {b} = ?",
                )
        # Fallback: use 1 * 1 = 1
        return Question(
            operand_a=1, operand_b=1, operator="÷",
            correct_answer=1,
            display_text="1 ÷ 1 = ?",
        )
