# Generated by Django 4.1.2 on 2022-10-28 15:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="available_balance",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="account",
            name="current_balance",
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name="item",
            name="last_transaction_update",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="account",
            name="access_token",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="api.item"
            ),
        ),
        migrations.AlterField(
            model_name="account",
            name="account_id",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="account",
            name="official_name",
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="item",
            name="item_id",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="item",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.CreateModel(
            name="Transactions",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("transaction_id", models.CharField(max_length=255, unique=True)),
                ("amount", models.FloatField(null=True)),
                ("category_id", models.CharField(max_length=255, null=True)),
                ("category", models.CharField(max_length=255, null=True)),
                ("pending", models.BooleanField(null=True)),
                ("account_owner", models.CharField(max_length=255, null=True)),
                (
                    "account_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="api.account"
                    ),
                ),
            ],
        ),
    ]