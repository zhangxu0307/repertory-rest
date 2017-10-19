# -*- coding:utf-8 -*-

from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from .models import Equipment, EquipmentInput, EquipmentOutput
from django.db.models import Q


#-------------------------- 基本信息------------------------------

# 整机全信息序列化
class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        exclude = ("owner",) # 用户不显式出现
        #fields = "__all__"
        read_only_fields = ('equipmentNum',) # 库存量只读，不能修改
        depth=1

    # 更新时确保整机标号唯一性
    def update(self, instance, validated_data):
        nowID = instance.equipmentID
        updateID = validated_data["equipmentID"]
        #print (nowID, updateID)
        user = validated_data["owner"]
        #print ("user",user)
        queryset = Equipment.objects.filter(owner=user)
        if (not queryset.filter(equipmentID=updateID)) or updateID == nowID:
            instance.equipmentID = validated_data.get('equipmentID', instance.equipmentID)
            instance.equipmentType = validated_data.get('equipmentType', instance.equipmentType)
            instance.equipmentStoreState = validated_data.get('equipmentStoreState', instance.equipmentStoreState)
            instance.equipmentMark = validated_data.get('equipmentMark', instance.equipmentMark)
            #instance.equipmentNum = validated_data.get('equipmentNum', instance.equipmentNum)
            instance.description = validated_data.get('description', instance.description)

            instance.equipmentBand = validated_data.get('equipmentBand', instance.equipmentBand)
            instance.equipmentOriginal = validated_data.get('equipmentOriginal', instance.equipmentOriginal)
            instance.equipmentYear = validated_data.get('equipmentYear', instance.equipmentYear)
            instance.equipmentState = validated_data.get('equipmentState', instance.equipmentState)
            instance.equipmentPosition = validated_data.get('equipmentPosition', instance.equipmentPosition)
            instance.equipmentUnit = validated_data.get('equipmentUnit', instance.equipmentUnit)

            instance.equipmentHour = validated_data.get('equipmentHour', instance.equipmentHour)


            instance.save()
            return instance
        else:
            raise serializers.ValidationError({"equipmentID": "This ID has been used!"}) # 此处如何提示待定

    # 单位原值不能为负数
    def validate_equipmentUnit(self, value):

        if value == None:
            return value

        if value < 0:
            raise serializers.ValidationError("equipment Unit is negative!")
        return value

    def validate_equipmentHour(self, value):

        if value == None:
            return value

        if value < 0:
            raise serializers.ValidationError("equipment Hour is negative!")
        return value

# ---------------------------- 入库信息与操作 ----------------------------

# 整机入库详细信息
class EquipmentInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = EquipmentInput
        # fields = "__all__"
        # depth = 1
        exclude = ("inputEquipment",)
        # 入库的数量只读，不能修改
        read_only_fields = ('inputNum',) # 入库信息中的库存品基本信息全部只读，修改只能通过库存品页面

# 以下是入库表单的序列化

