"""File output — generates printable question files (TXT and CSV)."""

import csv
from datetime import date
from typing import Optional

from question_engine import Question
from constants import OPERATIONS


class FileGenerator:
    """Static methods to write question sets to files."""

    @staticmethod
    def generate_txt(
        questions: list[Question],
        output_path: str,
        config: Optional[dict] = None,
    ) -> None:
        """Write questions to a human-readable text file, grouped by operation.

        Args:
            questions: List of Question objects.
            output_path: Path to write the file.
            config: Optional config dict for header info (ranges, etc.).
        """
        # Group questions by operator
        groups: dict[str, list[Question]] = {}
        for q in questions:
            groups.setdefault(q.operator, []).append(q)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("小学生算术练习题\n")
            f.write(f"生成日期: {date.today()}\n")
            if config:
                f.write(f"运算类型: {'、'.join(config.get('operations', []))}\n")
            f.write("=" * 40 + "\n\n")

            for op, label in OPERATIONS.items():
                qs = groups.get(op, [])
                if not qs:
                    continue

                # Section header
                f.write(f"{label}（共 {len(qs)} 题）\n")
                f.write("-" * 30 + "\n")

                for i, q in enumerate(qs, 1):
                    # Pad index for alignment
                    f.write(f"  {i:>3}.   {q.display_text.replace('?', '______')}\n")

                f.write("\n")

            f.write("=" * 40 + "\n")
            f.write("加油！认真完成每一道题！\n")

    @staticmethod
    def generate_csv(
        questions: list[Question],
        output_path: str,
        include_answers: bool = True,
    ) -> None:
        """Write questions to a CSV file.

        Args:
            questions: List of Question objects.
            output_path: Path to write the CSV.
            include_answers: If True, includes the correct answer column.
        """
        with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)

            if include_answers:
                writer.writerow(["序号", "类型", "题目", "正确答案"])
                for i, q in enumerate(questions, 1):
                    writer.writerow([
                        i,
                        OPERATIONS.get(q.operator, q.operator),
                        f"{q.operand_a} {q.operator} {q.operand_b}",
                        q.correct_answer,
                    ])
            else:
                writer.writerow(["序号", "类型", "题目"])
                for i, q in enumerate(questions, 1):
                    writer.writerow([
                        i,
                        OPERATIONS.get(q.operator, q.operator),
                        f"{q.operand_a} {q.operator} {q.operand_b} =",
                    ])

    @staticmethod
    def generate_wrong_questions_txt(
        wrong_questions: list[dict],
        output_path: str,
    ) -> None:
        """Write wrong-question review to a text file."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("错题回顾\n")
            f.write(f"生成日期: {date.today()}\n")
            f.write("=" * 40 + "\n\n")

            for i, record in enumerate(wrong_questions, 1):
                f.write(f"{i}. {record['question']}\n")
                f.write(f"   你的答案: {record['user_answer']}\n")
                f.write(f"   正确答案: {record['correct_answer']}\n\n")

            f.write("=" * 40 + "\n")
            f.write("认真复习错题，下次一定更好！\n")

    @staticmethod
    def generate_wrong_questions_csv(
        wrong_questions: list[dict],
        output_path: str,
    ) -> None:
        """Write wrong-question review to a CSV file."""
        with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["序号", "题目", "你的答案", "正确答案"])
            for i, record in enumerate(wrong_questions, 1):
                writer.writerow([
                    i,
                    record["question"],
                    record["user_answer"],
                    record["correct_answer"],
                ])
