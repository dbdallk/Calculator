"""Saedi Calculator — a modern desktop calculator built with PyQt5."""
import sys
import math
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QSplitter, QFrame, QAction,
    QMessageBox, QShortcut
)
from calc_engine import evaluate, CalculationError

APP_STYLE = """
QMainWindow, QWidget { background: #101522; color: #e9eefb; font-family: 'Segoe UI', 'Arial'; }
QLabel#brand { color: #8ea7ff; font-size: 17px; font-weight: 700; }
QLabel#subtle { color: #8995ad; font-size: 11px; }
QLineEdit#expression { background: #171e2e; border: 1px solid #2b3650; border-radius: 12px; padding: 12px; color: #f5f7ff; font-size: 22px; }
QLabel#result { background: #171e2e; border: 1px solid #2b3650; border-radius: 12px; padding: 14px; color: #8ea7ff; font-size: 29px; font-weight: 600; }
QPushButton { background: #202a3d; color: #e9eefb; border: 1px solid #2c3851; border-radius: 10px; padding: 12px 5px; font-size: 16px; }
QPushButton:hover { background: #303e59; border-color: #728cff; }
QPushButton:pressed { background: #43557a; }
QPushButton[role="operator"] { background: #293653; color: #aebeff; }
QPushButton[role="accent"] { background: #6c82f4; color: white; border: none; font-weight: 700; }
QPushButton[role="utility"] { background: #182234; color: #a6b5d5; }
QListWidget { background: #171e2e; border: 1px solid #2b3650; border-radius: 9px; padding: 6px; color: #dce4f8; }
QFrame#panel { background: #141b29; border: 1px solid #28334a; border-radius: 12px; }
"""

class CalculatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Saedi Calculator — Qt 5")
        self.resize(760, 690)
        self.setMinimumSize(440, 570)
        self.degrees = True
        self.last_result = 0
        self.memory = 0.0
        self.history_items = []
        self._build_ui()
        self._shortcuts()
        self.statusBar().showMessage("Ready  •  Keyboard supported  •  Safe expression engine")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 16, 18, 16)
        root.setSpacing(12)

        header = QHBoxLayout()
        brand = QLabel("◈  SAEDI CALCULATOR")
        brand.setObjectName("brand")
        subtitle = QLabel("Qt 5  •  Scientific edition")
        subtitle.setObjectName("subtle")
        header.addWidget(brand)
        header.addStretch()
        header.addWidget(subtitle)
        root.addLayout(header)

        self.expression = QLineEdit()
        self.expression.setObjectName("expression")
        self.expression.setPlaceholderText("Type an expression…  e.g. sin(30) + sqrt(16)")
        self.expression.setAlignment(Qt.AlignRight)
        self.expression.returnPressed.connect(self.calculate)
        root.addWidget(self.expression)

        self.result = QLabel("0")
        self.result.setObjectName("result")
        self.result.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.result.setTextInteractionFlags(Qt.TextSelectableByMouse)
        root.addWidget(self.result)

        tools = QHBoxLayout()
        self.angle_btn = self._button("DEG", "utility", lambda: self.toggle_angle())
        tools.addWidget(self.angle_btn)
        for label, action in [
            ("MC", lambda: self.memory_clear()), ("MR", lambda: self.memory_recall()),
            ("M+", lambda: self.memory_add()), ("M−", lambda: self.memory_subtract()),
            ("Copy", lambda: self.copy_result()), ("⌫", lambda: self.backspace()),
        ]:
            tools.addWidget(self._button(label, "utility", action))
        root.addLayout(tools)

        splitter = QSplitter(Qt.Horizontal)
        keypad_panel = QFrame()
        keypad_panel.setObjectName("panel")
        keypad_layout = QVBoxLayout(keypad_panel)
        keypad_layout.setContentsMargins(10, 10, 10, 10)
        grid = QGridLayout()
        grid.setSpacing(7)
        keypad_layout.addLayout(grid)

        keys = [
            [("sin", "fn"), ("cos", "fn"), ("tan", "fn"), ("(", "operator"), (")", "operator")],
            [("asin", "fn"), ("acos", "fn"), ("atan", "fn"), ("√", "fn"), ("x²", "fn")],
            [("7", ""), ("8", ""), ("9", ""), ("÷", "operator"), ("%", "operator")],
            [("4", ""), ("5", ""), ("6", ""), ("×", "operator"), ("xʸ", "operator")],
            [("1", ""), ("2", ""), ("3", ""), ("−", "operator"), ("π", "fn")],
            [("0", ""), (".", ""), ("e", "fn"), ("+", "operator"), ("=", "accent")],
            [("AC", "utility"), ("±", "utility"), ("ln", "fn"), ("log", "fn"), ("!", "fn")],
        ]
        for row, row_keys in enumerate(keys):
            for col, (label, role) in enumerate(row_keys):
                button = self._button(label, role, lambda checked=False, t=label: self.key_action(t))
                grid.addWidget(button, row, col)
                button.setMinimumHeight(48)
        bottom = QHBoxLayout()
        bottom.addWidget(self._button("1/x", "fn", lambda: self.insert_function("1/(")))
        bottom.addWidget(self._button("|x|", "fn", lambda: self.insert_function("abs(")))
        bottom.addWidget(self._button("Round", "fn", lambda: self.insert_function("round(")))
        bottom.addWidget(self._button("exp", "fn", lambda: self.insert_function("exp(")))
        keypad_layout.addLayout(bottom)
        splitter.addWidget(keypad_panel)

        history_panel = QFrame()
        history_panel.setObjectName("panel")
        history_layout = QVBoxLayout(history_panel)
        history_title = QLabel("HISTORY")
        history_title.setObjectName("brand")
        history_layout.addWidget(history_title)
        self.history = QListWidget()
        self.history.itemDoubleClicked.connect(self.use_history)
        history_layout.addWidget(self.history)
        history_buttons = QHBoxLayout()
        history_buttons.addWidget(self._button("Use", "utility", lambda: self.use_history()))
        history_buttons.addWidget(self._button("Clear", "utility", lambda: self.history.clear()))
        history_layout.addLayout(history_buttons)
        splitter.addWidget(history_panel)
        splitter.setSizes([440, 220])
        root.addWidget(splitter, 1)

        menubar = self.menuBar()
        edit_menu = menubar.addMenu("Edit")
        clear_action = QAction("Clear expression", self)
        clear_action.setShortcut(QKeySequence("Ctrl+L"))
        clear_action.triggered.connect(self.clear)
        edit_menu.addAction(clear_action)
        copy_action = QAction("Copy result", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy_result)
        edit_menu.addAction(copy_action)
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)

    def _button(self, text, role="", callback=None):
        btn = QPushButton(text)
        if role:
            btn.setProperty("role", role)
        if callback:
            btn.clicked.connect(callback)
        return btn

    def _shortcuts(self):
        QShortcut(QKeySequence("Escape"), self, activated=self.clear)
        QShortcut(QKeySequence("Backspace"), self, activated=self.backspace)
        QShortcut(QKeySequence("Ctrl+H"), self, activated=lambda: self.history.setFocus())

    def key_action(self, key):
        if key == "=":
            self.calculate()
        elif key == "AC":
            self.clear()
        elif key == "±":
            text = self.expression.text().strip()
            if text.startswith("-(") and text.endswith(")"):
                self.expression.setText(text[2:-1])
            elif text:
                self.expression.setText(f"-({text})")
            else:
                self.expression.setText("-")
        elif key == "√":
            self.insert_function("sqrt(")
        elif key == "x²":
            self.expression.setText(f"({self.expression.text()})**2" if self.expression.text() else "")
        elif key == "xʸ":
            self.expression.insert("^")
        elif key == "!":
            self.expression.insert("!")
        else:
            self.expression.insert({"×": "*", "÷": "/", "−": "-", "π": "pi"}.get(key, key))

    def insert_function(self, name):
        self.expression.insert(name)

    def calculate(self):
        raw = self.expression.text().strip()
        if not raw:
            return
        expr = raw.replace("!", ")") if False else raw
        # Convert postfix factorial for simple numeric/parenthesized operands.
        import re
        expr = re.sub(r"(\b(?:\d+(?:\.\d*)?|pi|e|\([^()]*\)))!", r"factorial(\1)", expr)
        try:
            value = evaluate(expr, self.degrees)
            shown = self.format_number(value)
            self.result.setText(shown)
            self.last_result = value
            self.history_items.append((raw, shown))
            self.history.insertItem(0, f"{raw}  =  {shown}")
            self.statusBar().showMessage("Calculation successful")
        except CalculationError as error:
            self.result.setText("Error")
            self.statusBar().showMessage(str(error), 5000)

    @staticmethod
    def format_number(value):
        if isinstance(value, float) and value.is_integer() and abs(value) < 1e15:
            return str(int(value))
        return f"{value:.12g}"

    def clear(self):
        self.expression.clear()
        self.result.setText("0")
        self.expression.setFocus()

    def backspace(self):
        self.expression.backspace()
        self.expression.setFocus()

    def toggle_angle(self):
        self.degrees = not self.degrees
        self.angle_btn.setText("DEG" if self.degrees else "RAD")
        self.statusBar().showMessage("Angle mode: " + ("Degrees" if self.degrees else "Radians"), 2500)

    def _current_value(self):
        try:
            return evaluate(self.expression.text(), self.degrees) if self.expression.text().strip() else self.last_result
        except CalculationError:
            return self.last_result

    def memory_clear(self):
        self.memory = 0.0
        self.statusBar().showMessage("Memory cleared", 2000)

    def memory_recall(self):
        self.expression.insert(self.format_number(self.memory))

    def memory_add(self):
        self.memory += self._current_value()
        self.statusBar().showMessage("Added to memory", 2000)

    def memory_subtract(self):
        self.memory -= self._current_value()
        self.statusBar().showMessage("Subtracted from memory", 2000)

    def copy_result(self):
        QApplication.clipboard().setText(self.result.text())
        self.statusBar().showMessage("Result copied to clipboard", 2000)

    def use_history(self, item=None):
        item = item or self.history.currentItem()
        if item:
            text = item.text().split("  =  ", 1)[0]
            self.expression.setText(text)
            self.expression.setFocus()

    def about(self):
        QMessageBox.about(self, "About Saedi Calculator",
            "Saedi Calculator\nA scientific calculator built with Python and PyQt5.\n"
            "Includes a safe math parser, keyboard input, memory and calculation history.")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Saedi Calculator")
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    window = CalculatorWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
