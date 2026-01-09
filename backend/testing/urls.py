from django.urls import path
from .views import (
    TestingProductView,
    TestingThirdPartyView,
    TestingUserProfileView,
    TestingView,
    TestingUserLoginView,
)

urlpatterns = [
    path("testing/", TestingView.as_view(), name="testing-view"),
    path("testing/products/", TestingProductView.as_view(),
         name="testing-product-view"),
    path("testing/users/", TestingUserProfileView.as_view(),
         name="testing-user-profile-view"),
    path("testing/users/login/", TestingUserLoginView.as_view(),
         name="testing-user-login-view"),
    path("testing/external-data/", TestingThirdPartyView.as_view(),
         name="testing-external-data-view"),
]
