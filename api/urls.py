from django.urls import path
from .views import user

app_name = "api"

urlpatterns = [
    # Auth routes
    path("user/signup/", user.SignUpView.as_view(), name="user-signup"),
    path("user/login/", user.LoginView.as_view(), name="user-login"),
    path("user/logout", user.LogoutView.as_view(), name="user-logout"),
    path("user/me/", user.MeView.as_view(), name="user-me")
]
