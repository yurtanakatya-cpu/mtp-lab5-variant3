"""Проверки арифметики и некорректного ввода."""

import unittest

from lab5_app.calculator import calculate, parse_number


class CalculatorTests(unittest.TestCase):
    """Операции, десятичные дроби и ошибки."""

    def test_four_operations(self) -> None:
        """Все четыре операции дают ожидаемый результат."""
        for operation, expected in (("+", "9"), ("-", "3"),
                                    ("*", "18"), ("/", "2")):
            with self.subTest(operation=operation):
                self.assertEqual(calculate("6", operation, "3"), expected)

    def test_decimal_comma_and_negative(self) -> None:
        """Дроби считаются десятично, поддерживаются пробелы и минус."""
        self.assertEqual(calculate(" 0,1 ", "+", "0.2"), "0.3")
        self.assertEqual(calculate("-2.5", "*", "4"), "-10")

    def test_repeating_fraction(self) -> None:
        """Периодическая дробь ограничена 28 значащими цифрами."""
        self.assertEqual(calculate("1", "/", "3"), "0." + "3" * 28)

    def test_invalid_numbers(self) -> None:
        """Пустые, нечисловые и бесконечные значения отклоняются."""
        for value in ("", " ", "abc", "1,2.3", "NaN", "sNaN", "Infinity",
                      "1" * 81, "__import__('os')"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_number(value)
        with self.assertRaises(TypeError):
            parse_number(True)

    def test_zero_and_invalid_operation(self) -> None:
        """Нулевой результат допустим, деление на ноль запрещено."""
        self.assertEqual(calculate("2", "-", "2"), "0")
        for args in (("1", "/", "-0.0"), ("1", "**", "2")):
            with self.subTest(args=args), self.assertRaises(ValueError):
                calculate(*args)

    def test_decimal_overflow(self) -> None:
        """Чрезмерный результат превращается в понятную ошибку."""
        with self.assertRaises(ValueError):
            calculate("1e999999", "*", "1e999999")
