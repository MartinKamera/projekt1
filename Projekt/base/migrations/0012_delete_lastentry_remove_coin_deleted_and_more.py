# Generated by Django 5.2 on 2025-06-06 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_rename_last_updated_coin_updated_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LastEntry',
        ),
        migrations.RemoveField(
            model_name='coin',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='portfolio',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='pricehistory',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='deleted',
        ),
        migrations.AlterField(
            model_name='coin',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
