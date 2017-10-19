# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from user_api.models import CompanyUser


STATE_CHOICES = (("在用", "在用"), ("闲置可用", "闲置可用"), ("闲置可租", "闲置可租"), ("闲置可售", "闲置可售"))
#STATE_CHOICES = (("USING", "USING"), ("UNUSED", "UNUSED"), ("RENT", "RENT"), ("SELL", "SELL"))
class Material(models.Model):

    materialID = models.CharField("材料标号", max_length=100)
    materialType = models.CharField("材料类型", max_length=100, null=False, blank=True, default="")
    materialStoreState = models.CharField("材料库存状态", choices=STATE_CHOICES, default='闲置可用', max_length=100)
    materialMark = models.CharField("材料型号", max_length=100, null=False, blank=True, default="")
    materialNum = models.DecimalField("库存材料量", max_digits=8, decimal_places=2, default=0)

    materialBand = models.CharField("材料品牌", max_length=100, null=False, blank=True, default="")
    materialOriginal = models.CharField("材料原产地", max_length=100, null=False, blank=True, default="")
    materialYear = models.DateField("材料年份", null=True, blank=True)
    materialState = models.CharField("材料状态", max_length=100, null=False, blank=True, default="")
    materialPosition = models.CharField("材料位置", max_length=100, null=False, blank=True, default="")
    materialUnit = models.DecimalField("材料单位原值", max_digits=8, decimal_places=2, null=True, blank=True)

    description = models.TextField('备注', null=False, blank=True, default="")
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    company = models.ForeignKey(CompanyUser, null=True, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.materialID

class MaterialInput(models.Model):

    inputDateTime = models.DateField('入库时间')

    inputOperator = models.CharField('操作人员', max_length=100)
    inputNum = models.DecimalField("入库量", max_digits=8, decimal_places=2)
    inputMaterial = models.ForeignKey(Material, on_delete=models.CASCADE)
    inputDescription = models.TextField('入库备注', null=False, blank=True, default="")

    # def __unicode__(self):
    #     return self.name


class MaterialOutput(models.Model):

    outputDateTime = models.DateField('出库时间')
    materialUser = models.CharField("材料去向",  null=False, max_length=100)
    outputOperator = models.CharField('操作人员', max_length=100)
    leftNum = models.DecimalField("当前库存量", max_digits=8, decimal_places=2, null=True,)
    outputNum = models.DecimalField("出库量", max_digits=8, decimal_places=2)
    outputMaterial = models.ForeignKey(Material, on_delete=models.CASCADE)
    outputDescription = models.TextField('出库备注', null=False, blank=True, default="")


    # def __unicode__(self):
    #     return self.name

class ForecastingResult():

    def __init__(self, ansList, testY, predictTimeIndex, validTimeIndex, multiStepAnsList, multiStepAccList, oneStepAnsList, oneStepAccList, multiStepAcc, oneStepAcc):
        self.ansList = ansList
        self.testY = testY
        self.predictTimeIndex = predictTimeIndex
        self.validTimeIndex = validTimeIndex
        self.multiStepAccList = multiStepAccList
        self.multiStepAnsList = multiStepAnsList
        self.oneStepAnsList = oneStepAnsList
        self.oneStepAccList = oneStepAccList
        self.multiStepAcc = multiStepAcc
        self.oneStepAcc = oneStepAcc


admin.site.register([Material, MaterialInput, MaterialOutput])



