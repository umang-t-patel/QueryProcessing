import requests,json,re,itertools,nltk
import testqueryprocessing.data as exago_data
from nltk.corpus import wordnet
from django.conf import settings
googleapikey = 'https://language.googleapis.com/v1/documents:annotateText?fields=entities(name%2Ctype)%2Ctokens&key=AIzaSyABnTrrsgCNLAqxMpdNOz9bNtFae9r7CZQ'
sessionurl = 'http://exagosupport.com:85/Exago/NLP_REST_API/WebServiceApi/Rest/Sessions'
queryurl = 'http://exagosupport.com:85/Exago/NLP_REST_API/WebServiceApi/Rest/Reports/execute/csv?sid={0}'
header = {'Content-Type': 'application/json','Accept': 'application/json','Authorization': 'Basic Og=='}
entities_type = {}
def googlettsapi(text):
    data = {"content": text,"type": "PLAIN_TEXT"}
    request_document = {}
    request_document['document'] = data
    request_document['encodingType'] = "UTF32"
    request_document['features'] = { "extractEntities": True, "extractSyntax": True }
    response = requests.post(url = googleapikey,
    	data = json.dumps(request_document),
    	headers = {'Content-Type': 'application/json'})
    global entities_type
    entities_type = response.json()['entities']
    temp_speech_text = response.json()['tokens']
    speech_ret_text = []
    print('Removing Determiner')
    for temp_ret_text in temp_speech_text:
        ret_text = {}
        if temp_ret_text['partOfSpeech']['tag'] != 'DET':
            for ret in temp_ret_text:
                temp_ret = temp_ret_text[ret]
                if ret == 'partOfSpeech':
                    temp_pos = {}
                    for pos in temp_ret:
                        if 'UNKNOWN' not in temp_ret[pos]:
                            temp_pos[pos] = temp_ret[pos]
                            if pos == 'tag':
                                temp_pos["Description"] = exago_data.pos_dict[temp_ret[pos]]
                    ret_text[ret] = temp_pos
                elif ret == 'dependencyEdge':
                    ret_text[ret] = temp_ret
                elif ret == 'text':
                    ret_text[ret] = temp_ret['content']
                elif ret == 'lemma':
                    ret_text[ret] = temp_ret
            speech_ret_text.append(ret_text)
    return speech_ret_text
def createsession():
    response = requests.post(url = sessionurl,
    	headers = header)
    return response.json()['Id']
def getdata(raw_data):
    session_id = createsession()
    url = (queryurl).format(session_id)
    data = generatedata(raw_data)
    response = requests.post(url = url,
    	data = json.dumps(data),
    	headers = header)
    return response.json()
def generatedata(data):
    send_data = {"DisplayField": data["DisplayField"],"AggMethod": data["AggMethod"]}
    temp_data = []
    for filters in data["Filters"]:
        temp_filters = {"EntityName": filters["EntityName"], "ColumnName": filters["ColumnName"], "Operator": filters["Operator"], "Values": filters["Values"]}
        temp_data.append(temp_filters)
    send_data["Filters"] = temp_data
    return send_data
def performNLP(google_output):
    print('Seprating Noun and Non-nouns')
    print('Noun')
    result_text_not_noun = [text['text'] for text in google_output if text['partOfSpeech']['tag'] != 'NOUN']
    print('Non-Noun')
    result_text_noun = [text['text'] for text in google_output if text['partOfSpeech']['tag'] == 'NOUN']

    print('Getting List of Table Name')
    table_data = [key for key, value in exago_data.table_data.items()]
    print('Perform Similarity for Table Name')
    table_output = performsimilarity(result_text_noun,table_data)
    attr_data = []
    print('Getting List of Attributes')
    attr_data = itertools.chain.from_iterable(exago_data.table_data.values())

    print('Perform Similarity for Attributes')
    attr_output = performsimilarity(result_text_noun,attr_data)

    print('Getting List of Aggregation Data')
    agg_data = [key for key, value in exago_data.agg_data.items()]
    print('Getting Similarity of Aggregation Data')
    agg_output = performsimilarity(result_text_not_noun,agg_data)

    print('Getting List of Opertional Data')
    opr_data = [key for key, value in exago_data.operator_data.items()]
    print('Getting Similarity of Opertional Data')
    opr_output = performsimilarity(result_text_not_noun,opr_data)

    print('table output:',table_output)
    print('Attributes output:',attr_output)
    print('Aggregation output:',agg_output)
    print('Opertional output:',opr_output)
    get_data = "Error"
    try:
        send_data = {"DisplayField": exago_data.mapped_data[table_output[2]]+"."+attr_output[2],"AggMethod": 6}
        temp_data = [{"EntityName": exago_data.mapped_data[table_output[2]], "ColumnName": "LastName", "Operator": 0, "Values": [ table_output[1], "null" ]}]
        send_data["Filters"] = temp_data
        get_data = getdata(send_data)["ExecuteData"]
    except:
        pass
    return get_data
def performsimilarity(input_list, data_list):
    url = settings.NLTK_DIR
    nltk.data.path.append(url)
    output_list = []
    global entities_type
    for input_word in input_list:
        for data_word in data_list:
            wordFrominput_list = wordnet.synsets(input_word)
            wordFromdata_list = wordnet.synsets(data_word)
            if wordFrominput_list and wordFromdata_list:
                for wordfromdata in wordFromdata_list:
                    s = wordFrominput_list[0].wup_similarity(wordfromdata)
                    if s == None:
                        s = 0.0
                    output_list.append([s, input_word, data_word])
            elif [dic_entity['type'] for dic_entity in entities_type if input_word in dic_entity.values()]:
                entity_type = [dic_entity['type'] for dic_entity in entities_type if input_word in dic_entity.values()]
                wordFrominput_list = wordnet.synsets(entity_type[0])
                wordFromdata_list = wordnet.synsets(data_word)
                if wordFrominput_list and wordFromdata_list:
                    for wordfromdata in wordFromdata_list:
                        s = wordFrominput_list[0].wup_similarity(wordfromdata)
                        if s == None:
                            s = 0.0
                        output_list.append([s, input_word, data_word])
    return max(output_list)
def getresults(text):
    print('Get Results from Google NLP')
    google_output = googlettsapi(text)
    print('Passing Results from Google NLP to perform NLP')
    nlp_output = performNLP(google_output)
    return google_output,nlp_output
