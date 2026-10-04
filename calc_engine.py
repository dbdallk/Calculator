"""Safe mathematical expression evaluator for Saedi Calculator (Qt 5)."""
import ast
import math
import operator
from typing import Callable


class CalculationError(ValueError):
    """Raised when an expression is invalid or cannot be evaluated."""


_BINARY: dict[type, Callable] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY: dict[type, Callable] = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def evaluate(expression: str, degrees: bool = True) -> float:
    """Evaluate a limited math expression without using eval()."""
    expr = expression.strip().replace("×", "*").replace("÷", "/").replace("−", "-")
    expr = expr.replace("^", "**").replace("π", "pi")
    if not expr:
        raise CalculationError("Enter an expression")
    if len(expr) > 500:
        raise CalculationError("Expression is too long")

    def factorial(value):
        if value < 0 or int(value) != value or value > 170:
            raise CalculationError("Factorial requires an integer from 0 to 170")
        return math.factorial(int(value))

    def trig(fn):
        return lambda x: fn(math.radians(x) if degrees else x)

    def inv_trig(fn):
        return lambda x: math.degrees(fn(x)) if degrees else fn(x)

    functions = {
        "sqrt": math.sqrt, "abs": abs, "round": round,
        "sin": trig(math.sin), "cos": trig(math.cos), "tan": trig(math.tan),
        "asin": inv_trig(math.asin), "acos": inv_trig(math.acos),
        "atan": inv_trig(math.atan), "ln": math.log, "log": math.log10,
        "log10": math.log10, "exp": math.exp, "factorial": factorial,
    }
    constants = {"pi": math.pi, "e": math.e, "tau": math.tau}

    try:
        root = ast.parse(expr, mode="eval")
        def visit(node):
            if isinstance(node, ast.Expression):
                return visit(node.body)
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
                left, right = visit(node.left), visit(node.right)
                if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                    raise CalculationError("Exponent is too large")
                result = _BINARY[type(node.op)](left, right)
                if isinstance(result, complex):
                    raise CalculationError("Complex results are not supported")
                return result
            if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
                return _UNARY[type(node.op)](visit(node.operand))
            if isinstance(node, ast.Name) and node.id in constants:
                return constants[node.id]
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                name = node.func.id
                if name not in functions or node.keywords or len(node.args) not in (1, 2):
                    raise CalculationError("Unsupported function")
                args = [visit(arg) for arg in node.args]
                return functions[name](*args)
            raise CalculationError("Unsupported expression")

        result = visit(root)
        if not isinstance(result, (int, float)) or not math.isfinite(result):
            raise CalculationError("Result is not finite")
        return result
    except CalculationError:
        raise
    except ZeroDivisionError as exc:
        raise CalculationError("Cannot divide by zero") from exc
    except (SyntaxError, TypeError, ValueError, OverflowError) as exc:
        raise CalculationError("Invalid expression") from exc
