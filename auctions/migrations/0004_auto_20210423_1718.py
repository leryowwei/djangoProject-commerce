# Generated by Django 3.1.7 on 2021-04-23 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20210423_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='image',
            field=models.URLField(blank=True),
        ),
    ]