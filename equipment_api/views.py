# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
import django_filters.rest_framework
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q
from forecasting_algorithm.algorithm import forecasting, evaluate, evaluate_onestep
from rest_framework import serializers

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time

from .models import Equipment, EquipmentInput, EquipmentOutput, ForecastingResult
from .serializers import EquipmentSerializer, EquipmentInputSerializer, EquipmentOutputSerializer, \
    InputEquipmentFormSerializer, OutputEquipmentSerializer, ForecastingResultSerializer

# 整机信息列表展示
class EquipmentList(generics.ListAPIView):

    serializer_class = EquipmentSerializer
    queryset = Equipment.objects.all()

    def get_queryset(self):

        user = self.request.user
        if user.is_superuser == True:  # 超级用户返回全部数据，下同
            queryset = Equipment.objects.all()
        else:
            # companyUser = user.baseuser # 一般用户返回本公司数据， 下同
            queryset = Equipment.objects.filter(owner=user)
        return queryset

# 查看某一型号整机详细信息，并做删除修改
class EquipmentDeatils(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = EquipmentSerializer
    lookup_field = ["pk"]

    def get_object(self):

        user = self.request.user
        if user.is_superuser == True:
            queryset = Equipment.objects.all()
        else:
            # companyUser = user.baseuser
            queryset = Equipment.objects.filter(owner=user)
        filter = {}

        for field in self.lookup_field:
            filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)
        #self.check_object_permissions(self.request, obj)
        return obj

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)


# 有条件查找整机
class EquipmentSearch(generics.ListAPIView):

    serializer_class = EquipmentSerializer

    def get_queryset(self):

        user = self.request.user
        if user.is_superuser == True:
            queryset = Equipment.objects.all()
        else:
            # companyUser = user.baseuser
            queryset = Equipment.objects.filter(owner=user)

        equipmentID = self.request.query_params.get('equipmentID', "")
        #equipmentName = self.request.query_params.get('equipmentName', " ")
        equipmentCompany = self.request.query_params.get('equipmentCompany', "")
        equipmentType = self.request.query_params.get('equipmentType', "")
        equipmentBand = self.request.query_params.get('equipmentBand', "")
        equipmentOriginal = self.request.query_params.get('equipmentOriginal', "")
        equipmentPosition = self.request.query_params.get('equipmentPosition', "")
        equipmentYearStart = self.request.query_params.get('equipmentYearstart', "1800-01-01")
        equipmentYearEnd = self.request.query_params.get('equipmentYearend', "3000-01-01")


        querysetList = []
        if equipmentID != "":
            queryset1 = queryset.filter(Q(equipmentID__icontains=equipmentID))
            querysetList.append(queryset1)
        if equipmentType != "":
            queryset2 = queryset.filter(Q(equipmentType__icontains=equipmentType))
            querysetList.append(queryset2)
        if equipmentOriginal != "":
            queryset3 = queryset.filter(Q(equipmentOriginal__icontains=equipmentOriginal))
            querysetList.append(queryset3)
        if equipmentBand != "":
            queryset4 = queryset.filter(Q(equipmentBand__icontains=equipmentBand))
            querysetList.append(queryset4)
        if equipmentPosition != "":
            queryset5 = queryset.filter(Q(equipmentPosition__icontains=equipmentPosition))
            querysetList.append(queryset5)
        if equipmentCompany != "":
            queryset6 = queryset.filter(Q(owner__baseuser__company__contains=equipmentCompany))
            querysetList.append(queryset6)

        if equipmentYearStart != "" or equipmentYearEnd != "":
            if equipmentYearStart == "":
                equipmentYearStart = "1800-01-01"
            if equipmentYearEnd == "":
                equipmentYearEnd = "3000-01-01"
            #print (equipmentYearStart, equipmentYearEnd)

            try:
                equipmentYearStart = datetime.strptime(equipmentYearStart, "%Y-%m-%d")
                equipmentYearEnd = datetime.strptime(equipmentYearEnd, "%Y-%m-%d")

            except:
                raise serializers.ValidationError({"detail": "Invalid time format!"})
            queryset6 = queryset.filter(Q(equipmentYear__range=(equipmentYearStart, equipmentYearEnd)))
            querysetList.append(queryset6)

        if len(querysetList) == 0:
            return queryset

        for index, querysetItem in enumerate(querysetList):
            if index == 0:
                ans = querysetItem
            else:
                ans &= querysetItem
                                   # #Q(equipmentName__icontains=equipmentName) |
                                   # Q(equipmentType__icontains=equipmentType) &
                                   # Q(equipmentOriginal__icontains=equipmentOriginal) &
                                   # Q(equipmentBand__icontains=equipmentBand) &
                                   # Q(equipmentPosition__icontains=equipmentPosition ) &
                                   # Q(equipmentYear__range=(equipmentYearStart, equipmentYearEnd))
                                   # )
        return ans

