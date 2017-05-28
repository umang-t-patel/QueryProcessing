from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from queryprocessingapp import texttoquery as ttq
# Create your views here.
def index(request):
	if request.method == 'POST':
		if request.POST['submit'] == 'Process Text':
			speech_text = request.POST['speech_text']
			ret_text = ttq.texttoquery(speech_text)
			ret_dict={'ret_text':ret_text}
			return JsonResponse(ret_dict)
	else:
		test = []
		ret_dict={'test':test}
		return render(request,'index.html',context=ret_dict)
