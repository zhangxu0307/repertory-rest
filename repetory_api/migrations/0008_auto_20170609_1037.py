# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-09 02:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repetory_api', '0007_auto_20170608_1914'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='materialName',
        ),
        migrations.AddField(
            model_name='material',
            name='materailYear',
            field=models.DateTimeField(blank=True, null=True, verbose_name='\u6750\u6599\u5e74\u4efd'),
        ),
        migrations.AddField(
            model_name='material',
            name='materialBand',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u6750\u6599\u54c1\u724c'),
        ),
        migrations.AddField(
            model_name='material',
            name='materialMark',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u6750\u6599\u578b\u53f7'),
        ),
        migrations.AddField(
            model_name='material',
            name='materialOriginal',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u6750\u6599\u539f\u4ea7\u5730'),
        ),
        migrations.AddField(
            model_name='material',
            name='materialPostion',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u6750\u6599\u4f4d\u7f6e'),
        ),
        migrations.AddField(
            model_name='material',
            name='materialState',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u6750\u6599\u72b6\u6001'),
        ),
        migrations.AddField(
            model_name='material',
            name='materialStoreState',
            field=models.CharField(choices=[('USING', '\u5728\u7528'), ('UNUSED', '\u95f2\u7f6e\u53ef\u7528'), ('RENT', '\u95f2\u7f6e\u53ef\u79df'), ('SELL', '\u95f2\u7f6e\u53ef\u552e')], default='UNUSED', max_length=100, verbose_name='\u6750\u6599\u5e93\u5b58\u72b6\u6001'),
        ),
        migrations.AddField(
            model_name='material',
            name='materialType',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u6750\u6599\u7c7b\u578b'),
        ),
        migrations.AddField(
            model_name='material',
            name='matrialUnit',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=8, verbose_name='\u6750\u6599\u5355\u4f4d\u539f\u503c'),
        ),
        migrations.AlterField(
            model_name='material',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='\u5907\u6ce8'),
        ),
        migrations.AlterField(
            model_name='material',
            name='materialID',
            field=models.CharField(max_length=100, unique=True, verbose_name='\u6750\u6599\u6807\u53f7'),
        ),
        migrations.AlterField(
            model_name='material',
            name='materialNum',
            field=models.DecimalField(decimal_places=4, max_digits=8, verbose_name='\u5e93\u5b58\u6750\u6599\u91cf'),
        ),
    ]
