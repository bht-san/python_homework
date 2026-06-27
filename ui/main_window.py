"""Main window — owns the Notebook, wires frames together."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from constants import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT,
    MODE_TIMED,
)
from question_engine import QuestionEngine
from practice_session import PracticeSession
from ui.settings_frame import SettingsFrame
from ui.practice_frame import PracticeFrame
from ui.results_frame import ResultsFrame
from file_generator import FileGenerator


class MainWindow:
    """Top-level application window."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self._practice_active = False

        # Center the window
        self._center_window()

        # ── Notebook (tab container) ──
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        # ── Create frames ──
        self.settings_frame = SettingsFrame(
            self.notebook,
            on_start=self._on_start_practice,
            on_generate_file=self._on_generate_file,
        )
        self.practice_frame = PracticeFrame(
            self.notebook,
            on_session_end=self._on_session_end,
            on_quit=self._on_quit_practice,
        )
        self.results_frame = ResultsFrame(
            self.notebook,
            on_retry=self._on_retry,
            on_print_wrong=self._on_print_wrong,
        )

        # ── Add tabs ──
        self.notebook.add(self.settings_frame, text="练习设置")
        self.notebook.add(self.practice_frame, text="开始练习")
        self.notebook.add(self.results_frame, text="练习记录")

        # Prevent tab switching during practice
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # ── Status bar ──
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(
            root, textvariable=self.status_var,
            relief="sunken", anchor="w", padding=(10, 3),
        )
        status_bar.pack(fill="x", side="bottom")

        # ── Window close handler ──
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        w = WINDOW_WIDTH
        h = WINDOW_HEIGHT
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ── Navigation helpers ──

    def _switch_to_tab(self, index: int):
        """Switch notebook to the given tab index."""
        self._locked_tab = index
        self.notebook.select(index)

    def _set_status(self, msg: str):
        """Update the status bar."""
        self.status_var.set(msg)

    def _on_tab_changed(self, event=None):
        """Prevent manual tab switching during an active practice session."""
        if self._practice_active:
            # Force stay on practice tab (index 1)
            current = self.notebook.index("current")
            if current != 1:
                self.notebook.select(1)

    def _on_close(self):
        """Handle window close — clean up any running timers."""
        if self._practice_active:
            # Let the practice frame finish gracefully (timer cancels happen there)
            pass
        self.root.destroy()

    # ── Callbacks: Settings → Practice ──

    def _on_start_practice(self, config: dict):
        """Called when user clicks '开始练习' in settings."""
        try:
            engine = QuestionEngine(config)
        except ValueError as e:
            messagebox.showerror("错误", str(e))
            return

        # Generate question batch
        if config["mode"] == MODE_TIMED:
            # For timed mode, generate a large pool so user never runs out
            batch_count = 500
            session = PracticeSession(
                engine.generate_batch(batch_count),
                mode=config["mode"],
                time_limit=config["time_limit"],
            )
        else:
            batch_count = config["question_count"]
            session = PracticeSession(
                engine.generate_batch(batch_count, allow_duplicates=False),
                mode=config["mode"],
                question_count=batch_count,
            )

        self._current_config = config
        self._practice_active = True
        self.practice_frame.start_session(session)
        self._switch_to_tab(1)  # Practice tab
        self._set_status(f"正在练习 — {self._describe_config(config)}")

    @staticmethod
    def _describe_config(config: dict) -> str:
        """Return a short description of the config."""
        ops = "、".join(config["operations"])
        if config["mode"] == MODE_TIMED:
            return f"运算：{ops} | 计时 {config['time_limit'] // 60} 分钟"
        else:
            return f"运算：{ops} | 定量 {config['question_count']} 题"

    # ── Callbacks: Practice → Results ──

    def _on_session_end(self, session: PracticeSession):
        """Called when practice session completes."""
        self._practice_active = False
        self.results_frame.display(session)
        self._switch_to_tab(2)  # Results tab
        correct, wrong, unanswered = session.score
        self._set_status(
            f"练习结束 — 正确 {correct}，错误 {wrong}，"
            f"准确率 {session.accuracy * 100:.0f}%"
        )

    def _on_quit_practice(self):
        """User clicks '提前结束' during practice."""
        # The practice_frame already finishes the session,
        # and calls on_session_end via after().
        # Nothing extra needed here.
        pass

    # ── Callbacks: Results → Settings ──

    def _on_retry(self):
        """User clicks '再来一组'."""
        self._switch_to_tab(0)  # Settings tab
        self._set_status("就绪 — 请设置练习参数")

    def _on_print_wrong(self, session: PracticeSession):
        """User clicks '打印错题'."""
        wrong_qs = session.get_wrong_questions()
        if not wrong_qs:
            messagebox.showinfo("提示", "没有错题可打印！")
            return

        # Ask for save location
        path = filedialog.asksaveasfilename(
            title="保存错题文件",
            defaultextension=".txt",
            filetypes=[
                ("文本文件", "*.txt"),
                ("CSV 文件", "*.csv"),
            ],
            initialfile="错题回顾.txt",
        )
        if not path:
            return

        try:
            if path.endswith(".csv"):
                FileGenerator.generate_wrong_questions_csv(wrong_qs, path)
            else:
                FileGenerator.generate_wrong_questions_txt(wrong_qs, path)
            self._set_status(f"错题已保存至：{path}")
            messagebox.showinfo("保存成功", f"错题已保存至：\n{path}")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    # ── Callback: Generate file ──

    def _on_generate_file(self, config: dict):
        """User clicks '生成题目到文件'."""
        try:
            engine = QuestionEngine(config)
        except ValueError as e:
            messagebox.showerror("错误", str(e))
            return

        # Ask for count
        count = config.get("question_count", 20)
        if config["mode"] == MODE_TIMED or count == 0:
            count = 20  # default for standalone file generation

        # Ask for save location
        path = filedialog.asksaveasfilename(
            title="保存题目文件",
            defaultextension=".txt",
            filetypes=[
                ("文本文件", "*.txt"),
                ("CSV 文件 (含答案)", "*.csv"),
            ],
            initialfile="算术练习题.txt",
        )
        if not path:
            return

        try:
            questions = engine.generate_batch(count, allow_duplicates=False)
            if path.endswith(".csv"):
                FileGenerator.generate_csv(questions, path, include_answers=True)
            else:
                FileGenerator.generate_txt(questions, path, config)

            self._set_status(f"题目已保存至：{path}")
            messagebox.showinfo(
                "生成成功",
                f"已生成 {len(questions)} 道题目，保存至：\n{path}",
            )
        except Exception as e:
            messagebox.showerror("生成失败", str(e))
