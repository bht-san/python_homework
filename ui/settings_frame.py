"""Settings tab — operation selection, ranges, mode, and action buttons."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable

from constants import (
    OPERATIONS, MODE_TIMED, MODE_FIXED,
    DEFAULT_ADDSUB_MIN, DEFAULT_ADDSUB_MAX,
    DEFAULT_MUL_MIN, DEFAULT_MUL_MAX,
    DEFAULT_DIV_MIN, DEFAULT_DIV_MAX,
    DEFAULT_TIME_LIMIT_MINUTES, DEFAULT_QUESTION_COUNT,
    FONT_TITLE, FONT_BODY,
)


class SettingsFrame(ttk.Frame):
    """Settings panel for configuring the practice session."""

    def __init__(
        self,
        parent: tk.Widget,
        on_start: Callable[[dict], None],
        on_generate_file: Callable[[dict], None],
    ):
        super().__init__(parent)
        self.on_start = on_start
        self.on_generate_file = on_generate_file
        self._build_ui()

    def _build_ui(self):
        # ── Title ──
        title = ttk.Label(self, text="练习设置", font=FONT_TITLE)
        title.pack(pady=(20, 15))

        # ── Operation checkboxes ──
        ops_frame = ttk.LabelFrame(self, text="运算类型", padding=10)
        ops_frame.pack(fill="x", padx=40, pady=(0, 10))

        self.op_vars = {}
        ops_inner = ttk.Frame(ops_frame)
        ops_inner.pack()
        for key, label in OPERATIONS.items():
            var = tk.BooleanVar(value=True)
            self.op_vars[key] = var
            cb = ttk.Checkbutton(ops_inner, text=f"{label} ({key})", variable=var)
            cb.pack(side="left", padx=10)

        # ── Range settings ──
        range_frame = ttk.LabelFrame(self, text="数值范围", padding=10)
        range_frame.pack(fill="x", padx=40, pady=(0, 10))

        # Add/Sub range
        self.addsub_min_var, self.addsub_max_var = self._make_range_row(
            range_frame, "加法 / 减法范围:", DEFAULT_ADDSUB_MIN, DEFAULT_ADDSUB_MAX, 0
        )

        # Mul range
        self.mul_min_var, self.mul_max_var = self._make_range_row(
            range_frame, "乘法范围 (因数):", DEFAULT_MUL_MIN, DEFAULT_MUL_MAX, 1
        )

        # Div range
        self.div_min_var, self.div_max_var = self._make_range_row(
            range_frame, "除法范围 (商):", DEFAULT_DIV_MIN, DEFAULT_DIV_MAX, 2
        )

        # ── Mode selection ──
        mode_frame = ttk.LabelFrame(self, text="练习模式", padding=10)
        mode_frame.pack(fill="x", padx=40, pady=(0, 10))

        self.mode_var = tk.StringVar(value=MODE_FIXED)

        mode_inner = ttk.Frame(mode_frame)
        mode_inner.pack(fill="x")

        # Fixed mode row
        fixed_row = ttk.Frame(mode_inner)
        fixed_row.pack(anchor="w", pady=3)
        rb_fixed = ttk.Radiobutton(
            fixed_row, text="定量模式 — 题目数量:", variable=self.mode_var,
            value=MODE_FIXED, command=self._on_mode_change,
        )
        rb_fixed.pack(side="left")
        self.count_var = tk.IntVar(value=DEFAULT_QUESTION_COUNT)
        self.count_spin = ttk.Spinbox(
            fixed_row, from_=5, to=200, increment=5,
            textvariable=self.count_var, width=6,
        )
        self.count_spin.pack(side="left", padx=(5, 0))
        ttk.Label(fixed_row, text="题").pack(side="left")

        # Timed mode row
        timed_row = ttk.Frame(mode_inner)
        timed_row.pack(anchor="w", pady=3)
        rb_timed = ttk.Radiobutton(
            timed_row, text="计时模式 — 时长:", variable=self.mode_var,
            value=MODE_TIMED, command=self._on_mode_change,
        )
        rb_timed.pack(side="left")
        self.time_var = tk.IntVar(value=DEFAULT_TIME_LIMIT_MINUTES)
        self.time_spin = ttk.Spinbox(
            timed_row, from_=1, to=60, increment=1,
            textvariable=self.time_var, width=6,
        )
        self.time_spin.pack(side="left", padx=(5, 0))
        ttk.Label(timed_row, text="分钟").pack(side="left")

        self._on_mode_change()  # Set initial enabled state

        # ── Action buttons ──
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)

        file_btn = ttk.Button(
            btn_frame, text="📄 生成题目到文件",
            command=self._on_file_click,
        )
        file_btn.pack(side="left", padx=10)

        start_btn = ttk.Button(
            btn_frame, text="▶ 开始练习",
            command=self._on_start_click,
        )
        start_btn.pack(side="left", padx=10)

    @staticmethod
    def _make_range_row(parent, label_text, default_min, default_max, row):
        """Create a 'label: min [spin] max [spin]' row."""
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill="x", pady=3)

        lbl = ttk.Label(row_frame, text=label_text, width=22, anchor="e")
        lbl.pack(side="left", padx=(0, 5))

        min_var = tk.IntVar(value=default_min)
        ttk.Label(row_frame, text="最小值").pack(side="left")
        ttk.Spinbox(
            row_frame, from_=0, to=999, increment=1,
            textvariable=min_var, width=6,
        ).pack(side="left", padx=(2, 10))

        max_var = tk.IntVar(value=default_max)
        ttk.Label(row_frame, text="最大值").pack(side="left")
        ttk.Spinbox(
            row_frame, from_=1, to=999, increment=1,
            textvariable=max_var, width=6,
        ).pack(side="left", padx=(2, 0))

        return min_var, max_var

    def _on_mode_change(self):
        """Enable/disable spinboxes based on selected mode."""
        if self.mode_var.get() == MODE_FIXED:
            self.count_spin.configure(state="normal")
            self.time_spin.configure(state="disabled")
        else:
            self.count_spin.configure(state="disabled")
            self.time_spin.configure(state="normal")

    # ── Public API ──

    def get_config(self) -> dict:
        """Read all widget values and return a configuration dict."""
        operations = [k for k, v in self.op_vars.items() if v.get()]
        mode = self.mode_var.get()
        config = {
            "operations": operations,
            "addsub_min": self.addsub_min_var.get(),
            "addsub_max": self.addsub_max_var.get(),
            "mul_min": self.mul_min_var.get(),
            "mul_max": self.mul_max_var.get(),
            "div_min": self.div_min_var.get(),
            "div_max": self.div_max_var.get(),
            "mode": mode,
        }
        if mode == MODE_TIMED:
            config["time_limit"] = self.time_var.get() * 60  # convert to seconds
            config["question_count"] = 0
        else:
            config["time_limit"] = 0
            config["question_count"] = self.count_var.get()
        return config

    def validate(self) -> list[str]:
        """Return a list of validation error messages (empty = valid)."""
        errors = []
        config = self.get_config()

        if not config["operations"]:
            errors.append("请至少选择一种运算类型。")

        if config["addsub_min"] > config["addsub_max"]:
            errors.append("加法/减法：最小值不能大于最大值。")
        if config["mul_min"] > config["mul_max"]:
            errors.append("乘法：最小值不能大于最大值。")
        if config["div_min"] > config["div_max"]:
            errors.append("除法：最小值不能大于最大值。")
        if config.get("div_min", 1) < 1:
            errors.append("除法最小值必须 ≥ 1（除数不能为0）。")

        if config["mode"] == MODE_FIXED and config["question_count"] < 1:
            errors.append("题目数量必须 ≥ 1。")
        if config["mode"] == MODE_TIMED and config["time_limit"] < 10:
            errors.append("计时时长至少为 10 秒。")

        return errors

    # ── Button handlers ──

    def _on_start_click(self):
        errors = self.validate()
        if errors:
            messagebox.showwarning("设置错误", "\n".join(errors))
            return
        self.on_start(self.get_config())

    def _on_file_click(self):
        errors = self.validate()
        if errors:
            messagebox.showwarning("设置错误", "\n".join(errors))
            return
        self.on_generate_file(self.get_config())
