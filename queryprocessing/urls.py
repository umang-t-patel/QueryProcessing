from django.conf.urls import url,include
from django.contrib import admin
from queryprocessingapp import views
from queryprocessingappgoogle import views as viewsgoogle

urlpatterns = [
    url(r'^$',views.index),
    url(r'^google/',viewsgoogle.index),
    url(r'^admin/', admin.site.urls),
]
