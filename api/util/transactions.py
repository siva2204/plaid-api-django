from sqlite3 import Cursor
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from api.models import Account, Item, Transactions
from ..plaid_client import plaid_client as client
from ..logger import log
from django.db import transaction as atomic_transaction


def get_transactions_updates(item_id, initial_update_complete):
    added = []
    modified = []
    removed = []

    has_more = True  # for pagination logic
    cursor = None
    item = Item.objects.get(item_id=item_id)

    if initial_update_complete:  # if initial transaction pull is done, last cursor is updated to fetch new transactions
        cursor = item.last_transaction_update

    request = None

    if cursor is None:
        request = TransactionsSyncRequest(
            access_token=item.access_token,
        )

    if cursor != None:
        request = TransactionsSyncRequest(
            access_token=item.access_token,
            cursor=cursor
        )

    response = client.transactions_sync(request)

    added.extend(response["added"])
    modified.extend(response["modified"])
    removed.extend(response["removed"])

    has_more = response["has_more"]
    cursor = response["next_cursor"]

    while has_more:

        request = TransactionsSyncRequest(
            access_token=item.access_token,
            cursor=cursor
        )
        response = client.transactions_sync(request)

        added.extend(response["added"])
        modified.extend(response["modified"])
        removed.extend(response["removed"])

        has_more = response["has_more"]
        cursor = response["next_cursor"]
    log.info(f"transaction_sync data fetched for {item_id}")
    return added, modified, removed, item.access_token, cursor


def update_transactions(item_id, initial_update_complete):
    response = get_transactions_updates(
        item_id=item_id, initial_update_complete=initial_update_complete)

    added = response[0]
    modified = response[1]
    removed = response[2]
    access_token = response[3]
    cursor = response[4]

    with atomic_transaction.atomic():  # starting transaction here
        already_added_tn = _create_transactions(added)
        log.debug("successful tn creation")

        modified.extend(already_added_tn)
        _delete_transactions(removed)
        log.debug("successful tn deletion")

        _update_transactions(modified)
        log.debug("successful tn updation")

        _update_cursor(access_token=access_token, cursor=cursor)
        log.debug("cursor updated")
    raise Exception("update_transactions rolled back, did not commit")


def _update_cursor(access_token, cursor):
    item = Item.objects.get(access_token=access_token)
    item.last_transaction_update = cursor
    item.save()


def _create_transactions(transactions):
    modified = []  # To avoid duplicate entry in sandbox mode
    for transaction in transactions:
        """In sandbox mode some transaction_id are repeating or i.e duplicated row is there"""
        """if the transaction_id is already present we can move that to modified list"""

        if Transactions.objects.filter(transaction_id=transaction["transaction_id"]).exists():
            modified.append(transaction)
            continue

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
    return modified


def _delete_transactions(transactions):
    for transaction in transactions:
        Transactions.objects.filter(
            transaction_id=transaction["transaction_id"]).delete()


def _update_transactions(transactions):
    for transaction in transactions:

        old_transaction = Transactions.objects.get(
            transaction_id=transaction["transaction_id"])

        old_transaction.amount = transaction["amount"]
        old_transaction.category_id = transaction["category_id"]
        old_transaction.category = ",".join(transaction["category"])
        old_transaction.pending = transaction["pending"]
        old_transaction.account_owner = transaction["account_owner"]

        old_transaction.save()