# 显示某一整机的所有入库列表
class EquipmentInputList(generics.ListAPIView):

    serializer_class = EquipmentInputSerializer

    def get_queryset(self):

        # 方法一：在目标表中直接查询的方式进行
        user = self.request.user
        if user.is_superuser == True:
            queryset = EquipmentInput.objects.all()
        else:
            # companyUser = user.baseuser
            queryset = EquipmentInput.objects.filter(inputEquipment__owner=user)
        #queryset = equipmentInput.objects.all()
        equipmentID = self.request.query_params.get('id', None)
        queryset = queryset.filter(inputEquipment__id=equipmentID)

        return queryset

        # 方法二：间接查找
        # equipmentID = self.request.query_params.get('equipmentID', None)
        # equipment = equipment.objects.get(equipmentID=equipmentID)
        # queryset = equipment.equipmentinput_set.all() # 外键部分必须全部小写
        #
        # return queryset

# 显示某一条详细的入库信息, 按id查
class EquipmentInputDeatils(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = EquipmentInputSerializer
    queryset = EquipmentInput.objects.all()
    lookup_field = ["pk"]

    def get_object(self):

        user = self.request.user
        if user.is_superuser == True:
            queryset = EquipmentInput.objects.all()
        else:
            # companyUser = user.baseuser
            queryset = EquipmentInput.objects.filter(inputEquipment__owner=user)
        filter = {}

        for field in self.lookup_field:
            filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)
        #self.check_object_permissions(self.request, obj)
        return obj

    def delete(self, request, *args, **kwargs): # 删去一个入库操作，存库量相应变化

        instance = self.get_object()
        equipment = instance.inputEquipment
        equipment.equipmentNum -= instance.inputNum
        equipment.save()

        instance.delete()

# 入库操作
class EquipmentInputOp(generics.CreateAPIView):

    serializer_class = InputEquipmentFormSerializer

    def perform_create(self, serializer):  # 拿到当前登录用户信息创建
        serializer.save(owner=self.request.user)

# --------------------------------------

# 显示某一整机的所有概要出库列表
class EquipmentOutputList(generics.ListAPIView):

    serializer_class = EquipmentOutputSerializer

    def get_queryset(self):

        user = self.request.user
        if user.is_superuser == True:
            queryset = EquipmentOutput.objects.all()
        else:
            # companyUser = user.baseuser
            queryset = EquipmentOutput.objects.filter(outputEquipment__owner=user)
        equipmentID = self.request.query_params.get('id', None)
        queryset = queryset.filter(outputEquipment__id=equipmentID)
        return queryset

        # 方法二：间接查找
        # equipmentID = self.request.query_params.get('equipmentID', None)
        # equipment = equipment.objects.get(equipmentID=equipmentID)
        # print equipment
        # queryset = equipment.equipmentoutput_set.all()  # 外键部分必须全部小写
        #
        # return queryset

# 显示某一条详细的出库信息, 按id查
class EquipmentOutputDeatils(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = EquipmentOutputSerializer
    queryset = EquipmentOutput.objects.all()
    lookup_field = ["pk"]

    def get_object(self):

        user = self.request.user
        if user.is_superuser == True:
            queryset = EquipmentOutput.objects.all()
        else:
            # companyUser = user.baseuser
            queryset = EquipmentOutput.objects.filter(outputEquipment__owner=user)
        filter = {}

        for field in self.lookup_field:
            filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)
        #self.check_object_permissions(self.request, obj)
        return obj

    def delete(self, request, *args, **kwargs): # 删去一个出库操作，存库量相应变化

        instance = self.get_object()
        equipment = instance.outputequipment
        equipment.equipmentNum += instance.outputNum
        equipment.save()

        instance.delete()

