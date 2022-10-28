from asyncio.windows_events import NULL
from pickle import TRUE
from unicodedata import category
from django.db import models
from django.contrib.auth.models import User
import uuid


class Item(models.Model):
    """Item class defines the an Plaid Item, stores access_token(primary key), item_id and user_id"""

    """User can have many Items, therefore User is one - many related to Item"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    access_token = models.CharField(
        max_length=255, primary_key=True)  # primary key
    item_id = models.CharField(max_length=255)
    last_transaction_update = models.CharField(
        max_length=255, default=NULL, null=True)


class Account(models.Model):
    """Accounts defines an Plaid accound asscociated with an Item"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    access_token = models.ForeignKey(
        "Item", on_delete=models.CASCADE, null=False)
    account_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True)
    official_name = models.CharField(max_length=255, null=TRUE)
    current_balance = models.FloatField(null=True)
    available_balance = models.FloatField(null=True)
    subtype = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=255, null=True)


class Transactions(models):
    """Transactions Holds all the transactions details associated with an *Item*"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    account_id = models.ForeignKey(
        "Account", on_delete=models.CASCADE, null=False)
    transaction_id = models.CharField(max_length=255, unique=True, null=False)
    amount = models.FloatField(null=True)
    category_id = models.CharField(max_length=255, null=True)
    category = models.CharField(max_length=255, null=True)
    pending = models.BooleanField(null=True)
    account_owner = models.CharField(max_length=255, null=True)
