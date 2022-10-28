import json
from django.http import HttpRequest, HttpResponse, JsonResponse, response
from django.views import View
import plaid

from api.tasks import get_accounts, sync_transactions
from ..plaid_client import plaid_client
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from ..models import Account, Item, Transactions
from ..util.response import internalservererror_response


class AccessTokenView(View):
    def post(self, request: HttpRequest):
        # public token will be sent in request

        response = {
            "status_code": 200,
            "message": ""
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

            if Item.objects.filter(access_token=access_token).exists():
                response["message"] = "item already linked to this app"
                return JsonResponse(response)

            new_item = Item(access_token=access_token,
                            item_id=item_id, user=request.user)

            # save access_token and item_id in db
            new_item.save()

            # async jobs to celery
            # get items accounts
            get_accounts.delay(access_token)

            response["message"] = "successfully fetched access_token"
            return JsonResponse(response, status=200)
        except plaid.ApiException as e:
            responseBody = json.loads(e.body)
            response["message"] = responseBody["error_message"]
            response["status_code"] = e.status
            return JsonResponse(response, status=e.status)
        except Exception as e:
            print(e)
            return JsonResponse(internalservererror_response(), status=500)


class TransactionsView(View):
    def post(self, request: HttpRequest):
        # fetch users accounts and associated transactions
        response = {
            "status_code": 200,
            "message": "",
        }

        if not request.user.is_authenticated:
            response["message"] = "user not authenticated"
            response["status_code"] = 401
            return JsonResponse(response, status=401)

        try:
            items = Item.objects.filter(user=request.user)
            accounts = []
            data = []

            for item in items:
                account = Account.objects.filter(
                    access_token=item.access_token)
                accounts.extend(list(account))

            for account in accounts:
                transactions = list(
                    Transactions.objects.all().filter(account_id=account))
                result = {
                    "account": {
                        "id": account.id,
                        "name": account.name,
                        "official_name": account.official_name,
                        "current_balance": account.current_balance,
                        "subtype": account.subtype,
                        "type": account.type
                    }
                }

                t_result = []

                for t in transactions:
                    t_result.append({
                        "id": t.id,
                        "account_id": t.account_id.id,
                        "amount": t.amount,
                        "category_id": t.category_id,
                        "category": t.category,
                        "pending": t.pending,
                        "account_owner": t.account_owner
                    })

                result["transactions"] = t_result

                data.append(result)
            response["message"] = "successfully fetched data"
            response["data"] = data

            return JsonResponse(response, status=200)

        except Exception as e:
            print(e)
            response["message"] = "internal server error"
            response["status_code"] = 500
            return JsonResponse(response, status=500)


class WebHookView(View):
    # in this app, this webhooks only handles the transaction updates webhooks
    def post(self, request: HttpRequest):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        item_id = body["item_id"]
        webhook_code = body["webhook_code"]
        webhook_type = body["webhook_type"]

        print("webhook fired", item_id,
              webhook_code, webhook_type)

        if webhook_type != "TRANSACTIONS":
            return HttpResponse("Have a good day")

        if webhook_code == "SYNC_UPDATES_AVAILABLE":
            # this hook will be fired if there are any changes in transaction of an item or all the transactions after item creation
            # this hook is enough to update the transaction in real-time
            initial_update_complete = body["initial_update_complete"]
            sync_transactions.delay(item_id, initial_update_complete)
            pass
        elif webhook_code == "RECURRING_TRANSACTIONS_UPDATE":
            pass
        elif webhook_code == "INITIAL_UPDATE":
            pass
        elif webhook_code == "HISTORICAL_UPDATE":
            pass
        elif webhook_code == "DEFAULT_UPDATE":
            # used for testing, this hook code is fired of initially
            sync_transactions.delay(item_id, False)
        elif webhook_code == "TRANSACTIONS_REMOVED":
            pass

        return HttpResponse("Have a another good day")
