"""Practice tab — question display, answer input, feedback, progress."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from constants import (
    MODE_TIMED, COLOR_CORRECT, COLOR_WRONG,
    COLOR_QUESTION_BG, COLOR_TEXT,
    FONT_QUESTION, FONT_FEEDBACK, FONT_BODY, FONT_TITLE,
)
from practice_session import PracticeSession


class PracticeFrame(ttk.Frame):
    """The active practice panel: shows questions, captures answers."""

    def __init__(
        self,
        parent: tk.Widget,
        on_session_end: Callable[[PracticeSession], None],
        on_quit: Callable[[], None],
    ):
        super().__init__(parent)
        self.on_session_end = on_session_end
        self.on_quit = on_quit

        self._session: Optional[PracticeSession] = None
        self._timer_id: Optional[str] = None
        self._feedback_showing: bool = False
        self._finishing: bool = False

        self._build_ui()

    def _build_ui(self):
        # ── Top bar: progress + timer ──
        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", padx=40, pady=(15, 5))

        self.progress_label = ttk.Label(
            top_bar, text="", font=FONT_BODY,
        )
        self.progress_label.pack(side="left")

        self.timer_label = ttk.Label(
            top_bar, text="", font=FONT_BODY, foreground=COLOR_TEXT,
        )
        self.timer_label.pack(side="right")

        # Separator
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=40)

        # ── Question display area ──
        question_frame = tk.Frame(self, bg=COLOR_QUESTION_BG, bd=2, relief="groove")
        question_frame.pack(fill="x", padx=80, pady=(30, 20))

        self.question_label = tk.Label(
            question_frame,
            text="",
            font=FONT_QUESTION,
            bg=COLOR_QUESTION_BG,
            fg=COLOR_TEXT,
            pady=40,
        )
        self.question_label.pack()

        # ── Answer area ──
        answer_frame = ttk.Frame(self)
        answer_frame.pack(pady=10)

        ttk.Label(answer_frame, text="你的答案:", font=FONT_BODY).pack(
            side="left", padx=(0, 10),
        )

        self.answer_var = tk.StringVar()
        self.answer_entry = ttk.Entry(
            answer_frame, textvariable=self.answer_var,
            font=FONT_BODY, width=10, justify="center",
        )
        self.answer_entry.pack(side="left", padx=(0, 10))
        self.answer_entry.bind("<Return>", lambda e: self._on_submit())
        self.answer_entry.bind("<KeyRelease>", self._on_input_change)

        self.submit_btn = ttk.Button(
            answer_frame, text="提交 ✓", command=self._on_submit,
        )
        self.submit_btn.pack(side="left")
        self.submit_btn.configure(state="disabled")

        # ── Feedback area ──
        self.feedback_label = tk.Label(
            self, text="", font=FONT_FEEDBACK, pady=15,
        )
        self.feedback_label.pack()

        # ── Countdown display (timed mode only) ──
        self.countdown_label = tk.Label(
            self, text="", font=FONT_BODY, fg=COLOR_WRONG,
        )
        self.countdown_label.pack()

        # ── Quit button ──
        self.quit_btn = ttk.Button(
            self, text="✕ 提前结束", command=self._on_quit_click,
        )
        self.quit_btn.pack(pady=(5, 10))

    # ── Public API ──

    def start_session(self, session: PracticeSession) -> None:
        """Begin a new practice session."""
        self._session = session
        self._session.start()
        self._feedback_showing = False
        self._finishing = False

        # Reset UI
        self.feedback_label.configure(text="")
        self.countdown_label.configure(text="")
        self.answer_var.set("")
        self.answer_entry.configure(state="normal")
        self.submit_btn.configure(state="normal")
        self.quit_btn.configure(state="normal")
        self.answer_entry.focus_set()

        # Show first question
        self._show_question(session.current_question)

        # Start timer tick
        self._update_timer_display()
        if session.mode == MODE_TIMED:
            self._start_timer_tick()

    def _show_question(self, q) -> None:
        """Display the given question."""
        if q is None or self._session is None:
            return
        self.question_label.configure(text=q.display_text)
        current, total = self._session.progress
        if self._session.mode == MODE_TIMED:
            self.progress_label.configure(text=f"第 {current} 题")
        else:
            self.progress_label.configure(text=f"第 {current}/{total} 题")
        self._update_timer_display()

    # ── Answer handling ──

    def _on_input_change(self, event) -> None:
        """Enable submit button only when input is a valid integer."""
        val = self.answer_var.get().strip()
        if val == "" or val == "-":
            self.submit_btn.configure(state="disabled")
            return
        try:
            int(val)
            self.submit_btn.configure(state="normal")
        except ValueError:
            self.submit_btn.configure(state="disabled")

    def _on_submit(self) -> None:
        """Process the user's answer."""
        if self._session is None or self._session.is_complete:
            return

        val = self.answer_var.get().strip()
        try:
            answer = int(val)
        except ValueError:
            self.feedback_label.configure(
                text="⚠ 请输入一个整数", fg=COLOR_WRONG,
            )
            return

        is_correct, correct_ans = self._session.submit_answer(answer)

        if is_correct:
            self.feedback_label.configure(
                text="✓ 正确！太棒了！", fg=COLOR_CORRECT,
            )
        else:
            self.feedback_label.configure(
                text=f"✗ 很遗憾，正确答案是 {correct_ans}", fg=COLOR_WRONG,
            )

        self._feedback_showing = True
        # Disable input during feedback
        self.answer_entry.configure(state="disabled")
        self.submit_btn.configure(state="disabled")

        # After a short delay, advance to next question
        self.after(800, self._advance_or_finish)

    def _advance_or_finish(self) -> None:
        """Move to the next question or end the session."""
        if self._session is None or self._session.is_complete:
            return

        # Check timed expiry
        if self._session.check_timed_expiry():
            self._finish_session()
            return

        next_q = self._session.advance()
        if next_q is None:
            self._finish_session()
            return

        self._feedback_showing = False
        self.feedback_label.configure(text="")
        self.answer_var.set("")
        self.answer_entry.configure(state="normal")
        self.submit_btn.configure(state="disabled")
        self.answer_entry.focus_set()
        self._show_question(next_q)

    # ── Timer ──

    def _start_timer_tick(self) -> None:
        """Start the 1-second timer tick (for display only)."""
        if self._session is None or self._finishing:
            return
        # Always update display first — it may schedule _finish_session
        self._update_timer_display()
        if self._session.is_complete:
            return
        self._timer_id = self.after(1000, self._start_timer_tick)

    def _update_timer_display(self) -> None:
        """Update the timer label."""
        if self._session is None:
            return
        elapsed = self._session.elapsed_seconds
        if self._session.mode == MODE_TIMED:
            remaining = self._session.remaining_seconds
            mins, secs = divmod(remaining, 60)
            self.timer_label.configure(text=f"⏱ 剩余 {mins}:{secs:02d}")
            if remaining <= 30:
                self.countdown_label.configure(
                    text=f"⚠ 剩余时间不足 30 秒！", fg=COLOR_WRONG,
                )
            else:
                self.countdown_label.configure(text="")
        else:
            mins, secs = divmod(elapsed, 60)
            self.timer_label.configure(text=f"⏱ 用时 {mins}:{secs:02d}")

        # In timed mode, check for timeout
        if self._session.mode == MODE_TIMED and self._session.check_timed_expiry():
            self.after(100, self._finish_session)

    # ── Session end ──

    def _on_quit_click(self) -> None:
        """User manually ends the session early."""
        if self._session and not self._session.is_complete:
            self.quit_btn.configure(state="disabled")
            self._finish_session()

    def _finish_session(self) -> None:
        """Clean up and notify parent."""
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None

        # Prevent duplicate finish calls (use _finishing flag because
        # advance()/check_timed_expiry() may have already set _finished)
        if self._session is None or self._finishing:
            return

        self._finishing = True
        self._session.mark_finished()

        self.answer_entry.configure(state="disabled")
        self.submit_btn.configure(state="disabled")
        self.quit_btn.configure(state="disabled")
        self.question_label.configure(text="练习结束！")
        self.feedback_label.configure(text="")
        self.countdown_label.configure(text="")
        self.progress_label.configure(text="")
        self.timer_label.configure(text="")

        # Capture session reference to avoid stale closure if self._session changes
        finished_session = self._session
        self.after(500, lambda: self.on_session_end(finished_session))
