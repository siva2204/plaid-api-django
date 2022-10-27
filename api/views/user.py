from django.http import HttpRequest, JsonResponse
from django.views.generic import View
from django.contrib.auth import logout, authenticate, login
from api.util.response import internalservererror_response, unauthorized_response
from ..util.user import validate_email
from django.contrib.auth.models import User


class LoginView(View):
    def post(self, request: HttpRequest):
        response = {
            "status_code": 200,
            "message": ""
        }

        if request.user.is_authenticated:
            response["message"] = "Already logged in"
            return JsonResponse(response, status=400)

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is None:
            response["status_code"] = 401
            response["message"] = "invalid credentials"
            return JsonResponse(response, status=401)

        login(request, user)
        response["message"] = "successfully loggedIn!"
        return JsonResponse(response)


class SignUpView(View):
    def post(self, request: HttpRequest):
        response = {
            "status_code": 200,
            "message": ""
        }

        if request.user.is_authenticated:
            response["message"] = "Already logged in"
            return JsonResponse(response, status=400)

        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if not validate_email(email):
            response["message"] = "invalid email address"
            response["status_code"] = 400
            return JsonResponse(response, status=400)

        if len(password) <= 4:
            response["message"] = "password strength is low"
            response["status_code"] = 400
            return JsonResponse(response, status=400)

        if User.objects.filter(email=email).exists():
            response["message"] = "email already resgistered, please login"
            response["status_code"] = 409
            return JsonResponse(response, status=409)

        newuser = User.objects.create(
            username=username, email=email, password=password)

        try:
            newuser.save()
            response["message"] = "registration successful, please login"
            return JsonResponse(response)
        except:
            return JsonResponse(internalservererror_response(), status=500)


class LogoutView(View):
    def post(self, request):
        logout(request)
        return JsonResponse({"status_code": 200, "message": "loggedout successfully!"})


class MeView(View):
    def get(self, request: HttpRequest):
        if not request.user.is_authenticated:
            return JsonResponse(unauthorized_response("user not authenicated"), status=401, safe=False)

        user = {
            "username": request.user.username,
            "email": request.user.email,
            "id": request.user.id,
        }

        return JsonResponse(user)
