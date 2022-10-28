from operator import truediv
from pickle import TRUE
from django.db import models
from django.contrib.auth.models import User
import uuid
# Create your models here.


class Item(models.Model):
    """Item class defines the an Plaid Item, stores access_token(primary key), item_id and user_id"""

    """User can have many Items, therefore User is one - many related to Item"""
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=False)
    access_token = models.CharField(
        max_length=255, primary_key=True)  # primary key
    item_id = models.CharField(max_length=255)


class Account(models.Model):
    """Accounts defines an Plaid accound asscociated with an Item"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    access_token = models.ForeignKey(
        "Item", on_delete=models.PROTECT, null=False)
    account_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255, null=True)
    official_name = models.CharField(max_length=255, null=TRUE)
    subtype = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=255, null=True)


# class Transactions(models):
#     pass