# 除去库存量信息
class EquipmentInputForm(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        exclude = ('equipmentNum', 'owner', 'company') # 入库单中库存品存量和用户不显示

    # 单位原值不能为负数
    def validate_equipmentUnit(self, value):

        if value == None:
            return value
            #raise serializers.ValidationError("This field may not be blank.")

        if value < 0:
            raise serializers.ValidationError("equipment Unit is negative!")
        return value

    def validate_equipmentHour(self, value):

        if value == None:
            #raise serializers.ValidationError("This field may not be blank.")
            return value

        if value < 0:
            raise serializers.ValidationError("equipment Hour is negative!")
        return value


# 入库单信息序列化
class InputEquipmentFormSerializer(serializers.ModelSerializer):

    inputEquipment = EquipmentInputForm()
    class Meta:
        model = EquipmentInput
        fields = "__all__"


    def create(self, validated_data):

        inputData = {}
        inputData['inputOperator'] = validated_data['inputOperator']
        inputData['inputNum'] = validated_data['inputNum']
        inputData["inputDateTime"] = validated_data["inputDateTime"]
        id = validated_data['inputEquipment']["equipmentID"]
        user = validated_data["owner"]
        inputData["inputDescription"] = validated_data["inputDescription"]
        equipment = Equipment.objects.filter(Q(equipmentID=id)&Q(owner=user)) # 必须用filter，get会报错
        flag = equipment
        if flag:
            equipment = Equipment.objects.get(Q(equipmentID=id)&Q(owner=user))
            equipment.equipmentNum += validated_data["inputNum"]
            equipment.save()
        else:
            equipmentData = {}

            equipmentData["equipmentID"] = validated_data['inputEquipment']["equipmentID"]
            equipmentData["equipmentType"] = validated_data['inputEquipment']["equipmentType"]
            equipmentData["equipmentMark"] = validated_data['inputEquipment']["equipmentMark"]
            equipmentData["equipmentStoreState"] = validated_data['inputEquipment']["equipmentStoreState"]
            equipmentData["description"] = validated_data['inputEquipment']["description"]
            equipmentData["equipmentNum"] = validated_data["inputNum"]

            equipmentData["equipmentBand"] = validated_data['inputEquipment']["equipmentBand"]
            equipmentData["equipmentOriginal"] = validated_data['inputEquipment']["equipmentOriginal"]
            equipmentData["equipmentYear"] = validated_data['inputEquipment']["equipmentYear"]
            equipmentData["equipmentState"] = validated_data['inputEquipment']["equipmentState"]
            equipmentData["equipmentPosition"] = validated_data['inputEquipment']["equipmentPosition"]
            equipmentData["equipmentUnit"] = validated_data['inputEquipment']["equipmentUnit"]

            equipmentData["equipmentHour"] = validated_data['inputEquipment']["equipmentHour"]

            equipmentData["owner"] = validated_data["owner"]
            equipmentData["company"] = validated_data["owner"].baseuser
            equipment = Equipment.objects.create(**equipmentData)

        inputData['inputEquipment'] = equipment

        return EquipmentInput.objects.create(**inputData)

    # 入库量不能为负数
    def validate_inputNum(self, value):

        if value < 0:
            raise serializers.ValidationError("Input Number is negative!")
        return value





# ------------------------ 出库信息与操作 --------------------------------

# 出库信息序列化
class EquipmentOutputSerializer(serializers.ModelSerializer):

    class Meta:
        model = EquipmentOutput
        exclude = ("outputEquipment",)
        #fields = "__all__"
        #depth = 1
        read_only_fields = ( 'outputNum', 'leftNum', ) # 出库信息中的库存品基本信息全部只读，修改只能通过库存品页面

# 出库表单
class EquipmentOutputForm(serializers.ModelSerializer):

    class Meta:
        model = Equipment
        #exclude = ("equipmentNum", "owner")
        fields = ('equipmentID', 'id')


# 整机出库信息序列化
class OutputEquipmentSerializer(serializers.ModelSerializer):

    outputEquipment = EquipmentOutputForm()
    class Meta:
        model = EquipmentOutput
        fields = "__all__"
        read_only_fields = ("leftNum",)

    def create(self, validated_data):

        outputData = {}

        outputData['outputOperator'] = validated_data['outputOperator']
        outputData['outputNum'] = validated_data['outputNum']
        outputData["equipmentUser"] = validated_data["equipmentUser"]
        outputData["outputDateTime"] = validated_data["outputDateTime"]
        id = validated_data['outputEquipment']["equipmentID"]
        outputData["outputDescription"] = validated_data["outputDescription"]
        user = validated_data["owner"]
        try:
            equipment = Equipment.objects.get(Q(equipmentID=id)&Q(owner=user))
        except:
            raise serializers.ValidationError({"detail":"There is no such goods!"})
        #equipment = validated_data['outputequipment']
        if equipment.equipmentNum >= validated_data["outputNum"]:
            equipment.equipmentNum -= validated_data["outputNum"]
            equipment.save()
            outputData['outputEquipment'] = equipment
            outputData['leftNum'] = equipment.equipmentNum
            return EquipmentOutput.objects.create(**outputData)
        else:
            raise serializers.ValidationError({"equipmentNum": "Left Number is insufficient!"}) # 此处如何抛出异常待定

    def validate_outputNum(self, value):

        if value < 0:
            raise serializers.ValidationError("Output Number is negative!")
        return value



class ForecastingResultSerializer(serializers.Serializer):

    ansList = serializers.ListField(read_only=True, )
    testY = serializers.ListField(read_only=True, )
    predictTimeIndex = serializers.ListField(read_only=True, )
    validTimeIndex = serializers.ListField(read_only=True, )
    multiStepAccList = serializers.ListField(read_only=True, )
    multiStepAnsList = serializers.ListField(read_only=True, )
    oneStepAnsList = serializers.ListField(read_only=True, )
    oneStepAccList = serializers.ListField(read_only=True, )
    multiStepAcc = serializers.FloatField(read_only=True, )
    oneStepAcc = serializers.FloatField(read_only=True, )





