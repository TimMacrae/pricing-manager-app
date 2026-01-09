from __future__ import annotations


class SuperHero:
    def __init__(self, name: str, power_level: int):
        self.name = name
        self.power_level = power_level

    def __str__(self):
        return f"{self.name} with power level {self.power_level}"

    def is_stronger_than(self, other_hero: SuperHero) -> bool:
        return self.power_level > other_hero.power_level
