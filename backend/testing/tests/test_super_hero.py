from django.test import TestCase
from testing.super_hero import SuperHero


class TestSuperHero(TestCase):

    def setUp(self):
        self.hero = SuperHero(name="SetupHero", power_level=1000)
        self.hero2 = SuperHero(name="SetupHero2", power_level=800)

    def test_hero_creation(self):
        self.assertEqual(self.hero.name, "SetupHero")
        self.assertEqual(self.hero.power_level, 1000)

    def test_hero_strength_comparison(self):
        self.assertTrue(self.hero.is_stronger_than(self.hero2))
        self.assertFalse(self.hero2.is_stronger_than(self.hero))
