# Saedi Calculator — Qt 5

A modern scientific desktop calculator built with **Python 3** and **PyQt5 (Qt 5)**.

## Features

- Standard arithmetic, parentheses, percentages, powers and modulo
- Scientific functions: square root, trigonometry and inverse trigonometry, logarithms, exponentials, factorial, absolute value and rounding
- Degree/radian mode; constants `pi`, `e`, and `tau`
- Calculation history; double-click an entry to reuse it
- Memory keys: MC, MR, M+, and M−
- Keyboard input, backspace, clear, and copy result
- Dark interface and selectable result text
- Safe expression parser based on Python's AST; it does not use `eval()`
- Unit tests and GitHub Actions test workflow

## Requirements

- Python 3.9 or newer
- PyQt5 5.15.x (Qt 5)

## Install and run on Windows

Open Command Prompt in the project folder and run:

```bat
py -m pip install -r requirements.txt
py app.py
```

If the `py` command is unavailable, use `python` instead.

## Run tests

```bat
py -m unittest discover -s tests -v
```

## Expression examples

```text
2 + 3 * 4
(2 + 3)^2
sqrt(81)
sin(30)
log(100)
ln(e)
factorial(5)
pi * 2
```

Trigonometric functions use degrees by default; switch to **RAD** for radians. Function names are written in English. Use `^ ` or the xʸ key for powers.

## Project structure

- `app.py` — PyQt5 graphical interface
- `calc_engine.py` — restricted mathematical expression evaluator
- `tests/test_calc_engine.py` — unit tests
- `requirements.txt` — dependency list
- `.github/workflows/tests.yml` — automated test workflow

## License

MIT
