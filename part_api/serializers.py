# -*- coding:utf-8 -*-

from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from .models import Part, PartInput, PartOutput
from django.db.models import Q


#-------------------------- 基本信息------------------------------

# 零件全信息序列化
class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        exclude = ("owner",) # 用户不显式出现
        #fields = "__all__"
        read_only_fields = ('partNum',) # 库存量只读，不能修改
        depth=1

    # 更新时确保零件标号唯一性
    def update(self, instance, validated_data):
        nowID = instance.partID
        updateID = validated_data["partID"]
        #print (nowID, updateID)
        user = validated_data["owner"]
        #print ("user",user)
        queryset = Part.objects.filter(owner=user)
        if (not queryset.filter(partID=updateID)) or updateID == nowID:

            instance.partID = validated_data.get('partID', instance.partID)
            instance.partType = validated_data.get('partType', instance.partType)
            instance.partStoreState = validated_data.get('partStoreState', instance.partStoreState)
            instance.partMark = validated_data.get('partMark', instance.partMark)
            #instance.partNum = validated_data.get('partNum', instance.partNum)
            instance.description = validated_data.get('description', instance.description)

            instance.partBand = validated_data.get('partBand', instance.partBand)
            instance.partOriginal = validated_data.get('partOriginal', instance.partOriginal)
            instance.partYear = validated_data.get('partYear', instance.partYear)
            instance.partState = validated_data.get('partState', instance.partState)
            instance.partPosition = validated_data.get('partPosition', instance.partPosition)
            instance.partUnit = validated_data.get('partUnit', instance.partUnit)

            instance.partName = validated_data.get('partName', instance.partName)
            instance.partCompany = validated_data.get('partCompany', instance.partCompany)
            instance.partMachineName = validated_data.get('partMachineName', instance.partMachineName)
            instance.partMachineType = validated_data.get('partMachineType', instance.partMachineType)
            instance.partMachineBand = validated_data.get('partMachineBand', instance.partMachineBand)
            instance.partCondition = validated_data.get('partCondition', instance.partCondition)
            instance.partVulnerability = validated_data.get('partVulnerability', instance.partVulnerability)


            instance.save()
            return instance
        else:
            raise serializers.ValidationError({"partID": "This ID has been used!"}) # 此处如何提示待定

    # 单位原值不能为负数
    def validate_partUnit(self, value):

        if value == None:
            return value

        if value < 0:
            raise serializers.ValidationError("Part Unit is negative!")
        return value

# ---------------------------- 入库信息与操作 ----------------------------

# 零件入库详细信息
class PartInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = PartInput
        exclude = ("inputPart",)
        #fields = "__all__"
        #depth = 1
        # 入库的数量只读，不能修改
        read_only_fields = ('inputNum',) # 入库信息中的库存品基本信息全部只读，修改只能通过库存品页面

# 以下是入库表单的序列化

# 除去库存量信息
class PartInputForm(serializers.ModelSerializer):
    class Meta:
        model = Part
        exclude = ('partNum', 'owner', 'company') # 入库单中库存品存量和用户不显示

    # 单位原值不能为负数
    def validate_partUnit(self, value):

        if value == None:
            return value
            #raise serializers.ValidationError("This field may not be blank.")

        if value < 0:
            raise serializers.ValidationError("Part Unit is negative!")
        return value

