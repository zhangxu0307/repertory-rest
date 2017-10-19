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

from .models import Part, PartInput, PartOutput, ForecastingResult
from .serializers import PartSerializer, PartInputSerializer, PartOutputSerializer, \
    InputPartFormSerializer, OutputPartSerializer, ForecastingResultSerializer

# 零件信息列表展示
class PartList(generics.ListAPIView):

    serializer_class = PartSerializer
    queryset = Part.objects.all()

    def get_queryset(self):

        user = self.request.user
        if user.is_superuser == True:  # 超级用户返回全部数据，下同
            queryset = Part.objects.all()
        else:
            # companyUser = user.baseuser # 一般用户返回本公司数据， 下同
            queryset = Part.objects.filter(owner=user)
        return queryset

# 查看某一型号零件详细信息，并做删除修改
class PartDeatils(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = PartSerializer
    lookup_field = ["pk",]

    def get_object(self):

        user = self.request.user
        if user.is_superuser == True:
            queryset = Part.objects.all()
        else:
            queryset = Part.objects.filter(owner=user)
        filter = {}

        for field in self.lookup_field:
            filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)
        #self.check_object_permissions(self.request, obj)
        return obj

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)


# 有条件查找零件
class PartSearch(generics.ListAPIView):

    serializer_class = PartSerializer

    def get_queryset(self):

        user = self.request.user
        if user.is_superuser == True:
            queryset = Part.objects.all()
        else:
            queryset = Part.objects.filter(owner=user)

        partID = self.request.query_params.get('partID', "")
        #partName = self.request.query_params.get('partName', " ")
        partCompany = self.request.query_params.get('partCompany', "")
        partType = self.request.query_params.get('partType', "")
        partBand = self.request.query_params.get('partBand', "")
        partOriginal = self.request.query_params.get('partOriginal', "")
        partPosition = self.request.query_params.get('partPosition', "")
        partYearStart = self.request.query_params.get('partYearstart', "1800-01-01")
        partYearEnd = self.request.query_params.get('partYearend', "3000-01-01")


        querysetList = []
        if partID != "":
            queryset1 = queryset.filter(Q(partID__icontains=partID))
            querysetList.append(queryset1)
        if partType != "":
            queryset2 = queryset.filter(Q(partType__icontains=partType))
            querysetList.append(queryset2)
        if partOriginal != "":
            queryset3 = queryset.filter(Q(partOriginal__icontains=partOriginal))
            querysetList.append(queryset3)
        if partBand != "":
            queryset4 = queryset.filter(Q(partBand__icontains=partBand))
            querysetList.append(queryset4)
        if partPosition != "":
            queryset5 = queryset.filter(Q(partPosition__icontains=partPosition))
            querysetList.append(queryset5)
        if partCompany  != "":
            queryset6 = queryset.filter(Q(owner__baseuser__company__contains=partCompany))
            querysetList.append(queryset6)
        if partYearStart != "" or partYearEnd != "":
            if partYearStart == "":
                partYearStart = "1800-01-01"
            if partYearEnd == "":
                partYearEnd = "3000-01-01"

            try:
                partYearStart = datetime.strptime(partYearStart, "%Y-%m-%d")
                partYearEnd = datetime.strptime(partYearEnd, "%Y-%m-%d")

            except:
                raise serializers.ValidationError({"detail": "Invalid time format!"})
            queryset6 = queryset.filter(Q(partYear__range=(partYearStart, partYearEnd)))
            querysetList.append(queryset6)

        if len(querysetList) == 0:
            return queryset

        for index, querysetItem in enumerate(querysetList):
            if index == 0:
                ans = querysetItem
            else:
                ans &= querysetItem
                                   # #Q(partName__icontains=partName) |
                                   # Q(partType__icontains=partType) &
                                   # Q(partOriginal__icontains=partOriginal) &
                                   # Q(partBand__icontains=partBand) &
                                   # Q(partPosition__icontains=partPosition ) &
                                   # Q(partYear__range=(partYearStart, partYearEnd))
                                   # )
        return ans

