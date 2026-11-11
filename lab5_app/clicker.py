"""Правила кликера: очки, сила клика и стоимость улучшения."""


class Clicker:
    """Игра без таймера: усиление стоит очки и удваивает свою цену."""

    def __init__(self) -> None:
        """Начать новую игру."""
        self.reset()

    @property
    def score(self) -> int:
        """Вернуть текущий запас очков."""
        return self._score

    @property
    def power(self) -> int:
        """Вернуть число очков за один клик."""
        return self._power

    @property
    def upgrade_cost(self) -> int:
        """Вернуть стоимость следующего улучшения."""
        return self._upgrade_cost

    def click(self) -> int:
        """Начислить очки за клик и вернуть новый счёт."""
        self._score += self._power
        return self._score

    def upgrade(self) -> None:
        """Потратить очки и увеличить силу клика на единицу."""
        if self._score < self._upgrade_cost:
            raise ValueError("Пока не хватает очков для улучшения.")
        self._score -= self._upgrade_cost
        self._power += 1
        self._upgrade_cost *= 2

    def reset(self) -> None:
        """Сбросить счёт, силу клика и стоимость улучшения."""
        self._score = 0
        self._power = 1
        self._upgrade_cost = 10
