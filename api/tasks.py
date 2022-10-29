"""This files conatins async tasks, i.e Plaid Async fetch requests"""
import json
from pydoc import plain
from celery import shared_task
from .util import transactions
from api.models import Account, Item
from .plaid_client import plaid_client as client
from plaid.model import accounts_get_request
import plaid
from .logger import log


@shared_task
def update_accounts(access_token):
    """save and updates accounts accordingly"""
    try:
        request = accounts_get_request.AccountsGetRequest(
            access_token=access_token)

        response = client.accounts_get(request)
        accounts = response["accounts"]
        item = Item.objects.get(access_token=access_token)
        # item can't be None here, so skipping the check here :))

        for account in accounts:

            saved_account = Account.objects.get(
                account_id=account["account_id"])

            if saved_account != None:
                # account is already present in db
                saved_account.name = account["name"]
                saved_account.official_name = account["official_name"]
                saved_account.subtype = account["subtype"]
                saved_account.type = account["type"]
                saved_account.available_balance = account["balances"]["available"]
                saved_account.current_balance = account["balances"]["current"]

                saved_account.save()
                continue

            new_account = Account(access_token=item,
                                  account_id=account["account_id"],
                                  name=account["name"], official_name=account["official_name"],
                                  subtype=account["subtype"], type=account["type"],
                                  available_balance=account["balances"][
                                      "available"], current_balance=account["balances"]["current"]
                                  )
            new_account.save()

    except plaid.ApiException as e:
        responseBody = json.loads(e.body)
        log.error(
            f"get_accounts task failed {responseBody['error_message']} ", e)
    except Exception as e:
        log.error(f"get_accounts task failed to save data in database: ", e)


@shared_task
def sync_transactions(item_id, initial_update_complete=True):
    try:
        # add new transaction, update updated transaction & delete deleted transactions
        transactions.update_transactions(
            item_id=item_id, initial_update_complete=initial_update_complete)
    except plaid.ApiException as e:
        responseBody = json.loads(e.body)
        log.error(
            f"sync_transactions task failed for {item_id} - {responseBody['error_message']}", e)
    except Exception as e:
        log.error("sync_transaction task failed to save data in database: ", e)
