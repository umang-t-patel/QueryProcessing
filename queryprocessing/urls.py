from django.conf.urls import url,include
from django.contrib import admin
from queryprocessingapp import views
from queryprocessingappgoogle import views as viewsgoogle
from testqueryprocessing import views as viewstest

urlpatterns = [
    url(r'^$',views.index),
    url(r'^google/',viewsgoogle.index),
    url(r'^test/',viewstest.index),
    url(r'^admin/', admin.site.urls),
]