# 显示某一零件的所有入库列表
class PartInputList(generics.ListAPIView):

    serializer_class = PartInputSerializer

    def get_queryset(self):

        # 方法一：在目标表中直接查询的方式进行
        user = self.request.user
        if user.is_superuser == True:
            queryset = PartInput.objects.all()
        else:
            queryset = PartInput.objects.filter(inputPart__owner=user)
        #queryset = PartInput.objects.all()
        partID = self.request.query_params.get('id', None)
        queryset = queryset.filter(inputPart__id=partID)
        return queryset

        # 方法二：间接查找
        # partID = self.request.query_params.get('partID', None)
        # part = Part.objects.get(partID=partID)
        # queryset = part.partinput_set.all() # 外键部分必须全部小写
        #
        # return queryset

# 显示某一条详细的入库信息, 按id查
class PartInputDeatils(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = PartInputSerializer
    queryset = PartInput.objects.all()
    lookup_field = ["pk"]

    def get_object(self):

        #queryset = self.get_queryset()
        user = self.request.user
        if user.is_superuser == True:
            queryset = PartInput.objects.all()
        else:
            queryset = PartInput.objects.filter(inputPart__owner=user)
        filter = {}

        for field in self.lookup_field:
            filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)
        #self.check_object_permissions(self.request, obj)
        return obj

    def delete(self, request, *args, **kwargs): # 删去一个入库操作，存库量相应变化

        instance = self.get_object()
        part = instance.inputPart
        part.partNum -= instance.inputNum
        part.save()

        instance.delete()

# 入库操作
class PartInputOp(generics.CreateAPIView):

    serializer_class = InputPartFormSerializer

    def perform_create(self, serializer):  # 拿到当前登录用户信息创建
        serializer.save(owner=self.request.user)

# --------------------------------------

# 显示某一零件的所有概要出库列表
class PartOutputList(generics.ListAPIView):

    serializer_class = PartOutputSerializer

    def get_queryset(self):

        user = self.request.user
        if user.is_superuser == True:
            queryset = PartOutput.objects.all()
        else:
            queryset = PartOutput.objects.filter(outputPart__owner=user)
        partID = self.request.query_params.get('id', None)
        queryset = queryset.filter(outputPart__id=partID)
        return queryset

        # 方法二：间接查找
        # partID = self.request.query_params.get('partID', None)
        # part = Part.objects.get(partID=partID)
        # print part
        # queryset = part.partoutput_set.all()  # 外键部分必须全部小写
        #
        # return queryset

# 显示某一条详细的出库信息, 按id查
class PartOutputDeatils(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = PartOutputSerializer
    queryset = PartOutput.objects.all()
    lookup_field = ["pk"]

    def get_object(self):

        user = self.request.user
        if user.is_superuser == True:
            queryset = PartOutput.objects.all()
        else:
            queryset = PartOutput.objects.filter(outputPart__owner=user)
        filter = {}

        for field in self.lookup_field:
            filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)
        #self.check_object_permissions(self.request, obj)
        return obj

    def delete(self, request, *args, **kwargs): # 删去一个出库操作，存库量相应变化

        instance = self.get_object()
        part = instance.outputPart
        part.partNum += instance.outputNum
        part.save()

        instance.delete()

# 出库操作, 二维码扫入出库信息
class PartOutputOp1(generics.CreateAPIView):

    serializer_class = OutputPartSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = PartOutput.objects.filter(outputPart__owner=user)
        return queryset

    def perform_create(self, serializer):  # 拿到当前登录用户信息创建
        serializer.save(owner=self.request.user)

# # 出库操作，手动先查找对应的物品再点击进行出库
# class PartOutputOp2(generics.CreateAPIView):
#
#     serializer_class = OutputPartSerializer

class ForecastingPartOutput(APIView):


    def get(self, request, format=None):

        user = self.request.user
        if user.is_superuser == True:
            queryset = PartOutput.objects.all()
        else:
            # companyUser = user.baseuser
            queryset = PartOutput.objects.filter(outputMaterial__owner=user)

        partID = self.request.query_params.get('partID', None)
        queryset = queryset.filter(outputPart__partID=partID)

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








