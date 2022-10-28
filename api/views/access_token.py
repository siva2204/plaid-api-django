import json
from django.http import HttpRequest, JsonResponse, response
from django.views import View
import plaid
from ..plaid_client import plaid_client
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest


class AccessTokenView(View):
    def post(self, request: HttpRequest):
        # public token will be sent in request

        response = {
            "status_code": 200,
            "message": " "
        }

        if not request.user.is_authenticated:
            response["message"] = "user not authenticated"
            response["status_code"] = 401
            return JsonResponse(response, status=401)

        public_token = request.POST["public_token"]

        exchange_request = ItemPublicTokenExchangeRequest(
            public_token=public_token)
        try:
            exchange_response = plaid_client.item_public_token_exchange(
                exchange_request)

            access_token = exchange_response["access_token"]
            item_id = exchange_response["item_id"]

            # save access_token and item_id in db

            #async jobs
            # 1. get items accounts

        except plaid.ApiException as e:
            responseBody = json.loads(e.body)
            response["message"] = responseBody["error_message"]
            response["status_code"] = e.status
            return JsonResponse(response, status=e.status)
