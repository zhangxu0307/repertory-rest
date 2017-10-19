# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from user_api.models import CompanyUser


STATE_CHOICES = (("在用", "在用"), ("闲置可用", "闲置可用"), ("闲置可租", "闲置可租"), ("闲置可售", "闲置可售"))
#STATE_CHOICES = (("USING", "USING"), ("UNUSED", "UNUSED"), ("RENT", "RENT"), ("SELL", "SELL"))

class Equipment(models.Model):

    equipmentID = models.CharField("设备标号", max_length=100)
    equipmentType = models.CharField("设备类型", max_length=100, null=False, blank=True, default="")
    equipmentStoreState = models.CharField("设备库存状态", choices=STATE_CHOICES, default="闲置可用", max_length=100)
    equipmentMark = models.CharField("设备型号", max_length=100, null=False, blank=True, default="")
    equipmentNum = models.IntegerField("库存设备数量", default=0)

    equipmentHour = models.IntegerField("设备工作小时", null=True, blank=True, default=0)

    equipmentBand = models.CharField("设备品牌", max_length=100, null=False, blank=True, default="")
    equipmentOriginal = models.CharField("设备原产地", max_length=100, null=False, blank=True, default="")
    equipmentYear = models.DateField("设备年份", null=True, blank=True,)
    equipmentState = models.CharField("设备状态", max_length=100, null=False, blank=True, default="")
    equipmentPosition = models.CharField("设备位置", max_length=100, null=False, blank=True, default="")
    equipmentUnit = models.DecimalField("设备单位原值", max_digits=8, decimal_places=2, null=True, blank=True)

    description = models.TextField('备注', null=False, blank=True, default="")
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    company = models.ForeignKey(CompanyUser, null=True, on_delete=models.CASCADE)


    def __unicode__(self):
        return self.equipmentID

class EquipmentInput(models.Model):

    inputDateTime = models.DateField('入库时间')

    inputOperator = models.CharField('操作人员', max_length=100)
    inputNum = models.IntegerField("入库量")
    inputEquipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    inputDescription = models.TextField('入库备注', null=False, blank=True, default="")

    # def __unicode__(self):
    #     return self.name


class EquipmentOutput(models.Model):

    outputDateTime = models.DateField('出库时间')
    equipmentUser = models.CharField("设备去向",  null=False, max_length=100)
    outputOperator = models.CharField('操作人员', max_length=100)
    leftNum = models.IntegerField("当前库存量", null=True,)
    outputNum = models.IntegerField("出库量")
    outputEquipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
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



