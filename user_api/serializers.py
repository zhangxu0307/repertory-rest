# -*- coding:utf-8 -*-

from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from .models import CompanyUser


class CompanyUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompanyUser
        fields = "__all__"
        depth = 1




