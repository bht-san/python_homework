"""Results tab — score summary and wrong-question review."""

import tkinter as tk
from tkinter import ttk
from typing import Callable

from constants import (
    COLOR_CORRECT, COLOR_WRONG, COLOR_TEXT,
    FONT_TITLE, FONT_SCORE, FONT_RESULT, FONT_BODY,
)
from practice_session import PracticeSession


class ResultsFrame(ttk.Frame):
    """Displays practice session results: score, accuracy, wrong question review."""

    def __init__(
        self,
        parent: tk.Widget,
        on_retry: Callable[[], None],
        on_print_wrong: Callable[[PracticeSession], None],
    ):
        super().__init__(parent)
        self.on_retry = on_retry
        self.on_print_wrong = on_print_wrong
        self._session: PracticeSession = None

        self._build_ui()

    def _build_ui(self):
        # ── Bottom buttons (pack first → reserved at bottom) ──
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side="bottom", fill="x", padx=40, pady=(5, 15))

        retry_btn = ttk.Button(
            btn_frame, text="🔄 再来一组", command=self.on_retry,
        )
        retry_btn.pack(side="left", padx=10)

        self.print_btn = ttk.Button(
            btn_frame, text="🖨 打印错题",
            command=self._on_print_wrong,
            state="disabled",
        )
        self.print_btn.pack(side="left", padx=10)

        # ── Scrollable wrong-question list (fills remaining space) ──
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True, padx=40, pady=(0, 5))

        self.review_canvas = tk.Canvas(container, height=80)
        scrollbar = ttk.Scrollbar(
            container, orient="vertical", command=self.review_canvas.yview,
        )
        self.review_inner = ttk.Frame(self.review_canvas)

        self.review_inner.bind("<Configure>", lambda e: self.review_canvas.configure(
            scrollregion=self.review_canvas.bbox("all"),
        ))
        self.review_canvas.create_window((0, 0), window=self.review_inner, anchor="nw")
        self.review_canvas.configure(yscrollcommand=scrollbar.set)

        self.review_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.no_wrong_label = ttk.Label(
            self.review_inner, text="", font=FONT_BODY,
        )

        # ── Wrong questions review title ──
        review_title = ttk.Label(self, text="错题回顾", font=FONT_RESULT)
        review_title.pack(side="top", pady=(0, 0))

        # ── Separator ──
        ttk.Separator(self, orient="horizontal").pack(
            side="top", fill="x", padx=40, pady=(0, 5),
        )

        # ── Summary area ──
        self.summary_frame = ttk.Frame(self)
        self.summary_frame.pack(side="top", fill="x", padx=60, pady=(0, 5))

        self.score_label = tk.Label(
            self.summary_frame, text="", font=FONT_SCORE, fg=COLOR_TEXT,
        )
        self.score_label.pack(pady=2)

        self.accuracy_label = tk.Label(
            self.summary_frame, text="", font=FONT_RESULT, fg=COLOR_TEXT,
        )
        self.accuracy_label.pack(pady=2)

        self.time_label = tk.Label(
            self.summary_frame, text="", font=FONT_BODY, fg=COLOR_TEXT,
        )
        self.time_label.pack(pady=2)

        self.stars_label = tk.Label(
            self.summary_frame, text="", font=FONT_SCORE, fg="#f39c12",
        )
        self.stars_label.pack(pady=2)

        # ── Title ──
        title = ttk.Label(self, text="练习记录", font=FONT_TITLE)
        title.pack(side="top", pady=(20, 5))

    # ── Public API ──

    def display(self, session: PracticeSession) -> None:
        """Show the results for a completed session."""
        self._session = session

        correct, wrong, unanswered = session.score
        total_answered = correct + wrong
        total = total_answered + unanswered
        accuracy = session.accuracy * 100
        elapsed = session.elapsed_seconds
        mins, secs = divmod(elapsed, 60)

        # Score line
        self.score_label.configure(
            text=f"本次成绩：{correct}/{total_answered} 正确",
        )

        # Accuracy line
        self.accuracy_label.configure(
            text=f"正确率：{accuracy:.0f}%",
        )

        # Time line
        if session.mode == "timed":
            self.time_label.configure(
                text=f"用时：{mins}:{secs:02d}（共答 {total_answered} 题）",
            )
        else:
            self.time_label.configure(
                text=f"用时：{mins}:{secs:02d}",
            )

        # Stars
        stars = self._get_stars(accuracy)
        self.stars_label.configure(text=stars)

        # Wrong questions review
        self._build_wrong_questions_list(session)

        # Enable/disable print wrong button
        if wrong > 0:
            self.print_btn.configure(state="normal")
        else:
            self.print_btn.configure(state="disabled")

    def _build_wrong_questions_list(self, session: PracticeSession) -> None:
        """Populate the scrollable wrong-question review area."""
        # Clear existing widgets
        for w in self.review_inner.winfo_children():
            w.destroy()

        wrong_qs = session.get_wrong_questions()

        if not wrong_qs:
            self.no_wrong_label = ttk.Label(
                self.review_inner,
                text="🎉 太棒了！全部正确，没有错题！",
                font=FONT_RESULT,
            )
            self.no_wrong_label.pack(pady=20)
            return

        for record in wrong_qs:
            row = ttk.Frame(self.review_inner)
            row.pack(fill="x", pady=2)

            text = (
                f"第 {record['index']} 题  "
                f"{record['question']}  "
                f"你的答案：{record['user_answer']}  "
                f"正确答案：{record['correct_answer']}"
            )
            lbl = ttk.Label(row, text=text, font=FONT_BODY, foreground=COLOR_WRONG)
            lbl.pack(anchor="w")

    @staticmethod
    def _get_stars(accuracy: float) -> str:
        """Return star rating based on accuracy percentage."""
        if accuracy >= 95:
            return "⭐⭐⭐⭐⭐ 完美！"
        elif accuracy >= 85:
            return "⭐⭐⭐⭐ 优秀！"
        elif accuracy >= 70:
            return "⭐⭐⭐ 良好"
        elif accuracy >= 60:
            return "⭐⭐ 继续加油"
        else:
            return "⭐ 多加练习"

    def _on_print_wrong(self) -> None:
        """Handle print wrong questions button."""
        if self._session:
            self.on_print_wrong(self._session)
