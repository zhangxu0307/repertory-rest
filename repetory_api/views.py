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
from repetory_api.permission import IsOwnerOrReadOnly, IsOwnerOrReadOnlyInput, IsOwnerOrReadOnlyOutput

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, time

from .models import Material, MaterialInput, MaterialOutput, ForecastingResult
from .serializers import MaterialSerializer, MaterialInputSerializer, MaterialOutputSerializer, \
    InputMaterialFormSerializer, OutputMaterialSerializer, ForecastingResultSerializer

# 材料信息全部显示
class MaterialList(generics.ListAPIView):

    serializer_class = MaterialSerializer

    def get_queryset(self):

        user = self.request.user
        if user.is_superuser == True: # 超级用户返回全部数据，下同
            queryset = Material.objects.all()
        else:
            #companyUser = user.baseuser # 一般用户返回本公司数据， 下同
            queryset = Material.objects.filter(owner=user)
        return queryset

# 查看某一型号材料详细信息，并做删除修改
class MaterialDeatils(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = MaterialSerializer
    lookup_field = ["pk",]

    permission_classes = (IsOwnerOrReadOnly,) # 只有创建者才可以做修改和删除权限，下同

    def get_object(self):

        user = self.request.user

        if user.is_superuser == True:
            queryset = Material.objects.all()
        else:
            #companyUser = user.baseuser
            queryset = Material.objects.filter(owner=user)
        filter = {}

        for field in self.lookup_field:
            filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)
        #self.check_object_permissions(self.request, obj)
        return obj

    def perform_update(self, serializer):
        user = self.request.user
        #companyUser = user.baseuser
        serializer.save(owner=user)

# 有条件查找材料
class MaterialSearch(generics.ListAPIView):

    serializer_class = MaterialSerializer

    def get_queryset(self):

        user = self.request.user
        if user.is_superuser == True:
            queryset = Material.objects.all()
        else:
            #companyUser = user.baseuser
            queryset = Material.objects.filter(owner=user)

        materialID = self.request.query_params.get('materialID', "")
        materialCompany = self.request.query_params.get('materialCompany', "")
        materialType = self.request.query_params.get('materialType', "")
        materialBand = self.request.query_params.get('materialBand', "")
        materialOriginal = self.request.query_params.get('materialOriginal', "")
        materialPosition = self.request.query_params.get('materialPosition', "")
        materialYearStart = self.request.query_params.get('materialYearstart', "")
        materialYearEnd = self.request.query_params.get('materialYearend', "")

        querysetList = []
        if materialID != "":
            queryset1 = queryset.filter(Q(materialID__icontains=materialID))
            querysetList.append(queryset1)
        if materialType != "":
            queryset2 = queryset.filter(Q(materialType__icontains=materialType))
            querysetList.append(queryset2)
        if materialOriginal != "":
            queryset3 = queryset.filter(Q(materialOriginal__icontains=materialOriginal))
            querysetList.append(queryset3)
        if materialBand != "":
            queryset4 = queryset.filter(Q(materialBand__icontains=materialBand))
            querysetList.append(queryset4)
        if materialPosition != "":
            queryset5 = queryset.filter(Q(materialPosition__icontains=materialPosition))
            querysetList.append(queryset5)
        if materialCompany != "":
            queryset6 = queryset.filter(Q(owner__baseuser__company__contains=materialCompany))
            querysetList.append(queryset6)

        if materialYearStart != "" or materialYearEnd != "":
            if materialYearStart == "":
                materialYearStart = "1800-01-01"
            if materialYearEnd == "":
                materialYearEnd = "3000-01-01"

            try:
                materialYearStart = datetime.strptime(materialYearStart, "%Y-%m-%d")
                materialYearEnd = datetime.strptime(materialYearEnd, "%Y-%m-%d")

            except:
                raise serializers.ValidationError({"detail": "Invalid time format!"})
            queryset6 = queryset.filter(Q(materialYear__range=(materialYearStart, materialYearEnd)))
            querysetList.append(queryset6)

        if len(querysetList) == 0:
            return queryset

        for index, querysetItem in enumerate(querysetList):
            if index == 0:
                ans = querysetItem
            else:
                ans &= querysetItem
                                   # #Q(materialName__icontains=materialName) |
                                   # Q(materialType__icontains=materialType) &
                                   # Q(materialOriginal__icontains=materialOriginal) &
                                   # Q(materialBand__icontains=materialBand) &
                                   # Q(materialPosition__icontains=materialPosition ) &
                                   # Q(materialYear__range=(materialYearStart, materialYearEnd))
                                   # )
        return ans

