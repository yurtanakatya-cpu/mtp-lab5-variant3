"""Интеграционные проверки настоящих виджетов Tkinter и SQLite."""

import sqlite3
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

from lab5_app.application import Application
from lab5_app.color_tab import PALETTE
from lab5_app.storage import TaskStore


class GuiTests(unittest.TestCase):
    """Проверять кнопки и состояние экрана, используя временную базу."""

    def setUp(self) -> None:
        """Создать настоящие виджеты; для тестов нужен рабочий дисплей."""
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.store = TaskStore(Path(temp.name) / "gui.db")
        self.root = tk.Tk()
        self.addCleanup(self.root.destroy)
        self.root.withdraw()
        self.callback_errors = []
        self.root.report_callback_exception = (
            lambda *error: self.callback_errors.append(error)
        )
        self.app = Application(self.root, self.store)
        self.root.update()

    def tearDown(self) -> None:
        """Исключения обработчиков событий тоже должны провалить тест."""
        self.assertEqual(self.callback_errors, [])

    def test_notebook_switches_four_tabs(self) -> None:
        """Вкладки доступны и переключаются без пересоздания окна."""
        notebook = self.app.notebook
        self.assertEqual(len(notebook.tabs()), 4)
        for tab in notebook.tabs():
            notebook.select(tab)
            self.root.update()
            self.assertEqual(notebook.select(), tab)

    def test_calculator_button_and_error_recovery(self) -> None:
        """После деления на ноль можно сразу выполнить другую операцию."""
        tab = self.app.calculator
        tab.left.set("1")
        tab.right.set("0")
        tab.operation.set("/")
        tab.calculate_button.invoke()
        self.assertIn("На ноль", tab.result.get())
        tab.left.set("0,1")
        tab.right.set("0.2")
        tab.operation.set("+")
        tab.calculate_button.invoke()
        self.assertEqual(tab.result.get(), "Результат: 0.3")

    def test_color_button_changes_background_and_wraps(self) -> None:
        """Меняется именно фон, а после полного круга цвет повторяется."""
        tab = self.app.colors
        for step in range(1, len(PALETTE) + 1):
            previous = tab.panel.cget("background")
            tab.change_button.invoke()
            expected_name, expected_color = PALETTE[step % len(PALETTE)]
            self.assertNotEqual(previous, tab.panel.cget("background"))
            self.assertEqual(tab.panel.cget("background"), expected_color)
            self.assertEqual(tab.panel.cget("text"), expected_name)

    def test_clicker_buttons_and_upgrade_availability(self) -> None:
        """Покупка открывается после десяти кликов, сброс очищает игру."""
        tab = self.app.clicker
        self.assertTrue(tab.upgrade_button.instate(("disabled",)))
        for _ in range(10):
            tab.click_button.invoke()
        self.assertFalse(tab.upgrade_button.instate(("disabled",)))
        tab.upgrade_button.invoke()
        self.assertEqual(tab.score_text.get(), "Очки: 0")
        tab.click_button.invoke()
        self.assertEqual(tab.score_text.get(), "Очки: 2")
        tab.reset_button.invoke()
        self.assertEqual(tab.score_text.get(), "Очки: 0")
        self.assertEqual(tab.power_text.get(), "За клик: 1")

    def test_tasks_crud_through_buttons(self) -> None:
        """Кнопки действительно записывают изменения в файловую SQLite."""
        tab = self.app.tasks
        tab.title.set("Проверка кнопок")
        tab.done.set(True)
        tab.add_button.invoke()
        self.root.update()
        task = self.store.list_tasks()[0]
        self.assertTrue(task.done)
        self.assertEqual(tab.tree.item(str(task.id), "values")[1],
                         "Проверка кнопок")
        tab.tree.selection_set(str(task.id))
        self.root.update()
        self.assertEqual(tab.title.get(), "Проверка кнопок")
        tab.title.set("Изменено")
        tab.done.set(False)
        tab.save_button.invoke()
        self.root.update()
        self.assertEqual(self.store.list_tasks()[0].title, "Изменено")
        self.assertFalse(self.store.list_tasks()[0].done)
        tab.tree.selection_set(str(task.id))
        self.root.update()
        with patch("lab5_app.tasks_tab.messagebox.askyesno",
                   return_value=True):
            tab.delete_button.invoke()
        self.root.update()
        self.assertEqual(self.store.list_tasks(), [])
        self.assertEqual(tab.tree.get_children(), ())

    def test_cancel_delete_preserves_row(self) -> None:
        """Отказ в диалоге оставляет запись в базе."""
        task_id = self.store.add("Оставить")
        tab = self.app.tasks
        tab.refresh()
        tab.tree.selection_set(str(task_id))
        self.root.update()
        with patch("lab5_app.tasks_tab.messagebox.askyesno",
                   return_value=False):
            tab.delete_button.invoke()
        self.assertEqual(len(self.store.list_tasks()), 1)

    def test_invalid_title_keeps_form_and_database(self) -> None:
        """Неудачная запись показывает ошибку и сохраняет текст в форме."""
        tab = self.app.tasks
        tab.title.set("x" * 121)
        tab.add_button.invoke()
        self.assertIn("Ошибка", tab.status.get())
        self.assertEqual(tab.title.get(), "x" * 121)
        self.assertEqual(self.store.list_tasks(), [])

    def test_database_errors_are_visible(self) -> None:
        """Ошибка SQLite не уничтожает прежнюю таблицу на экране."""
        self.store.add("Прежняя запись")
        tab = self.app.tasks
        tab.refresh()
        with patch.object(self.store, "list_tasks",
                          side_effect=sqlite3.OperationalError("locked")):
            tab.refresh_button.invoke()
        self.assertEqual(len(tab.tree.get_children()), 1)
        self.assertIn("Ошибка чтения БД", tab.status.get())
        tab.title.set("Новая")
        with patch.object(self.store, "add",
                          side_effect=sqlite3.OperationalError("readonly")):
            tab.add_button.invoke()
        self.assertIn("readonly", tab.status.get())
        self.assertEqual(tab.title.get(), "Новая")
        self.assertEqual(len(self.store.list_tasks()), 1)
