#encoding=utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    # 材料信息列表显示
    url(r'^material/$', views.MaterialList.as_view(), name='material_list'),
    # 参数为材料ID号，查看材料详细信息，可进行修改和删除 (?P<materialID>.+)
    url(r'^material/(?P<pk>[0-9]+)/$', views.MaterialDeatils.as_view(), name='material_detail'),
    # 有条件查找，暂定
    url(r'^material/search$', views.MaterialSearch.as_view(), name='material_search'),
    # 入库信息列表显示
    url(r'^material/inputlist$', views.MaterialInputList.as_view(), name='material_input_list'),
    # 参数为材料ID号，入库详细信息显示，可进行修改和删除
    url(r'^material_input_detail/(?P<pk>[0-9]+)/$', views.MaterialInputDeatils.as_view(), name='material_input_detail'),
    # 入库操作，填写入库单
    url(r'^material_input/$', views.MaterialInputOp.as_view(), name='material_input_OP'),
    # 出库信息列表显示
    url(r'^material/outputlist$', views.MaterialOutputList.as_view(), name='material_output_list'),
    # 出库详细信息显示
    url(r'^material_output_detail/(?P<pk>[0-9]+)/$', views.MaterialOutputDeatils.as_view(), name='material_output_detail'),
    # 出库操作，二维码扫入，填写出库单
    url(r'^material_output/$', views.MaterialOutputOp1.as_view(), name='material_output_OP'),
    # 出库操作，页面中查找后出库
    #url(r'^material_output/$', views.MaterialOutputOp2.as_view(), name='material_output_OP'),
    # 预测算法启动
    url(r'^forecasting_material/$', views.ForecastingMaterialOutput.as_view(), name='forecasting'),
]