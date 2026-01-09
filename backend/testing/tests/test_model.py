from itertools import product
from django.core.exceptions import ValidationError
from django.test import TestCase
from testing.models import Product
from django.db import IntegrityError


class TestProductModel(TestCase):

    # This is a static class method that sets up data once for the TestCase
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product", price=50.00, stock_count=20)
        self.discounted_product = Product(
            name="Discounted Product", price=200.00, stock_count=5)

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(float(self.product.price), 50.00)
        self.assertEqual(self.product.stock_count, 20)

    def test_get_discounted_price(self):
        self.assertEqual(
            self.discounted_product.get_discounted_price(10), 180.00)
        self.assertEqual(
            # No discount
            self.product.get_discounted_price(0), self.product.price)
        self.assertEqual(
            self.product.get_discounted_price(100), 0.00)  # 100% discount

    def test_in_stock_property(self):
        product_in_stock = self.product
        product_out_of_stock = Product(
            name="Out of Stock Product", price=50.00, stock_count=0)
        self.assertTrue(product_in_stock.in_stock)
        self.assertFalse(product_out_of_stock.in_stock)

    def test_clean_method_validations(self):
        product_negative_price = Product(
            name="Negative Price Product", price=-10.00, stock_count=5)
        product_negative_stock = Product(
            name="Negative Stock Product", price=10.00, stock_count=-5)

        with self.assertRaises(ValidationError) as cm_price:
            product_negative_price.clean()
        self.assertIn("Price cannot be negative.", str(cm_price.exception))

        with self.assertRaises(ValidationError) as cm_stock:
            product_negative_stock.clean()
        self.assertIn("Stock count cannot be negative.",
                      str(cm_stock.exception))

    def test_constrain_price_non_negative_on_save(self):
        self.product.price = -20.00
        with self.assertRaises(IntegrityError):
            self.product.save()

    def test_constrain_stock_count_non_negative_on_save(self):
        self.product.stock_count = -5
        with self.assertRaises(IntegrityError):
            self.product.save()
