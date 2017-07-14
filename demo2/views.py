# Copyright (C) DomaniSystems, Inc. - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Umang Patel <umapatel@my.bridgeport.edu> and Jeongkyu Lee <jelee0408@gmail.com>, June 2017
# Updated by Umang Patel, July 2017
'''
This is the Demo 2 of the Project.
Demo 2 - Voice to Query which includes simple Queries with feedback and one variations of each query
demo1.exago - ../demo1/exago.py contains the modal to generate Text to Sql Queries and return the Data retrieved from Sql Database
'''
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from demo1.exago import getresults
def index(request):
	'''
	If the request method is GET then return the demo2.html
	If the request method is POST then process the Text to Sql queries with feedback if required
	'''
	if request.method == 'POST':
		try:
			if request.POST['submit'] == 'Process Text':
				speech_text = request.POST['speech_text']
				feedback_text = request.POST['feedback_text']
				feedback_exists = False
				# If requires feedback from the user then Send False, if not then True.
				if feedback_text:
					# If user response yes to feedback question then send True for Text processing or else return empty values.
					if feedback_text != 'yes':
						speech_ret_text = output_value = output_feedback = feedback_text = ""
					else:
						speech_ret_text,output_value,output_feedback,feedback_text = getresults(speech_text.replace("'", ""), True)
				else:
					speech_ret_text,output_value,output_feedback,feedback_text = getresults(speech_text.replace("'", ""), False)
		except Exception as error:
			print(error)
			# If error then return empty values which in JavaSript converts to No Result Found
			speech_ret_text=output_value=output_feedback=feedback_text=""
		ret_dict={'ret_text':str(speech_ret_text),'output_value':output_value,'output_feedback':output_feedback,'feedback_text':feedback_text}
		return JsonResponse(ret_dict)
	else:
		test = []
		ret_dict={'test':test}
		return render(request,'demo2.html',context=ret_dict)
