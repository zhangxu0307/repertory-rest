# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-06 05:57
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('repetory_api', '0021_auto_20170705_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
