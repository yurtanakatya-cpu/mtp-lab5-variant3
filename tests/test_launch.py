"""Проверки точки входа без запуска цикла GUI."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from lab5_app.__main__ import DEFAULT_DATABASE

PROJECT = Path(__file__).resolve().parents[1]


class LaunchTests(unittest.TestCase):
    """Справка доступна из проекта и по абсолютному пути."""

    def test_help_from_another_directory(self) -> None:
        """Запуск скрипта не зависит от текущего рабочего каталога."""
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, "-B", str(PROJECT / "main.py"), "--help"],
                cwd=directory, capture_output=True, text=True,
                encoding="utf-8", env=self.utf8_environment(), timeout=15,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--database", result.stdout)

    def test_module_help(self) -> None:
        """Доступен запуск python -m lab5_app."""
        result = subprocess.run(
            [sys.executable, "-B", "-m", "lab5_app", "--help"],
            cwd=PROJECT, capture_output=True, text=True, encoding="utf-8",
            env=self.utf8_environment(), timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--database", result.stdout)

    def test_default_database_is_anchored_to_project(self) -> None:
        """Каталог запуска не меняет местоположение стандартной базы."""
        self.assertEqual(DEFAULT_DATABASE, PROJECT / "data" / "tasks.db")

    @staticmethod
    def utf8_environment() -> dict[str, str]:
        """Настроить кодировку вывода дочернего процесса на Windows."""
        return {**os.environ, "PYTHONIOENCODING": "utf-8"}
