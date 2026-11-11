"""Четыре арифметические операции без выполнения кода из ввода."""

from decimal import Decimal, DecimalException, localcontext
from operator import add, mul, sub, truediv


def parse_number(text: str) -> Decimal:
    """Прочитать конечное десятичное число с точкой или запятой."""
    if not isinstance(text, str):
        raise TypeError("Число нужно передать строкой.")
    cleaned = text.strip().replace(",", ".")
    if not cleaned or len(cleaned) > 80:
        raise ValueError("Введите число длиной от 1 до 80 символов.")
    try:
        number = Decimal(cleaned)
    except DecimalException as error:
        raise ValueError("Введите корректное число.") from error
    if not number.is_finite():
        raise ValueError("Число должно быть конечным.")
    return number


def calculate(left: str, operation: str, right: str) -> str:
    """Вычислить результат с точностью 28 значащих цифр."""
    operations = {"+": add, "-": sub, "*": mul, "/": truediv}
    if operation not in operations:
        raise ValueError("Выберите операцию +, -, * или /.")
    first, second = parse_number(left), parse_number(right)
    if operation == "/" and second == 0:
        raise ValueError("На ноль делить нельзя.")
    try:
        with localcontext() as context:
            context.prec = 28
            result = operations[operation](first, second)
            if result == 0:
                return "0"
            result = result.normalize()
            if -6 <= result.adjusted() <= 20:
                return format(result, "f")
            return str(result)
    except DecimalException as error:
        raise ValueError("Результат выходит за диапазон Decimal.") from error
