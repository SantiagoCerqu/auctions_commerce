# Generated by Django 4.1 on 2024-05-28 14:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0002_alter_category_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="listing",
            name="bid_amount",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
    ]
