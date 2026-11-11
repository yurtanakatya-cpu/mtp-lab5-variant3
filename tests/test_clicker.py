"""Проверки начисления очков и покупок."""

import unittest

from lab5_app.clicker import Clicker


class ClickerTests(unittest.TestCase):
    """Правила игры проверяются независимо от Tkinter."""

    def test_initial_state_and_clicks(self) -> None:
        """Первый и второй клик начисляют по одному очку."""
        game = Clicker()
        self.assertEqual((game.score, game.power, game.upgrade_cost),
                         (0, 1, 10))
        self.assertEqual(game.click(), 1)
        self.assertEqual(game.click(), 2)

    def test_unaffordable_upgrade_preserves_state(self) -> None:
        """Неудачная покупка ничего не меняет."""
        game = Clicker()
        game.click()
        with self.assertRaises(ValueError):
            game.upgrade()
        self.assertEqual((game.score, game.power, game.upgrade_cost),
                         (1, 1, 10))

    def test_two_upgrades(self) -> None:
        """Улучшения списывают очки, дорожают и усиливают клик."""
        game = Clicker()
        for _ in range(10):
            game.click()
        game.upgrade()
        self.assertEqual((game.score, game.power, game.upgrade_cost),
                         (0, 2, 20))
        for _ in range(10):
            game.click()
        game.upgrade()
        self.assertEqual((game.score, game.power, game.upgrade_cost),
                         (0, 3, 40))
        self.assertEqual(game.click(), 3)

    def test_reset_and_independent_games(self) -> None:
        """Новая игра сбрасывает все параметры и не затрагивает другую."""
        first, second = Clicker(), Clicker()
        for _ in range(12):
            first.click()
        first.upgrade()
        first.reset()
        self.assertEqual((first.score, first.power, first.upgrade_cost),
                         (0, 1, 10))
        self.assertEqual(second.score, 0)
