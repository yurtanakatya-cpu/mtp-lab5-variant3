"""Проверки настоящей файловой SQLite: CRUD и сохранность данных."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from lab5_app.storage import Task, TaskStore


class StorageTests(unittest.TestCase):
    """Для каждого теста создаётся отдельная временная БД."""

    def setUp(self) -> None:
        """Создать пустое хранилище."""
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "nested" / "tasks.db"
        self.store = TaskStore(self.path)

    def test_crud(self) -> None:
        """Добавление, чтение, изменение и удаление работают по ID."""
        self.assertEqual(self.store.list_tasks(), [])
        task_id = self.store.add("  Подготовить отчёт  ")
        other_id = self.store.add("Вторая задача")
        self.assertEqual(self.store.list_tasks()[0],
                         Task(task_id, "Подготовить отчёт", False))
        self.store.update(task_id, "Отчёт готов", True)
        self.assertEqual(self.store.list_tasks()[0],
                         Task(task_id, "Отчёт готов", True))
        self.store.delete(task_id)
        self.assertEqual(self.store.list_tasks(),
                         [Task(other_id, "Вторая задача", False)])

    def test_persistence(self) -> None:
        """Повторное открытие сохраняет изменения на диске."""
        task_id = self.store.add("Проверить сохранение")
        self.store.update(task_id, "Сохранено", True)
        reopened = TaskStore(self.path)
        self.assertEqual(reopened.list_tasks(),
                         [Task(task_id, "Сохранено", True)])
        reopened.delete(task_id)
        self.assertEqual(TaskStore(self.path).list_tasks(), [])

    def test_sql_text_is_stored_as_data(self) -> None:
        """Кавычки и фрагмент SQL не исполняются."""
        title = "'); DROP TABLE tasks; --"
        task_id = self.store.add(title)
        self.store.update(task_id, title, True)
        self.assertEqual(self.store.list_tasks(), [Task(task_id, title, True)])
        self.store.add("Таблица существует")
        self.assertEqual(len(self.store.list_tasks()), 2)

    def test_invalid_titles_preserve_existing_row(self) -> None:
        """Пустота, длинный текст и переносы не повреждают запись."""
        task_id = self.store.add("Исходная")
        for title in ("", "  ", "я" * 121, "две\nстроки", "две\rстроки"):
            with self.subTest(title=title):
                with self.assertRaises(ValueError):
                    self.store.add(title)
                with self.assertRaises(ValueError):
                    self.store.update(task_id, title, False)
        with self.assertRaises(TypeError):
            self.store.add(123)
        self.assertEqual(self.store.list_tasks(),
                         [Task(task_id, "Исходная", False)])

    def test_title_length_boundary(self) -> None:
        """Ровно 120 символов допустимы."""
        self.store.add("я" * 120)
        self.assertEqual(len(self.store.list_tasks()[0].title), 120)

    def test_invalid_id_and_status(self) -> None:
        """Bool не принимается вместо ID, целое не заменяет bool."""
        task_id = self.store.add("Задача")
        for task_id_value in (True, "1", 1.0):
            with self.subTest(value=task_id_value):
                with self.assertRaises(TypeError):
                    self.store.delete(task_id_value)
                with self.assertRaises(TypeError):
                    self.store.update(task_id_value, "Задача", False)
        with self.assertRaises(ValueError):
            self.store.delete(0)
        with self.assertRaises(TypeError):
            self.store.update(task_id, "Задача", 1)
        with self.assertRaises(TypeError):
            self.store.add("Задача", 1)
        self.assertFalse(self.store.list_tasks()[0].done)

    def test_missing_row(self) -> None:
        """Отсутствующая строка даёт ошибку, следующая запись возможна."""
        with self.assertRaises(ValueError):
            self.store.update(999, "Нет такой", False)
        with self.assertRaises(ValueError):
            self.store.delete(999)
        self.store.add("После ошибки")
        self.assertEqual(len(self.store.list_tasks()), 1)

    def test_invalid_database(self) -> None:
        """Посторонний файл не перезаписывается как новая база."""
        other = self.path.parent / "invalid.db"
        other.write_text("это не база данных", encoding="utf-8")
        with self.assertRaises(sqlite3.DatabaseError):
            TaskStore(other)
        self.assertEqual(other.read_text(encoding="utf-8"),
                         "это не база данных")
