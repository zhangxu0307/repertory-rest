# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from user_api.models import CompanyUser

STATE_CHOICES = (("在用", "在用"), ("闲置可用", "闲置可用"), ("闲置可租", "闲置可租"), ("闲置可售", "闲置可售"))
#STATE_CHOICES = (("USING", "USING"), ("UNUSED", "UNUSED"), ("RENT", "RENT"), ("SELL", "SELL"))

class Part(models.Model):

    partID = models.CharField("零件标号", max_length=100)
    partType = models.CharField("零件类型", max_length=100, null=False, blank=True, default="")
    partStoreState = models.CharField("零件库存状态", choices=STATE_CHOICES, default='闲置可用', max_length=100)
    partMark = models.CharField("零件型号", max_length=100, null=False, blank=True, default="")
    partNum = models.IntegerField("库存零件量", default=0)

    partBand = models.CharField("零件品牌", max_length=100, null=False, blank=True, default="")
    partOriginal = models.CharField("零件原产地", max_length=100, null=False, blank=True, default="")
    partYear = models.DateField("零件年份", null=True, blank=True)
    partState = models.CharField("零件状态", max_length=100, null=False, blank=True, default="")
    partPosition = models.CharField("零件位置", max_length=100, null=False, blank=True, default="")
    partUnit = models.DecimalField("零件单位原值", max_digits=8, decimal_places=2, null=True, blank=True)

    partName = models.CharField("零件名称", max_length=100, null=False, blank=True, default="")
    partCompany = models.CharField("零件制造企业", max_length=100, null=False, blank=True, default="")
    partMachineName = models.CharField("零件整机名称", max_length=100, null=False, blank=True, default="")
    partMachineType = models.CharField("零件整机型号", max_length=100, null=False, blank=True, default="")
    partMachineBand = models.CharField("零件整机品牌", max_length=100, null=False, blank=True, default="")
    partCondition = models.CharField("零件储存条件", max_length=100, null=False, blank=True, default="")
    partVulnerability = models.CharField("零件易损性", max_length=100, null=False, blank=True, default="")

    description = models.TextField('备注', null=False, blank=True, default="")
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    company = models.ForeignKey(CompanyUser, null=True, on_delete=models.CASCADE)


    def __unicode__(self):
        return self.partID

class PartInput(models.Model):

    inputDateTime = models.DateField('入库时间')

    inputOperator = models.CharField('操作人员', max_length=100)
    inputNum = models.IntegerField("入库量")
    inputPart = models.ForeignKey(Part, on_delete=models.CASCADE)
    inputDescription = models.TextField('入库备注', null=False, blank=True, default="")

    # def __unicode__(self):
    #     return self.name


class PartOutput(models.Model):

    outputDateTime = models.DateField('出库时间')
    partUser = models.CharField("零件去向",  null=False, max_length=100)
    outputOperator = models.CharField('操作人员', max_length=100)
    leftNum = models.IntegerField("当前库存量",  null=True,)
    outputNum = models.IntegerField("出库量",)
    outputPart = models.ForeignKey(Part, on_delete=models.CASCADE)
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