# 显示某一材料的所有入库列表
class MaterialInputList(generics.ListAPIView):

    serializer_class = MaterialInputSerializer

    def get_queryset(self):

        # 方法一：在目标表中直接查询的方式进行
        user = self.request.user
        if user.is_superuser == True:
            queryset = MaterialInput.objects.all()
        else:
            #companyUser = user.baseuser
            queryset = MaterialInput.objects.filter(inputMaterial__owner=user)
        #queryset = MaterialInput.objects.all()
        materialID = self.request.query_params.get('id', None)
        queryset = queryset.filter(inputMaterial__id=materialID)

        return queryset

        # 方法二：间接查找
        # materialID = self.request.query_params.get('materialID', None)
        # material = Material.objects.get(materialID=materialID)
        # queryset = material.materialinput_set.all() # 外键部分必须全部小写
        #
        # return queryset

# 显示某一条详细的入库信息, 按id查
class MaterialInputDeatils(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = MaterialInputSerializer
    queryset = MaterialInput.objects.all()
    lookup_field = ["pk"]
    permission_classes = (IsOwnerOrReadOnlyInput,) # 只有创建者拥有删除和修改权限

    def get_object(self):

        #queryset = self.get_queryset()
        user = self.request.user

        if user.is_superuser == True:
            queryset = MaterialInput.objects.all()
        else:
            #companyUser = user.baseuser
            queryset = MaterialInput.objects.filter(inputMaterial__owner=user)
        filter = {}

        for field in self.lookup_field:
            filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)
        #self.check_object_permissions(self.request, obj)
        return obj

    def delete(self, request, *args, **kwargs): # 删去一个入库操作，存库量相应变化

        instance = self.get_object()
        material = instance.inputMaterial
        material.materialNum -= instance.inputNum
        material.save()

        instance.delete()

# 入库操作
class MaterialInputOp(generics.CreateAPIView):

    serializer_class = InputMaterialFormSerializer
    permission_classes = (IsOwnerOrReadOnlyInput,)

    def perform_create(self, serializer):  # 拿到当前登录用户信息创建
        user = self.request.user
        #companyUser = user.baseuser
        serializer.save(owner=user)

# --------------------------------------

# 显示某一材料的所有概要出库列表
class MaterialOutputList(generics.ListAPIView):

    serializer_class = MaterialOutputSerializer

    def get_queryset(self):

        user = self.request.user
        if user.is_superuser == True:
            queryset = MaterialOutput.objects.all()
        else:
            #companyUser = user.baseuser
            queryset = MaterialOutput.objects.filter(outputMaterial__owner=user)
        materialID = self.request.query_params.get('id', None)
        queryset = queryset.filter(outputMaterial__id=materialID)
        return queryset

        # 方法二：间接查找
        # materialID = self.request.query_params.get('materialID', None)
        # material = Material.objects.get(materialID=materialID)
        # print material
        # queryset = material.materialoutput_set.all()  # 外键部分必须全部小写
        #
        # return queryset

# 显示某一条详细的出库信息, 按id查
class MaterialOutputDeatils(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = MaterialOutputSerializer
    queryset = MaterialOutput.objects.all()
    lookup_field = ["pk"]
    permission_classes = (IsOwnerOrReadOnlyOutput,) # 只有创建者拥有删除和修改权限

    def get_object(self):

        user = self.request.user

        if user.is_superuser == True:
            queryset = MaterialOutput.objects.all()
        else:
            #companyUser = user.baseuser
            queryset = MaterialOutput.objects.filter(outputMaterial__owner=user)
        filter = {}

        for field in self.lookup_field:
            filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)
        #self.check_object_permissions(self.request, obj)
        return obj

    def delete(self, request, *args, **kwargs): # 删去一个出库操作，存库量相应变化

        instance = self.get_object()
        material = instance.outputMaterial
        material.materialNum += instance.outputNum
        material.save()

        instance.delete()

# 出库操作, 二维码扫入出库信息
class MaterialOutputOp1(generics.CreateAPIView):

    serializer_class = OutputMaterialSerializer

    def get_queryset(self):
        user = self.request.user
        #companyUser = user.baseuser
        queryset = MaterialOutput.objects.filter(outputMaterial__owner=user)
        return queryset

    def perform_create(self, serializer):  # 拿到当前登录用户信息创建
        user = self.request.user
        #companyUser = user.baseuser
        serializer.save(owner=user)

# # 出库操作，手动先查找对应的物品再点击进行出库
# class MaterialOutputOp2(generics.CreateAPIView):
#
#     serializer_class = OutputMaterialSerializer

class ForecastingMaterialOutput(APIView):


    def get(self, request, format=None):

        user = self.request.user
        if user.is_superuser == True:
            queryset = MaterialOutput.objects.all()
        else:
            #companyUser = user.baseuser
            queryset = MaterialOutput.objects.filter(outputMaterial__owner=user)

        materialID = self.request.query_params.get('materialID', None)
        queryset = queryset.filter(outputMaterial__materialID=materialID)

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









