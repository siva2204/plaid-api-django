# Generated by Django 4.1.2 on 2022-10-28 06:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Item",
            fields=[
                (
                    "access_token",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("item_id", models.CharField(max_length=255)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Account",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("account_id", models.CharField(max_length=255)),
                ("name", models.CharField(max_length=255, null=True)),
                ("official_name", models.CharField(max_length=255, null=b"I01\n")),
                ("subtype", models.CharField(max_length=255, null=True)),
                ("type", models.CharField(max_length=255, null=True)),
                (
                    "access_token",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="api.item"
                    ),
                ),
            ],
        ),
    ]
