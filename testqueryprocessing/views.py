from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from testqueryprocessing.exago import getresults
def index(request):
	if request.method == 'POST':
		if request.POST['submit'] == 'Process Text':
			speech_text = request.POST['speech_text']
			speech_ret_text,output_value = getresults(speech_text)
			ret_dict={'ret_text':speech_ret_text,'output_value':output_value}
			return JsonResponse(ret_dict)
	else:
		test = []
		ret_dict={'test':test}
		return render(request,'test.html',context=ret_dict)
