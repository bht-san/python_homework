"""Shared constants for the arithmetic practice application."""

# Window
WINDOW_TITLE = "小学生加减乘除运算练习器"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Default ranges
DEFAULT_ADDSUB_MIN = 1
DEFAULT_ADDSUB_MAX = 20       # Addition / subtraction range
DEFAULT_MUL_MIN = 1
DEFAULT_MUL_MAX = 9            # Multiplication table range (multiplicand)
DEFAULT_DIV_MIN = 1
DEFAULT_DIV_MAX = 9            # Division range (quotient), divisor range same

# Maximum dividend allowed (div_max * div_max for 9x9 = 81 is fine;
# for larger ranges, cap it so numbers don't get unwieldy)
MAX_DIVIDEND = 200

# Practice defaults
DEFAULT_TIME_LIMIT_MINUTES = 3
DEFAULT_QUESTION_COUNT = 20
MAX_RETRY_DUPLICATE = 100      # Max retries to generate a unique question

# Operation definitions: internal key -> display label
OPERATIONS = {
    "+": "加法",
    "-": "减法",
    "x": "乘法",
    "÷": "除法",
}

# Modes
MODE_TIMED = "timed"
MODE_FIXED = "fixed"

# Colors
COLOR_CORRECT = "#27ae60"
COLOR_WRONG = "#e74c3c"
COLOR_BG = "#ecf0f1"
COLOR_QUESTION_BG = "#ffffff"
COLOR_TEXT = "#2c3e50"
COLOR_BUTTON_START = "#2980b9"
COLOR_BUTTON_FILE = "#8e44ad"

# Fonts
FONT_FAMILY = "Microsoft YaHei"
FONT_TITLE = (FONT_FAMILY, 18, "bold")
FONT_BODY = (FONT_FAMILY, 11)
FONT_QUESTION = (FONT_FAMILY, 36, "bold")
FONT_FEEDBACK = (FONT_FAMILY, 14, "bold")
FONT_RESULT = (FONT_FAMILY, 14)
FONT_SCORE = (FONT_FAMILY, 16, "bold")
