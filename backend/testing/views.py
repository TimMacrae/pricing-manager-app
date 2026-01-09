from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import TestingProductSerializer, TestingProductsCreateSerializer, TestingUserSerializer
from .models import Product, User
from rest_framework.permissions import IsAuthenticated
from requests.exceptions import Timeout, RequestException
import requests


class TestingView(APIView):
    """
    A simple testing view to verify that the testing app is set up correctly.
    """

    def get(self, request):
        return Response({"message": "Testing app is working!"})


class TestingProductView(APIView):
    """
    A simple view to test product-related functionality.
    """

    def get(self, request):
        products = Product.objects.all()
        serializer = TestingProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TestingProductsCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class TestingUserProfileView(APIView):
    """
    A simple view to test user-related functionality.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = TestingUserSerializer(request.user)
        return Response(serializer.data)


class TestingUserLoginView(APIView):
    """
    A simple view to test user login functionality.
    """

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                serializer = TestingUserSerializer(user)
                return Response(serializer.data)
            else:
                return Response({"error": "Invalid credentials"}, status=400)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=404)


class TestingThirdPartyView(APIView):
    """
    A view to test integration with a third-party service.
    """

    def get(self, request):
        try:
            response = requests.get(
                "https://jsonplaceholder.typicode.com/todos/1", timeout=10)
            response.raise_for_status()
            return JsonResponse(response.json())
        except Timeout:
            return Response({"error": "The request to the third-party service timed out."}, status=504)
        except RequestException as e:
            # log the exception details for debugging
            return Response({"error": f"An error occurred: {str(e)}"}, status=502)
