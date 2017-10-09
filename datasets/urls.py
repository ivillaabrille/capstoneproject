from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from datasets import views

app_name= 'datasets'

urlpatterns = [
    # /
    url(r'^$', views.IndexView, name='index'),

    # /signup
    url(r'^signup/$', views.signup, name='signup'),

    # /signin
    url(r'^signin/$', views.signin, name='signin'),

    # /signout
    url(r'^signout/$', views.signout, name='signout'),

    # /api-endpoint/datasets/
    url(r'^api-endpoint/datasets/$', views.DataSetList.as_view(), name='datasets'),

    # /data/
    url(r'^data/$', views.DataView.as_view(), name='data'),

    # /data/1/
    url(r'^data/(?P<pk>[0-9]+)/$', views.DataDetailView, name='datadetail'),

    # /data/1/adddata
    url(r'^data/(?P<pk>[0-9]+)/adddata/$', views.AddDataView, name='adddata'),

    # /mydata/
    url(r'^mydata/$', views.MyDataView, name='mydata'),

    # /newdata/
    url(r'^newdata/$', views.NewDataView, name='newdata'),

    # /newdata2/
    url(r'^newdata2/(?P<number>[0-9]+)/$', views.NewData2View, name='newdata2'),

    # /about/
    url(r'^about/$', views.AboutView, name='about'),


    # # /data/1/getcsv/
    # url(r'^data/(?P<pk>[0-9]+)/getcsv/$', views.GetCsvView.as_view(), name='getcsv'),
    #
    # # /data/1/getjson/
    # url(r'^data/(?P<pk>[0-9]+)/getjson/$', views.GetJsonView.as_view(), name='getjson'),

]

urlpatterns = format_suffix_patterns(urlpatterns)