# 出库操作, 二维码扫入出库信息
class EquipmentOutputOp1(generics.CreateAPIView):

    serializer_class = OutputEquipmentSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = EquipmentOutput.objects.filter(outputEquipment__owner=user)
        return queryset

    def perform_create(self, serializer):  # 拿到当前登录用户信息创建
        serializer.save(owner=self.request.user)

# # 出库操作，手动先查找对应的物品再点击进行出库
# class equipmentOutputOp2(generics.CreateAPIView):
#
#     serializer_class = OutputequipmentSerializer

class ForecastingEquipmentOutput(APIView):


    def get(self, request, format=None):

        user = self.request.user
        if user.is_superuser == True:
            queryset = EquipmentOutput.objects.all()
        else:
            # companyUser = user.baseuser
            queryset = EquipmentOutput.objects.filter(outputEquipment__owner=user)
        equipmentID = self.request.query_params.get('equipmentID', None)
        queryset = queryset.filter(outputEquipment__equipmentID=equipmentID)

        if len(queryset) == 0:
            return  Response({"details": "no such goods or no output data!"}) # 查无此物

        stepAhead = int(float(request.query_params.get('stepAhead', 1)))
        lag = int(float(request.query_params.get('lag', 5)))
        timeInterval = int(float(request.query_params.get('timeInterval', 1)))

        # 参数限制
        if stepAhead < 0:
            return Response({"details":"step ahead must be posistive!"})
        if stepAhead > 20:
            return Response({"details": "step ahead is too large!"})
        if lag < 5:
            return Response({"details": "lag is too low!"})
        if lag > 20:
            return Response({"details": "lag is too high!"})
        if timeInterval != 1 and timeInterval != 0:
            return Response({"details": "time interval value must be 0 or 1!"})

        dataSet = pd.DataFrame(list(queryset.values("outputDateTime", "outputNum")))
        print (dataSet)
        print (stepAhead, lag)

        dataSet.index = pd.to_datetime(dataSet["outputDateTime"])  # 设置时间索引，方便resample
        print (timeInterval)

        if timeInterval == 0:
            dataSet = dataSet.resample('1D')["outputNum"].sum()  # 天采样
        else:
            dataSet = dataSet.resample('1M')["outputNum"].sum()  # 月采样
        print (dataSet)

        # 获取时间索引
        timeIndex = dataSet.index
        if timeInterval == 0:
            validTimeIndex = [str(x)[:10] for x in timeIndex.values[-stepAhead:]]
            lastTimeIndex = datetime.strptime(validTimeIndex[-1], '%Y-%m-%d')
        else:
            validTimeIndex = [str(x)[:7] for x in timeIndex.values[-stepAhead:]]
            lastTimeIndex = datetime.strptime(validTimeIndex[-1], '%Y-%m')

        # 外推时间索引
        predictTimeIndex = []
        tmp = lastTimeIndex
        for i in range(1, stepAhead+1):
            if timeInterval == 1: # 按月加
                import dateutil
                tmp = tmp + dateutil.relativedelta.relativedelta(months=1)
                predictTimeIndex.append(tmp.strftime('%Y-%m'))
            else: # 按天加
                tmp = tmp + timedelta(days=1)
                predictTimeIndex.append(tmp.strftime('%Y-%m-%d'))


        ts = dataSet.values
        ts = ts.astype(np.float64) # 转换数据类型，decimal转化为float64
        if len(ts) < 50: # 数据长度限制
            return Response({"details": "time series is too short!"})
        testY, evalans, accList, accMean = evaluate(ts, lag, stepAhead)
        testY, evalans_1, accList_1, accMean_1 = evaluate_onestep(ts, lag, stepAhead)
        ans = forecasting(ts, lag, stepAhead)
        ans = ans[0] # 此处是一个嵌套list

        forecastingRes = ForecastingResult(ans, testY, predictTimeIndex, validTimeIndex,
                                           evalans, accList,evalans_1, accList_1, accMean, accMean_1)

        serializer = ForecastingResultSerializer(forecastingRes)

        return Response(serializer.data)









