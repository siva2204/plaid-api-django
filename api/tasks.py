"""This files conatins async tasks, i.e Plaid Async fetch requests"""
import json
from pydoc import plain
from celery import shared_task

from api.models import Account, Item
from .plaid_client import plaid_client as client
from plaid.model import accounts_get_request
import plaid


@shared_task
def get_accounts(access_token):
    # fetch accounts associated with item
    # saving it in the database
    try:
        request = accounts_get_request.AccountsGetRequest(
            access_token=access_token)

        response = client.accounts_get(request)
        accounts = response["accounts"]
        item = Item.objects.get(access_token=access_token)
        # item can't be None here, so skipping the check here :))

        for account in accounts:
            new_account = Account(access_token=item,
                                  account_id=account["account_id"],
                                  name=account["name"], official_name=account["official_name"],
                                  subtype=account["subtype"], type=account["type"],
                                  # TODO test these two fileds
                                  available_balance=account["available_balance"], current_balance=account["current_balance"]
                                  )
            new_account.save()

    except plaid.ApiException as e:
        responseBody = json.loads(e.body)
        print("get_accounts failed: ",
              responseBody["error_message"], " ", responseBody["error_code"])
    except Exception as e:
        print("get_accounts failed to save data in database: ", e)


@shared_task
def sync_transactions(item_id):
    # add new transaction, update updated transaction & delete deleted transactions
    pass
