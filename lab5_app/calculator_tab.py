"""Поля ввода и обработчик кнопки калькулятора."""

import tkinter as tk
from tkinter import ttk

from .calculator import calculate


class CalculatorTab(ttk.Frame):
    """Калькулятор двух чисел с сообщением об ошибке рядом с полями."""

    def __init__(self, master: tk.Misc) -> None:
        """Разместить поля, выбор операции и результат."""
        super().__init__(master, padding=24)
        self.left = tk.StringVar(self)
        self.right = tk.StringVar(self)
        self.operation = tk.StringVar(self, value="+")
        self.result = tk.StringVar(self, value="Результат появится здесь")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(2, weight=1)
        ttk.Label(self, text="Калькулятор", style="Heading.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 16)
        )
        ttk.Label(self, text="Первое число").grid(
            row=1, column=0, sticky="w"
        )
        ttk.Label(self, text="Второе число").grid(
            row=1, column=2, sticky="w"
        )
        self.left_entry = ttk.Entry(self, textvariable=self.left)
        self.left_entry.grid(row=2, column=0, sticky="ew", pady=8)
        ttk.Combobox(
            self, textvariable=self.operation, values=("+", "-", "*", "/"),
            state="readonly", width=4,
        ).grid(row=2, column=1, padx=12)
        self.right_entry = ttk.Entry(self, textvariable=self.right)
        self.right_entry.grid(row=2, column=2, sticky="ew", pady=8)
        self.calculate_button = ttk.Button(
            self, text="Вычислить", command=self.compute
        )
        self.calculate_button.grid(row=3, column=0, sticky="w", pady=12)
        ttk.Label(self, textvariable=self.result, wraplength=620).grid(
            row=4, column=0, columnspan=3, sticky="w", pady=8
        )
        hint = ttk.Label(
            self, text="Дробную часть можно отделить точкой или запятой."
        )
        hint.grid(row=5, column=0, columnspan=3, sticky="w", pady=8)
        self.left_entry.bind("<Return>", lambda event: self.compute())
        self.right_entry.bind("<Return>", lambda event: self.compute())

    def compute(self) -> None:
        """Обновить результат; ошибочный ввод не закрывает приложение."""
        try:
            answer = calculate(
                self.left.get(), self.operation.get(), self.right.get()
            )
        except ValueError as error:
            self.result.set(f"Ошибка: {error}")
        else:
            self.result.set(f"Результат: {answer}")
