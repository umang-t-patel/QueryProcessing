# Copyright (C) DomaniSystems, Inc. - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Umang Patel <umapatel@my.bridgeport.edu> and Jeongkyu Lee <jelee0408@gmail.com>, June 2017
# Updated by Umang Patel, July 2017
from django.conf.urls import url,include
from django.contrib import admin
from queryprocessingapp import views
from demo1 import views as viewsdemo1
from demo2 import views as viewsdemo2
from demo3 import views as viewsdemo3
'''
Create link between URL and Views in Django.
First URL is the default URL.
demo1 URL points to Demo 1
demo2 URL points to Demo 2
demo3 URL points to Demo 3
'''
urlpatterns = [
    url(r'^$',views.index),
    url(r'^demo1/',viewsdemo1.index),
    url(r'^demo2/',viewsdemo2.index),
    url(r'^demo3/',viewsdemo3.index),
    url(r'^admin/', admin.site.urls),
]
