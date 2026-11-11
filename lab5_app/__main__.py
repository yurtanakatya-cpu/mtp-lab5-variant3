"""Запуск графического приложения и выбор файла SQLite."""

import argparse
import sqlite3
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from .application import Application
from .storage import TaskStore

DEFAULT_DATABASE = Path(__file__).resolve().parent.parent / "data" / "tasks.db"


def main(argv: list[str] | None = None) -> int:
    """Открыть приложение; при ошибке запуска вернуть код 1."""
    parser = argparse.ArgumentParser(
        description="Лабораторная №5: приложение Tkinter, вариант 3."
    )
    parser.add_argument(
        "--database", type=Path, default=DEFAULT_DATABASE,
        help="путь к файлу SQLite (по умолчанию data/tasks.db в проекте)",
    )
    args = parser.parse_args(argv)
    try:
        root = tk.Tk()
    except tk.TclError as error:
        print(f"Не удалось открыть Tkinter: {error}", file=sys.stderr)
        return 1
    try:
        store = TaskStore(args.database)
        Application(root, store)
    except (OSError, sqlite3.Error) as error:
        root.withdraw()
        messagebox.showerror(
            "Ошибка открытия базы", f"Не удалось открыть SQLite:\n{error}",
            parent=root,
        )
        root.destroy()
        return 1
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
