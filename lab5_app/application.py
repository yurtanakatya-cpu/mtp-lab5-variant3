"""Общее окно и четыре вкладки пяти заданий варианта."""

import tkinter as tk
from tkinter import ttk

from .calculator_tab import CalculatorTab
from .clicker_tab import ClickerTab
from .color_tab import ColorTab
from .storage import TaskStore
from .tasks_tab import TasksTab


class Application(ttk.Frame):
    """Объединить самостоятельные разделы в ttk.Notebook."""

    def __init__(self, root: tk.Tk, store: TaskStore) -> None:
        """Настроить размеры окна и переключение вкладок с клавиатуры."""
        super().__init__(root, padding=16)
        root.title("Лабораторная №5 · Вариант 3")
        root.geometry("820x570")
        root.minsize(760, 520)
        root.protocol("WM_DELETE_WINDOW", root.destroy)
        style = ttk.Style(root)
        style.configure("Heading.TLabel", font=("Segoe UI", 16, "bold"))
        self.pack(fill="both", expand=True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        ttk.Label(self, text="Лабораторная работа №5 · Вариант 3").grid(
            row=0, column=0, sticky="w", pady=(0, 12)
        )
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="nsew")
        self.calculator = CalculatorTab(self.notebook)
        self.colors = ColorTab(self.notebook)
        self.clicker = ClickerTab(self.notebook)
        self.tasks = TasksTab(self.notebook, store)
        for tab, title in ((self.calculator, "Калькулятор"),
                           (self.colors, "Цветная панель"),
                           (self.clicker, "Кликер"),
                           (self.tasks, "Задачи · SQLite")):
            self.notebook.add(tab, text=title)
        self.notebook.enable_traversal()
