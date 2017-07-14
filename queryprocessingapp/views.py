# Copyright (C) DomaniSystems, Inc. - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Umang Patel <umapatel@my.bridgeport.edu> and Jeongkyu Lee <jelee0408@gmail.com>, June 2017
# Updated by Umang Patel, July 2017
'''
This is the Home Page View of the Project
Also, NLTK data is stored in the this App Directory named as nltk_data.
'''
from django.shortcuts import render
def index(request):
	test = []
	ret_dict={'test':test}
	return render(request,'index.html',context=ret_dict)
