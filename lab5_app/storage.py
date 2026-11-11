"""Хранение списка задач в SQLite с параметризованными запросами."""

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True)
class Task:
    """Снимок одной строки таблицы tasks."""

    id: int
    title: str
    done: bool


def validate_title(title: str) -> str:
    """Убрать крайние пробелы и проверить однострочное название."""
    if not isinstance(title, str):
        raise TypeError("Название должно быть строкой.")
    title = title.strip()
    if not 1 <= len(title) <= 120 or "\n" in title or "\r" in title:
        raise ValueError("Название: от 1 до 120 символов в одной строке.")
    return title


def validate_id(task_id: int) -> None:
    """Проверить положительный целочисленный идентификатор."""
    if isinstance(task_id, bool) or not isinstance(task_id, int):
        raise TypeError("ID должен быть целым числом.")
    if task_id < 1:
        raise ValueError("ID должен быть положительным.")


class TaskStore:
    """Файловая БД; каждое действие фиксируется и закрывает соединение."""

    def __init__(self, path: str | Path) -> None:
        """Создать каталог и таблицу, не удаляя существующие записи."""
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS tasks ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "title TEXT NOT NULL CHECK(length(trim(title)) "
                "BETWEEN 1 AND 120), "
                "done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0, 1)))"
            )
            connection.execute("SELECT id, title, done FROM tasks LIMIT 0")

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        """Откатить неудачную операцию и всегда закрыть соединение."""
        connection = sqlite3.connect(self.path, timeout=1)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def list_tasks(self) -> list[Task]:
        """Прочитать задачи в порядке добавления."""
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT id, title, done FROM tasks ORDER BY id"
            ).fetchall()
        return [Task(row[0], row[1], bool(row[2])) for row in rows]

    def add(self, title: str, done: bool = False) -> int:
        """Добавить задачу и вернуть выданный SQLite идентификатор."""
        title = validate_title(title)
        if not isinstance(done, bool):
            raise TypeError("Отметка выполнения должна быть bool.")
        with self._connection() as connection:
            cursor = connection.execute(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                (title, int(done)),
            )
            return int(cursor.lastrowid)

    def update(self, task_id: int, title: str, done: bool) -> None:
        """Изменить название и отметку выполнения существующей задачи."""
        validate_id(task_id)
        title = validate_title(title)
        if not isinstance(done, bool):
            raise TypeError("Отметка выполнения должна быть bool.")
        with self._connection() as connection:
            cursor = connection.execute(
                "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
                (title, int(done), task_id),
            )
            if cursor.rowcount != 1:
                raise ValueError("Задача не найдена. Обновите список.")

    def delete(self, task_id: int) -> None:
        """Удалить выбранную задачу по ID, не затрагивая другие."""
        validate_id(task_id)
        with self._connection() as connection:
            cursor = connection.execute(
                "DELETE FROM tasks WHERE id = ?", (task_id,)
            )
            if cursor.rowcount != 1:
                raise ValueError("Задача не найдена. Обновите список.")
