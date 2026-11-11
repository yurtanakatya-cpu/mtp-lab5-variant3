"""Цветная панель с циклическим переключением палитры."""

import tkinter as tk
from tkinter import ttk

PALETTE = (
    ("Голубой", "#c7e6ff"),
    ("Зелёный", "#caedd5"),
    ("Жёлтый", "#fff0b3"),
    ("Розовый", "#f6cddd"),
)


class ColorTab(ttk.Frame):
    """Кнопка меняет настоящий фон панели, а не только подпись."""

    def __init__(self, master: tk.Misc) -> None:
        """Показать начальный цвет и кнопку смены."""
        super().__init__(master, padding=24)
        self.color_index = 0
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        ttk.Label(self, text="Цветная панель", style="Heading.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 16)
        )
        self.panel = tk.Label(
            self, text=PALETTE[0][0], background=PALETTE[0][1],
            foreground="#243042", font=("Segoe UI", 22), height=5,
        )
        self.panel.grid(row=1, column=0, sticky="nsew")
        self.change_button = ttk.Button(
            self, text="Сменить цвет", command=self.change_color
        )
        self.change_button.grid(row=2, column=0, sticky="w", pady=(16, 0))

    def change_color(self) -> None:
        """Перейти к следующему цвету, после последнего вернуться к первому."""
        self.color_index = (self.color_index + 1) % len(PALETTE)
        name, color = PALETTE[self.color_index]
        self.panel.configure(text=name, background=color)
