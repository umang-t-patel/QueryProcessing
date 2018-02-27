# Written by Umang Patel <umapatel@my.bridgeport.edu> and Jeongkyu Lee <jelee0408@gmail.com>, June 2017
# Updated by Umang Patel, July 2017
'''
This is the Demo 1 of the Project.
Demo 1 - Voice to Query which includes simple Queries with no feedback and no variations
demo1.exago - exago.py contains the modal to generate Text to Sql Queries and return the Data retrieved from Sql Database
'''
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from demo1.exago import getresults
def index(request):
	'''
	If the request method is GET then return the demo2.html
	If the request method is POST then process the Text to Sql queries.
	'''
	if request.method == 'POST':
		if request.POST['submit'] == 'Process Text':
			try:
				speech_text = request.POST['speech_text']
				feedback_text = request.POST['feedback_text']
				# Returning True in both the cases as there is no feedback in this application
				if feedback_text:
					speech_ret_text,output_value,output_feedback,feedback_text = getresults(speech_text.replace("'", ""), True)
				else:
					speech_ret_text,output_value,output_feedback,feedback_text = getresults(speech_text.replace("'", ""), True)
			except Exception as error:
				print(error)
				# If error then return empty values which in JavaSript converts to No Result Found
				speech_ret_text=output_value=output_feedback=feedback_text=""
			ret_dict={'ret_text':str(speech_ret_text),'output_value':output_value,'output_feedback':output_feedback,'feedback_text':feedback_text}
			return JsonResponse(ret_dict)
	else:
		test = []
		ret_dict={'test':test}
		return render(request,'demo1.html',context=ret_dict)
