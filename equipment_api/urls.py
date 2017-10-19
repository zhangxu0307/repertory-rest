#encoding=utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    # 材料信息列表显示
    url(r'^equipment/$', views.EquipmentList.as_view(), name='equipment_list'),
    # 参数为材料ID号，查看材料详细信息，可进行修改和删除
    url(r'^equipment/(?P<pk>[0-9]+)/$', views.EquipmentDeatils.as_view(), name='equipment_detail'),
    # 有条件查找，暂定
    url(r'^equipment/search$', views.EquipmentSearch.as_view(), name='equipment_search'),
    # 入库信息列表显示
    url(r'^equipment/inputlist$', views.EquipmentInputList.as_view(), name='equipment_input_list'),
    # 参数为材料ID号，入库详细信息显示，可进行修改和删除
    url(r'^equipment_input_detail/(?P<pk>[0-9]+)/$', views.EquipmentInputDeatils.as_view(), name='equipment_input_detail'),
    # 入库操作，填写入库单
    url(r'^equipment_input/$', views.EquipmentInputOp.as_view(), name='equipment_input_OP'),
    # 出库信息列表显示
    url(r'^equipment/outputlist$', views.EquipmentOutputList.as_view(), name='equipment_output_list'),
    # 出库详细信息显示
    url(r'^equipment_output_detail/(?P<pk>[0-9]+)/$', views.EquipmentOutputDeatils.as_view(), name='equipment_output_detail'),
    # 出库操作，二维码扫入，填写出库单
    url(r'^equipment_output/$', views.EquipmentOutputOp1.as_view(), name='equipment_output_OP'),
    # 出库操作，页面中查找后出库
    #url(r'^equipment_output/$', views.EquipmentOutputOp2.as_view(), name='equipment_output_OP'),
    # 预测算法启动
    url(r'^forecasting_equipment/$', views.ForecastingEquipmentOutput.as_view(), name='forecasting'),
]