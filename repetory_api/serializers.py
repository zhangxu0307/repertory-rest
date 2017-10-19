# -*- coding:utf-8 -*-

from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from .models import Material, MaterialInput, MaterialOutput
from django.db.models import Q


#-------------------------- 基本信息------------------------------

# 材料全信息序列化
class MaterialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Material
        exclude = ("owner",) # 用户不显式出现
        #fields = "__all__"
        read_only_fields = ('materialNum',) # 库存量只读，不能修改
        depth = 1

    # 更新时确保材料标号唯一性
    def update(self, instance, validated_data):
        nowID = instance.materialID
        updateID = validated_data["materialID"]
        #print (nowID, updateID)
        user = validated_data["owner"]
        #print ("user",user)
        queryset = Material.objects.filter(owner=user)
        if (not queryset.filter(materialID=updateID)) or updateID == nowID:
            instance.materialID = validated_data.get('materialID', instance.materialID)
            instance.materialType = validated_data.get('materialType', instance.materialType)
            instance.materialStoreState = validated_data.get('materialStoreState', instance.materialStoreState)
            instance.materialMark = validated_data.get('materialMark', instance.materialMark)
            #instance.materialNum = validated_data.get('materialNum', instance.materialNum)
            instance.description = validated_data.get('description', instance.description)

            instance.materialBand = validated_data.get('materialBand', instance.materialBand)
            instance.materialOriginal = validated_data.get('materialOriginal', instance.materialOriginal)
            instance.materialYear = validated_data.get('materialYear', instance.materialYear)
            instance.materialState = validated_data.get('materialState', instance.materialState)
            instance.materialPosition = validated_data.get('materialPosition', instance.materialPosition)
            instance.materialUnit = validated_data.get('materialUnit', instance.materialUnit)

            instance.save()
            return instance
        else:
            raise serializers.ValidationError({"materialID": "This ID has been used!"}) # 此处如何提示待定

    # 单位原值不能为负数
    def validate_materialUnit(self, value):

        if value == None:
            return value

        if value < 0:
            raise serializers.ValidationError("Material Unit is negative!")
        return value

# ---------------------------- 入库信息与操作 ----------------------------

# 材料入库详细信息
class MaterialInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = MaterialInput
        exclude = ("inputMaterial",)

        #fields = "__all__"
        #depth = 1
        # 入库的数量只读，不能修改
        read_only_fields = ('inputNum',) # 入库信息中的库存品基本信息全部只读，修改只能通过库存品页面

# 以下是入库表单的序列化

# 除去库存量信息
class MaterialInputForm(serializers.ModelSerializer):
    class Meta:
        model = Material
        exclude = ('materialNum', 'owner', 'company') # 入库单中库存品存量和用户不显示

    # 单位原值不能为负数
    def validate_materialUnit(self, value):

        if value == None:
            return value
            #raise serializers.ValidationError("This field may not be blank.")

        if value < 0:
            raise serializers.ValidationError("Material Unit is negative!")
        return value
# 入库单信息序列化
class InputMaterialFormSerializer(serializers.ModelSerializer):

    inputMaterial = MaterialInputForm()
    class Meta:
        model = MaterialInput
        fields = "__all__"


    def create(self, validated_data):

        inputData = {}
        inputData['inputOperator'] = validated_data['inputOperator']
        inputData['inputNum'] = validated_data['inputNum']
        inputData["inputDateTime"] = validated_data["inputDateTime"]
        id = validated_data['inputMaterial']["materialID"]
        user = validated_data["owner"]
        inputData["inputDescription"] = validated_data["inputDescription"]


        material = Material.objects.filter(Q(materialID=id)&Q(owner=user)) # 必须用filter，get会报错
        flag = material
        if flag:
            material = Material.objects.get(Q(materialID=id)&Q(owner=user))
            material.materialNum += validated_data["inputNum"]
            material.save()
        else:
            materialData = {}

            materialData["materialID"] = validated_data['inputMaterial']["materialID"]
            materialData["materialType"] = validated_data['inputMaterial']["materialType"]
            materialData["materialMark"] = validated_data['inputMaterial']["materialMark"]
            materialData["materialStoreState"] = validated_data['inputMaterial']["materialStoreState"]
            materialData["description"] = validated_data['inputMaterial']["description"]
            materialData["materialNum"] = validated_data["inputNum"]

            materialData["materialBand"] = validated_data['inputMaterial']["materialBand"]
            materialData["materialOriginal"] = validated_data['inputMaterial']["materialOriginal"]
            materialData["materialYear"] = validated_data['inputMaterial']["materialYear"]
            materialData["materialState"] = validated_data['inputMaterial']["materialState"]
            materialData["materialPosition"] = validated_data['inputMaterial']["materialPosition"]
            materialData["materialUnit"] = validated_data['inputMaterial']["materialUnit"]

            materialData["owner"] = validated_data["owner"]
            materialData["company"] = validated_data["owner"].baseuser
            material = Material.objects.create(**materialData)

        inputData['inputMaterial'] = material

        return MaterialInput.objects.create(**inputData)

    # 入库量不能为负数
    def validate_inputNum(self, value):

        if value < 0:
            raise serializers.ValidationError("Input Number is negative!")
        return value

# ------------------------ 出库信息与操作 --------------------------------

# 出库信息序列化
class MaterialOutputSerializer(serializers.ModelSerializer):

    class Meta:
        model = MaterialOutput
        exclude = ("outputMaterial",)
        #fields = "__all__"
        #depth = 1
        read_only_fields = ( 'outputNum', 'leftNum', ) # 出库信息中的库存品基本信息全部只读，修改只能通过库存品页面

# 出库表单
class MaterialOutputForm(serializers.ModelSerializer):

    class Meta:
        model = Material
        #exclude = ("materialNum", "owner")
        fields = ('materialID',  'id')


# 材料出库信息序列化
class OutputMaterialSerializer(serializers.ModelSerializer):

    outputMaterial = MaterialOutputForm()
    class Meta:
        model = MaterialOutput
        fields = "__all__"
        read_only_fields = ("leftNum",)

    def create(self, validated_data):

        outputData = {}

        outputData['outputOperator'] = validated_data['outputOperator']
        outputData['outputNum'] = validated_data['outputNum']
        outputData["materialUser"] = validated_data["materialUser"]
        outputData["outputDateTime"] = validated_data["outputDateTime"]
        id = validated_data['outputMaterial']["materialID"]
        user = validated_data["owner"]
        outputData["outputDescription"] = validated_data["outputDescription"]
        try:
            material = Material.objects.get(Q(materialID=id)&Q(owner=user))
        except:
            raise serializers.ValidationError({"detail":"There is no such goods!"})
        #material = validated_data['outputMaterial']
        if material.materialNum >= validated_data["outputNum"]:
            material.materialNum -= validated_data["outputNum"]
            material.save()
            outputData['outputMaterial'] = material
            outputData['leftNum'] = material.materialNum
            return MaterialOutput.objects.create(**outputData)
        else:
            raise serializers.ValidationError({"materialNum": "Left Number is insufficient!"}) # 此处如何抛出异常待定

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





