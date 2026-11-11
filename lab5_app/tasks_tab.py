"""Таблица SQLite и форма добавления, изменения и удаления задач."""

import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from .storage import TaskStore


class TasksTab(ttk.Frame):
    """CRUD через кнопки; ID берётся из выделенной строки Treeview."""

    def __init__(self, master: tk.Misc, store: TaskStore) -> None:
        """Построить форму и загрузить существующие записи."""
        super().__init__(master, padding=24)
        self.store = store
        self.title = tk.StringVar(self)
        self.done = tk.BooleanVar(self)
        self.status = tk.StringVar(self)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        ttk.Label(self, text="Задачи · SQLite", style="Heading.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 12)
        )
        form = ttk.Frame(self)
        form.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        form.columnconfigure(1, weight=1)
        ttk.Label(form, text="Название:").grid(row=0, column=0, padx=(0, 8))
        self.title_entry = ttk.Entry(form, textvariable=self.title)
        self.title_entry.grid(row=0, column=1, sticky="ew")
        ttk.Checkbutton(form, text="Выполнено", variable=self.done).grid(
            row=0, column=2, padx=(12, 0)
        )
        table = ttk.Frame(self)
        table.grid(row=2, column=0, sticky="nsew")
        table.columnconfigure(0, weight=1)
        table.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(
            table, columns=("id", "title", "done"), show="headings",
            selectmode="browse", height=8,
        )
        for column, text, width in (("id", "ID", 50),
                                    ("title", "Название", 420),
                                    ("done", "Выполнено", 90)):
            self.tree.heading(column, text=text)
            self.tree.column(column, width=width, minwidth=40,
                             stretch=column == "title")
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            table, orient="vertical", command=self.tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<<TreeviewSelect>>", self.select_task)
        buttons = ttk.Frame(self)
        buttons.grid(row=3, column=0, sticky="w", pady=12)
        self.add_button = ttk.Button(
            buttons, text="Добавить", command=self.add_task
        )
        self.save_button = ttk.Button(
            buttons, text="Сохранить", command=self.save_task
        )
        self.delete_button = ttk.Button(
            buttons, text="Удалить", command=self.delete_task
        )
        self.clear_button = ttk.Button(
            buttons, text="Снять выбор", command=self.clear_form
        )
        self.refresh_button = ttk.Button(
            buttons, text="Обновить", command=self.refresh
        )
        for column, button in enumerate((self.add_button, self.save_button,
                                         self.delete_button,
                                         self.clear_button,
                                         self.refresh_button)):
            button.grid(row=0, column=column, padx=(0, 6))
        ttk.Label(self, textvariable=self.status, wraplength=660).grid(
            row=4, column=0, sticky="w"
        )
        self.refresh()

    def clear_form(self) -> None:
        """Сбросить форму, выделение и доступность действий над строкой."""
        self.tree.selection_remove(*self.tree.selection())
        self.title.set("")
        self.done.set(False)
        self.save_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")

    def refresh(self) -> bool:
        """Прочитать БД, сохранив старый список при ошибке чтения."""
        try:
            tasks = self.store.list_tasks()
        except (sqlite3.Error, OSError) as error:
            self.status.set(f"Ошибка чтения БД: {error}")
            return False
        self.tree.delete(*self.tree.get_children())
        for task in tasks:
            self.tree.insert(
                "", "end", iid=str(task.id),
                values=(task.id, task.title, "Да" if task.done else "Нет"),
            )
        self.clear_form()
        self.status.set(f"Задач в базе: {len(tasks)}")
        return True

    def select_task(self, event: tk.Event | None = None) -> None:
        """Перенести выбранную строку в форму редактирования."""
        selection = self.tree.selection()
        if selection:
            values = self.tree.item(selection[0], "values")
            self.title.set(values[1])
            self.done.set(values[2] == "Да")
            self.save_button.configure(state="normal")
            self.delete_button.configure(state="normal")

    def selected_id(self) -> int:
        """Получить ID выбранной строки или объяснить, чего не хватает."""
        selection = self.tree.selection()
        if not selection:
            raise ValueError("Сначала выберите задачу в таблице.")
        return int(selection[0])

    def _write(self, action: Callable[[], object], success: str) -> None:
        """Выполнить изменение и перезагрузить таблицу после успеха."""
        try:
            action()
        except (ValueError, sqlite3.Error, OSError) as error:
            self.status.set(f"Ошибка: {error}")
        else:
            if self.refresh():
                self.status.set(success)

    def add_task(self) -> None:
        """Добавить новую задачу с названием и отметкой из формы."""
        self._write(
            lambda: self.store.add(self.title.get(), self.done.get()),
            "Задача добавлена.",
        )

    def save_task(self) -> None:
        """Сохранить правки названия и отметки выполнения."""
        self._write(
            lambda: self.store.update(
                self.selected_id(), self.title.get(), self.done.get()
            ),
            "Изменения сохранены.",
        )

    def delete_task(self) -> None:
        """Запросить подтверждение перед удалением выбранной строки."""
        try:
            task_id = self.selected_id()
        except ValueError as error:
            self.status.set(str(error))
            return
        if messagebox.askyesno(
            "Удалить задачу?", "Выбранная задача будет удалена из базы.",
            parent=self,
        ):
            self._write(lambda: self.store.delete(task_id), "Задача удалена.")
