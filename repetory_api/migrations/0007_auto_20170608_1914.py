# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-08 11:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repetory_api', '0006_auto_20170608_1751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='materialID',
            field=models.CharField(max_length=100, verbose_name='\u6750\u6599\u6807\u53f7'),
        ),
    ]
