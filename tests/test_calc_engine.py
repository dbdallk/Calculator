import unittest
from calc_engine import evaluate, CalculationError


class CalculatorEngineTests(unittest.TestCase):
    def test_arithmetic_and_precedence(self):
        self.assertEqual(evaluate("2 + 3 * 4"), 14)
        self.assertEqual(evaluate("(2 + 3) * 4"), 20)

    def test_power_and_constants(self):
        self.assertEqual(evaluate("2^3"), 8)
        self.assertAlmostEqual(evaluate("pi"), 3.141592653589793)

    def test_scientific_functions(self):
        self.assertAlmostEqual(evaluate("sin(30)"), 0.5)
        self.assertEqual(evaluate("sqrt(81)"), 9)
        self.assertEqual(evaluate("log(100)"), 2)

    def test_radians(self):
        self.assertAlmostEqual(evaluate("sin(pi/2)", degrees=False), 1)

    def test_division_by_zero(self):
        with self.assertRaises(CalculationError):
            evaluate("1/0")

    def test_rejects_code_execution(self):
        with self.assertRaises(CalculationError):
            evaluate("__import__('os').system('echo unsafe')")

    def test_rejects_empty_input(self):
        with self.assertRaises(CalculationError):
            evaluate(" ")

if __name__ == "__main__":
    unittest.main()
