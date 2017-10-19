#encoding=utf-8
from django.conf.urls import url
from . import views

urlpatterns = [
    # 材料信息列表显示
    url(r'^part/$', views.PartList.as_view(), name='part_list'),
    # 参数为材料ID号，查看材料详细信息，可进行修改和删除
    url(r'^part/(?P<pk>[0-9]+)/$', views.PartDeatils.as_view(), name='part_detail'),
    # 有条件查找，暂定
    url(r'^part/search$', views.PartSearch.as_view(), name='part_search'),
    # 入库信息列表显示
    url(r'^part/inputlist$', views.PartInputList.as_view(), name='part_input_list'),
    # 参数为材料ID号，入库详细信息显示，可进行修改和删除
    url(r'^part_input_detail/(?P<pk>[0-9]+)/$', views.PartInputDeatils.as_view(), name='part_input_detail'),
    # 入库操作，填写入库单
    url(r'^part_input/$', views.PartInputOp.as_view(), name='part_input_OP'),
    # 出库信息列表显示
    url(r'^part/outputlist$', views.PartOutputList.as_view(), name='part_output_list'),
    # 出库详细信息显示
    url(r'^part_output_detail/(?P<pk>[0-9]+)/$', views.PartOutputDeatils.as_view(), name='part_output_detail'),
    # 出库操作，二维码扫入，填写出库单
    url(r'^part_output/$', views.PartOutputOp1.as_view(), name='part_output_OP'),
    # 出库操作，页面中查找后出库
    #url(r'^part_output/$', views.PartOutputOp2.as_view(), name='part_output_OP'),
    # 预测算法启动
    url(r'^forecasting_part/$', views.ForecastingPartOutput.as_view(), name='forecasting'),
]