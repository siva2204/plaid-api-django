from django.urls import path
from .views import user, access_token

app_name = "api"

urlpatterns = [
    # Auth routes
    path("user/signup/", user.SignUpView.as_view(), name="user-signup"),
    path("user/login/", user.LoginView.as_view(), name="user-login"),
    path("user/logout/", user.LogoutView.as_view(), name="user-logout"),
    path("user/me/", user.MeView.as_view(), name="user-me"),

    # Plaid API routes
    path("plaid/token-exchange/",
         access_token.AccessTokenView.as_view(), name="token-exchange"),
    path("plaid/get-transactions/",
         access_token.TransactionsView.as_view(), name="get-transactions"),
    path("plaid/webhook/", access_token.WebHookView.as_view(), name="plaid-webhook")
]
