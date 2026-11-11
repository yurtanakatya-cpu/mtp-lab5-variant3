"""Графические кнопки и счётчики игры «Кликер»."""

import tkinter as tk
from tkinter import ttk

from .clicker import Clicker


class ClickerTab(ttk.Frame):
    """Синхронизировать виджеты с состоянием игры после каждого действия."""

    def __init__(self, master: tk.Misc) -> None:
        """Создать игру, кнопки и подписи."""
        super().__init__(master, padding=24)
        self.game = Clicker()
        self.score_text = tk.StringVar(self)
        self.power_text = tk.StringVar(self)
        self.upgrade_text = tk.StringVar(self)
        self.message = tk.StringVar(self)
        ttk.Label(self, text="Кликер", style="Heading.TLabel").pack(
            anchor="w", pady=(0, 16)
        )
        self.score_label = ttk.Label(
            self, textvariable=self.score_text, font=("Segoe UI", 24)
        )
        self.score_label.pack(anchor="w", pady=8)
        ttk.Label(self, textvariable=self.power_text).pack(anchor="w")
        self.click_button = ttk.Button(
            self, text="Клик!", command=self.click
        )
        self.click_button.pack(anchor="w", pady=16, ipadx=28, ipady=12)
        self.upgrade_button = ttk.Button(
            self, textvariable=self.upgrade_text, command=self.upgrade
        )
        self.upgrade_button.pack(anchor="w", pady=4)
        self.reset_button = ttk.Button(
            self, text="Начать заново", command=self.reset
        )
        self.reset_button.pack(anchor="w", pady=8)
        ttk.Label(self, textvariable=self.message).pack(anchor="w", pady=8)
        self.refresh()

    def refresh(self) -> None:
        """Обновить счётчики и доступность покупки."""
        self.score_text.set(f"Очки: {self.game.score}")
        self.power_text.set(f"За клик: {self.game.power}")
        self.upgrade_text.set(f"Усилить за {self.game.upgrade_cost} очков")
        available = self.game.score >= self.game.upgrade_cost
        self.upgrade_button.configure(
            state="normal" if available else "disabled"
        )

    def click(self) -> None:
        """Засчитать клик."""
        self.game.click()
        self.message.set("")
        self.refresh()

    def upgrade(self) -> None:
        """Купить улучшение, если очков достаточно."""
        try:
            self.game.upgrade()
        except ValueError as error:
            self.message.set(str(error))
        else:
            self.message.set("Сила клика увеличена.")
        self.refresh()

    def reset(self) -> None:
        """Начать новую игру без сохранения старого счёта."""
        self.game.reset()
        self.message.set("Новая игра.")
        self.refresh()
