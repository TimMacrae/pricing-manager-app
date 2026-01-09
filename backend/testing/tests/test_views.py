from django.forms import ValidationError
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from testing.models import Product
from testing.models import User
from unittest.mock import patch
from requests.exceptions import Timeout, RequestException


class TestTestingViews(SimpleTestCase):

    def test_testing_view_get(self):
        response = self.client.get('/testing/')  # Adjust the URL as needed
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
                         "message": "Testing app is working!"})


class TestTestingProductView(TestCase):

    def setUp(self):
        # Create some test products
        self.product1 = Product.objects.create(
            name="Product 1", price=100.00, stock_count=10)
        self.product2 = Product.objects.create(
            name="Product 2", price=150.00, stock_count=5)

    def test_testing_product_view_get(self):
        # Adjust the URL as needed
        response = self.client.get('/testing/products/')
        self.assertEqual(response.status_code, 200)
        expected_data = [
            {
                "id": self.product1.id,
                "name": "Product 1",
                "price": "100.00",
            },
            {
                "id": self.product2.id,
                "name": "Product 2",
                "price": "150.00",
            }
        ]
        self.assertEqual(response.json(), expected_data)

    def test_testing_product_view_no_products(self):
        # Delete all products to test empty response
        Product.objects.all().delete()
        response = self.client.get('/testing/products/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_testing_product_view_post_valid_data(self):
        valid_data = {
            "name": "New Product",
            "price": "200.00",
            "stock_count": 15
        }
        response = self.client.post(
            '/testing/products/', data=valid_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], valid_data["name"])
        self.assertEqual(response.json()["price"], valid_data["price"])
        # Verify that the product was created in the database
        self.assertTrue(Product.objects.filter(name="New Product").exists())

    def test_testing_product_view_post_invalid_data(self):
        invalid_data = {
            "name": "",  # Name is required
            "price": "-50.00",  # Price cannot be negative
            "stock_count": -5  # Stock count cannot be negative
        }
        response = self.client.post(
            '/testing/products/', data=invalid_data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.json())
        self.assertEqual(Product.objects.count(), 2)


class TestTestingUserProfileView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass')

    def test_testing_user_profile_view_post_authenticated(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get('/testing/users/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], 'testuser')

    def test_testing_user_profile_view_post_unauthenticated(self):
        response = self.client.get('/testing/users/')
        # Forbidden for unauthenticated users
        self.assertEqual(response.status_code, 403)


class TestTestingUserLoginView(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='loginUser', password='loginPass')

    def test_testing_user_login_view_post_valid_credentials(self):
        valid_credentials = {
            "username": "loginUser",
            "password": "loginPass"
        }
        response = self.client.post(
            '/testing/users/login/', data=valid_credentials, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], 'loginUser')

    def test_testing_user_login_view_post_invalid_credentials(self):
        invalid_credentials = {
            "username": "loginUser",
            "password": "wrongPass"
        }
        response = self.client.post(
            '/testing/users/login/', data=invalid_credentials, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        self.assertEqual(response.json()["error"], "Invalid credentials")


class TestTestingThirdPartyView(SimpleTestCase):

    @patch('testing.views.requests.get')
    def test_testing_third_party_view_get_success(self, mock_get):
        mock_get.return_value.status_code = 200
        return_data = {
            "userId": 1,
            "id": 1,
            "title": "test title",
            "body": "test body"
        }
        mock_get.return_value.json.return_value = return_data

        response = self.client.get(reverse('testing-external-data-view'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, return_data)
        mock_get.assert_called_once_with(
            "https://jsonplaceholder.typicode.com/todos/1", timeout=10)

    def test_testing_third_party_view_get_timeout(self):

        with patch('testing.views.requests.get', side_effect=Timeout):
            response = self.client.get(reverse('testing-external-data-view'))
            self.assertEqual(response.status_code, 504)
            self.assertIn("error", response.json())
            self.assertEqual(
                response.json()["error"], "The request to the third-party service timed out.")

    def test_testing_third_party_view_get_request_exception(self):

        with patch('testing.views.requests.get', side_effect=RequestException("Service Unavailable")):
            response = self.client.get(reverse('testing-external-data-view'))
            self.assertEqual(response.status_code, 502)
            self.assertIn("error", response.json())
            self.assertIn("An error occurred: Service Unavailable",
                          response.json()["error"])