# 入库单信息序列化
class InputPartFormSerializer(serializers.ModelSerializer):

    inputPart = PartInputForm()
    class Meta:
        model = PartInput
        fields = "__all__"


    def create(self, validated_data):

        inputData = {}
        inputData['inputOperator'] = validated_data['inputOperator']
        inputData['inputNum'] = validated_data['inputNum']
        inputData["inputDateTime"] = validated_data["inputDateTime"]
        id = validated_data['inputPart']["partID"]
        user = validated_data["owner"]
        inputData["inputDescription"] = validated_data["inputDescription"]

        part = Part.objects.filter(Q(partID=id)&Q(owner=user)) # 必须用filter，get会报错
        flag = part
        if flag:
            part = Part.objects.get(Q(partID=id)&Q(owner=user))
            part.partNum += validated_data["inputNum"]
            part.save()
        else:
            partData = {}

            partData["partID"] = validated_data['inputPart']["partID"]
            partData["partType"] = validated_data['inputPart']["partType"]
            partData["partMark"] = validated_data['inputPart']["partMark"]
            partData["partStoreState"] = validated_data['inputPart']["partStoreState"]
            partData["description"] = validated_data['inputPart']["description"]
            partData["partNum"] = validated_data["inputNum"]

            partData["partBand"] = validated_data['inputPart']["partBand"]
            partData["partOriginal"] = validated_data['inputPart']["partOriginal"]
            partData["partYear"] = validated_data['inputPart']["partYear"]
            partData["partState"] = validated_data['inputPart']["partState"]
            partData["partPosition"] = validated_data['inputPart']["partPosition"]
            partData["partUnit"] = validated_data['inputPart']["partUnit"]

            partData["partName"] = validated_data['inputPart']['partName']
            partData["partCompany"] = validated_data['inputPart']['partCompany']
            partData["partMachineName"] = validated_data['inputPart']['partMachineName']
            partData["partMachineType"] = validated_data['inputPart']['partMachineType']
            partData["partMachineBand"] = validated_data['inputPart']['partMachineBand']
            partData["partCondition"] = validated_data['inputPart']['partCondition']
            partData["partVulnerability"] = validated_data['inputPart']['partVulnerability']

            partData["owner"] = validated_data["owner"]
            partData["company"] = validated_data["owner"].baseuser
            part = Part.objects.create(**partData)

        inputData['inputPart'] = part

        return PartInput.objects.create(**inputData)

    # 入库量不能为负数
    def validate_inputNum(self, value):

        if value < 0:
            raise serializers.ValidationError("Input Number is negative!")
        return value



# ------------------------ 出库信息与操作 --------------------------------

# 出库信息序列化
class PartOutputSerializer(serializers.ModelSerializer):

    class Meta:
        model = PartOutput
        exclude = ("outputPart",)
        #fields = "__all__"
        #depth = 1
        read_only_fields = ('outputNum', 'leftNum',) # 出库信息中的库存品基本信息全部只读，修改只能通过库存品页面

# 出库表单
class PartOutputForm(serializers.ModelSerializer):

    class Meta:
        model = Part
        #exclude = ("partNum", "owner")
        fields = ('partID', 'id')


# 零件出库信息序列化
# 零件出库信息序列化
class OutputPartSerializer(serializers.ModelSerializer):

    outputPart = PartOutputForm()
    class Meta:
        model = PartOutput
        fields = "__all__"
        read_only_fields = ("leftNum",)

    def create(self, validated_data):

        outputData = {}

        outputData['outputOperator'] = validated_data['outputOperator']
        outputData['outputNum'] = validated_data['outputNum']
        outputData["partUser"] = validated_data["partUser"]
        outputData["outputDateTime"] = validated_data["outputDateTime"]
        id = validated_data['outputPart']["partID"]
        user = validated_data["owner"]
        outputData["outputDescription"] = validated_data["outputDescription"]
        try:
            part = Part.objects.get(Q(partID=id)&Q(owner=user))
        except:
            raise serializers.ValidationError({"detail":"There is no such goods!"})
        #part = validated_data['outputPart']
        if part.partNum >= validated_data["outputNum"]:
            part.partNum -= validated_data["outputNum"]
            part.save()
            outputData['outputPart'] = part
            outputData['leftNum'] = part.partNum
            return PartOutput.objects.create(**outputData)
        else:
            raise serializers.ValidationError({"partNum": "Left Number is insufficient!"}) # 此处如何抛出异常待定

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





