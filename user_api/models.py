# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser)
# Create your models here.


class CompanyUser(models.Model):

    user = models.OneToOneField(User, related_name="baseuser") # 用户与单位一对一绑定
    company = models.CharField(max_length=100, null=True, blank=True)
    tel = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    #
    # def __unicode__(self):
    #     return self.company
