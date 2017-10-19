# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import generics
from django.shortcuts import render
from .models import CompanyUser
from .serializers import CompanyUserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework import serializers


# Create your views here.

# 创建用户详细信息
class CreateUserDeatilInfo(generics.CreateAPIView):

    queryset = CompanyUser.objects.all()
    serializer_class = CompanyUserSerializer

    def perform_create(self, serializer): # 拿到当前登录用户信息创建公司用户
        try:
            serializer.save(user=self.request.user)
        except:
            raise serializers.ValidationError({"detail": "This User Detail Info has been existed!"})
            #return Response({"details": "This User Detail Info has existed!"})


# 显示用户详细信息并可以做修改
class UserDisplay(generics.RetrieveUpdateAPIView):

    serializer_class = CompanyUserSerializer

    def get_object(self):

        user = self.request.user
        queryset = CompanyUser.objects.filter(user=user)
        obj = get_object_or_404(queryset, user=user)

        return obj



