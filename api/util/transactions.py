from ast import While
from asyncio.windows_events import NULL
from os import access
from unicodedata import category
from pyparsing import null_debug_action
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from api.models import Account, Item, Transactions
from ..plaid_client import plaid_client as client


def get_transactions_updates(item_id, initial_update_complete):
    cursor = NULL
    item = Item.objects.get(item_id=item_id)

    if not initial_update_complete:  # if initial transaction pull is done, last cursor is updated to fetch new transactions
        cursor = item.last_transaction_update

    added = []
    modified = []
    removed = []

    has_more = True  # for pagination logic

    while has_more:
        request = TransactionsSyncRequest(
            access_token=item.access_token
        )

        response = client.transactions_sync(request)

        added.extend(response["added"])
        modified.extend(response["modified"])
        removed.extend(response["removed"])

        has_more = response["has_more"]

        cursor = response["next_cursor"]

    return added, modified, removed, item.access_token, cursor


def update_transactions(item_id, initial_update_complete):
    response = get_transactions_updates(
        item_id=item_id, initial_update_complete=initial_update_complete)

    added = response[0]
    modified = response[1]
    removed = response[2]
    access_token = response[3]
    cursor = response[4]

    _create_transactions(added)
    _delete_transactions(removed)
    _update_transactions(modified)
    _update_cursor(access_token=access, cursor=cursor)


def _update_cursor(access_token, cursor):
    item = Item.objects.get(access_token=access_token)
    item.last_transaction_update = cursor


def _create_transactions(transactions):
    for transaction in transactions:
        account = Account.objects.get(account_id=transaction["account_id"])
        new_transactions = Transactions(
            account_id=account,
            transaction_id=transaction["transaction_id"],
            amount=transaction["amount"],
            category_id=transaction["category_id"],
            category=",".join(transaction["category"]),
            pending=transaction["pending"],
            account_owner=transaction["account_owner"],
        )

        new_transactions.save()


def _delete_transactions(transactions):
    for transaction in transactions:
        Transactions.objects.filter(
            transaction_id=transaction["transaction_id"]).delete()


def _update_transactions(transactions):
    for transaction in transactions:
        account = Account.objects.get(account_id=transaction["account_id"])

        old_transaction = Transactions.objects.get(
            transaction_id=transaction["transaction_id"])

        if old_transaction is not None:
            old_transaction["amount"] = transaction["amount"]
            old_transaction["category_id"] = transaction["category_id"]
            old_transaction["category"] = ",".join(transaction["category"])
            old_transaction["pending"] = transaction["pending"]
            old_transaction = transaction["account_owner"]

            old_transaction.save()
        else:
            # This wont happen but still tho
            account = Account.objects.get(account_id=transaction["account_id"])
            new_transactions = Transactions(
                account_id=account,
                transaction_id=transaction["transaction_id"],
                amount=transaction["amount"],
                category_id=transaction["category_id"],
                category=",".join(transaction["category"]),
                pending=transaction["pending"],
                account_owner=transaction["account_owner"],
            )

            new_transactions.save()
