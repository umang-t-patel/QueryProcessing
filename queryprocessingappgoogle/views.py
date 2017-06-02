from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests,json
pos_dict = {"ADJ": "adjective",
"ADP": "adposition",
"ADV": "adverb",
"AUX": "auxiliary verb",
"CONJ": "coordinating conjunction",
"DET": "determiner",
"INTJ": "interjection",
"NOUN": "noun",
"NUM": "numeral",
"PART": "particle",
"PRON": "pronoun",
"PROPN": "proper noun",
"PUNCT": "punctuation",
"SCONJ": "subordinating conjunction",
"SYM": "symbol",
"VERB": "verb",
"X": "other"}
googleapikey = 'https://language.googleapis.com/v1/documents:analyzeSyntax?fields=tokens&key=AIzaSyABnTrrsgCNLAqxMpdNOz9bNtFae9r7CZQ'
def index(request):
	if request.method == 'POST':
		if request.POST['submit'] == 'Process Text':
			speech_text = request.POST['speech_text']
			temp_speech_text = __generate_json(speech_text)
			# print(temp_speech_text)
			speech_ret_text = []
			for temp_ret_text in temp_speech_text:
				ret_text = {}
				for ret in temp_ret_text:
					temp_ret = temp_ret_text[ret]
					if ret == 'partOfSpeech':
						temp_pos = {}
						for pos in temp_ret:
							if 'UNKNOWN' not in temp_ret[pos]:
								temp_pos[pos] = temp_ret[pos]
								if pos == 'tag':
									temp_pos["Description"] = pos_dict[temp_ret[pos]]
						ret_text[ret] = temp_pos
					elif ret == 'dependencyEdge':
						ret_text[ret] = temp_ret
					elif ret == 'text':
						ret_text[ret] = temp_ret['content']
					elif ret == 'lemma':
						ret_text[ret] = temp_ret
				speech_ret_text.append(ret_text)
			ret_dict={'ret_text':speech_ret_text}
			return JsonResponse(ret_dict)
	else:
		test = []
		ret_dict={'test':test}
		return render(request,'google.html',context=ret_dict)

def __generate_json(text):
	data = {"content": text,"type": "PLAIN_TEXT"}
	request_document = {}
	request_document['document'] = data
	request_document['encodingType'] = "UTF32"
	response = requests.post(url = googleapikey,
		data = json.dumps(request_document),
		headers = {'Content-Type': 'application/json'})
	into = response.text
	if response.status_code != 200 or response.json().get('error'):
           resp = None
	else:
		resp = response.json()['tokens']
	return resp
