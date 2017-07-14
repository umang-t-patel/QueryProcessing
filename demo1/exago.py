# Copyright (C) DomaniSystems, Inc. - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Umang Patel <umapatel@my.bridgeport.edu> and Jeongkyu Lee <jelee0408@gmail.com>, June 2017
# Updated by Umang Patel, July 2017
import requests,json,re,itertools,nltk,math
from datetime import datetime
from dateutil.relativedelta import relativedelta
import demo1.data as exago_data
from nltk.corpus import wordnet
from django.conf import settings
import numpy as np
# Google API call with key.
googleapikey = 'https://language.googleapis.com/v1/documents:annotateText?fields=entities(name%2Ctype)%2Ctokens&key=AIzaSyABnTrrsgCNLAqxMpdNOz9bNtFae9r7CZQ'
# Exago API initiation call for Creating Session
sessionurl = 'http://52.89.147.247/ExagoWebApi/Rest/Sessions'
# Get data from the SQL database.
queryurl = 'http://52.89.147.247/ExagoWebApi/Rest/Reports/execute/csv?sid={0}'
header = {'Content-Type': 'application/json','Accept': 'application/json','Authorization': 'Basic Og=='}
entities_type = {}
json_data_to_send = {}
def googlettsapi(text):
    '''
    This function gets the input from user in form of text.
    Using Google Speech Language API extract important entities and also get Part of Speech information on the Input text.
    First call to Google API to get the Nouns from the list of word. Once the noun is identified.
    Capitalize it to get the important entities.
    Second call to Google API with the Capitalized text.
    Once get the POS information then create Dictionary to process it.
    Args:
        text(string) - User input.
    Returns:
        Dictionary - With important entities and POS information.
    '''
    # Printing the Input text
    print('Input: ',text)
    temp_text = text.title()
    data = {"content": temp_text,"type": "PLAIN_TEXT"}
    request_document = {}
    request_document['document'] = data
    request_document['encodingType'] = "UTF32"
    request_document['features'] = { "extractEntities": True, "extractSyntax": True }
    # First API call to get important entities
    response = requests.post(url = googleapikey,
    	data = json.dumps(request_document),
    	headers = {'Content-Type': 'application/json'})
    global entities_type
    entities_type = response.json()['entities']
    temp_speech_text = response.json()['tokens']
    # Identify the important entities and capitalize it.
    for ent_type in entities_type:
        if ent_type['type'] == 'PERSON':
            text = text.replace(ent_type['name'].lower(),ent_type['name'])
        else:
            temp_speech_text = [element for element in temp_speech_text if element.get('lemma', '') != ent_type['name']]
    for temp_resp in temp_speech_text:
        if temp_resp['partOfSpeech']['tag'] == 'NOUN' and temp_resp['partOfSpeech']['number'] == 'SINGULAR' and temp_resp['partOfSpeech']['proper'] == 'PROPER' and temp_resp['dependencyEdge']['label'] != 'NN' and temp_resp['dependencyEdge']['label'] != 'DEP':
            text = text.replace(temp_resp['lemma'].lower(),temp_resp['lemma'])
    # New input with the capitalize entities
    print('New Input: ',text)
    data = {"content": text,"type": "PLAIN_TEXT"}
    request_document = {}
    request_document['document'] = data
    request_document['encodingType'] = "UTF32"
    request_document['features'] = { "extractEntities": True, "extractSyntax": True }
    # Second call to Google API for extracting POS information
    response = requests.post(url = googleapikey,
    	data = json.dumps(request_document),
    	headers = {'Content-Type': 'application/json'})
    entities_type = response.json()['entities']
    temp_speech_text = response.json()['tokens']
    speech_ret_text = []
    # After getting the POS information filter it to remove stop words
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
    '''
    This function to create session with database API and get session id for further API calls
    Args:
        None
    Returns:
        Session ID - String
    '''
    response = requests.post(url = sessionurl,
    	headers = header)
    return response.json()['Id']
def getdata(raw_data):
    '''
    This function is to get the data from the database using the JSON data created using Text to SQL algorithm.
    Args:
        raw_data (dictionary) - JSON data created using algorithm
    Returns:
        Output(String) - Returned output from database API
    '''
    session_id = createsession()
    url = (queryurl).format(session_id)
    response = requests.post(url = url,
    	data = json.dumps(raw_data),
    	headers = header)
    return response.json()
def generatejson(json_data):
    '''
    This function is to generate JSON using the data generated using the Text to SQL algorithm.
    Sample JSON data -
    {
    'DisplayField': 'TableName.ColumnName', 'AggMethod': Aggregation_data,
    'Filters': [{'Values': ['Values', 'null'], 'EntityName': 'TableName', 'ColumnName': 'ColumnName', 'Operator': Operator_data}],
    'Sorts': {'EntityName': 'TableName', 'ColumnName': 'ColumnName'}
    }
    Sorting is optional - If the Aggregation is either top or bottom then sort it.
    Args:
        json_data (dictionary) - Data generated using the Text to SQL algorithm.
    Returns:
        Output(dictionary) - JSON data required to request to database API
    '''
    # Initialize required variables
    send_data = {}
    sorts = {}
    filter_data = []
    # Get operator from the data dictionary
    operator_output = json_data[len(json_data)-1][1]
    # Get list of numbers from the user input to extract dates and numbers to generate JSON data.
    number_output = [temp_number_output[0] for temp_number_output in json_data if str(temp_number_output[0]).isdigit() and temp_number_output[1] == 'POBJ']
    if number_output:
        # If there are more than 1 numbers then we use both the numbers to extract data from database.
        if len(number_output) != 1:
            # if the number length is greater than 3 then it will be considered as year or else the number of years.
            if len(number_output[0]) > 3:
                # Switch operator based on the input text.
                if operator_output == 1 or operator_output == 3:
                    # If operator is 1 i.e. Less than or 3 i.e. Greater than then just check with single value
                    filter_data.append({"EntityName":"Orders_0","ColumnName":"OrderDate","Operator":operator_output,"Values":[number_output[0]+"-01-01 00:00:00.000","null"]})
                    operator_output = 0
                else:
                    # If operator is not 1 neither 3 then just apply for 2 values.
                    if int(number_output[0]) < int(number_output[1]):
                        filter_data.append({"EntityName":"Orders_0","ColumnName":"OrderDate","Operator":operator_output,"Values":[number_output[0]+"-01-01 00:00:00.000",number_output[1]+"-12-31 00:00:00.000"]})
                    else:
                        filter_data.append({"EntityName":"Orders_0","ColumnName":"OrderDate","Operator":operator_output,"Values":[number_output[1]+"-01-01 00:00:00.000",number_output[0]+"-12-31 00:00:00.000"]})
                    operator_output = 0
            else:
                # Number of years to find out the date.
                birthdate1 = datetime.now().date() - relativedelta(years=int(number_output[0]))
                birthdate2 = datetime.now().date() - relativedelta(years=int(number_output[1]))
                if birthdate1 > birthdate2:
                    filter_data.append({"EntityName":"Employees_0","ColumnName":"BirthDate","Operator":operator_output,"Values":[str(birthdate2),str(birthdate1)]})
                else:
                    filter_data.append({"EntityName":"Employees_0","ColumnName":"BirthDate","Operator":operator_output,"Values":[str(birthdate1),str(birthdate2)]})
        else:
            if len(number_output[0]) > 3:
                if operator_output == 1 or operator_output == 3:
                    if operator_output == 1:
                        filter_data.append({"EntityName":"Orders_0","ColumnName":"OrderDate","Operator":operator_output,"Values":[number_output[0]+"-01-01","null"]})
                    elif operator_output == 3:
                        filter_data.append({"EntityName":"Orders_0","ColumnName":"OrderDate","Operator":operator_output,"Values":[number_output[0]+"-12-31","null"]})
                    operator_output = 0
                else:
                    filter_data.append({"EntityName":"Orders_0","ColumnName":"OrderDate","Operator":operator_output,"Values":[number_output[0]+"-01-01",number_output[0]+"-12-31"]})
                    operator_output = 0
            else:
                if operator_output == 1:
                    operator_output = 3
                elif operator_output == 3:
                    operator_output = 1
                birthdate1 = datetime.now().date() - relativedelta(years=int(number_output[0]))
                filter_data.append({"EntityName":"Employees_0","ColumnName":"BirthDate","Operator":operator_output,"Values":[str(birthdate1),"null"]})
    for output_json_data in json_data:
        if 'ROOT' in output_json_data and 'table' in output_json_data:
            attr_name=[get_desc.split('|')[1] for get_desc in exago_data.table_data.get(output_json_data[1], None)][0]
            send_data = {"DisplayField":exago_data.mapped_data[output_json_data[1]]+"."+attr_name,"AggMethod": json_data[len(json_data)-1][0]}
        elif 'table' in output_json_data:
            if (output_json_data[2].lower() in  output_json_data[1].lower()) and 'NSUBJ' in output_json_data:
                attr_name=[get_desc.split('|')[1] for get_desc in exago_data.table_data.get(output_json_data[1], None)][0]
                send_data = {"DisplayField":exago_data.mapped_data[output_json_data[1]]+"."+attr_name,"AggMethod": json_data[len(json_data)-1][0]}
            else:
                attr_name = ""
                if output_json_data[1] == "Employees":
                    attr_name = "LastName"
                elif output_json_data[1] == "Categories":
                    attr_name = "CategoryName"
                elif output_json_data[1] == "Products":
                    attr_name = "ProductName"
                filter_data.append({"EntityName":exago_data.mapped_data[output_json_data[1]],"ColumnName":attr_name,"Operator":operator_output,"Values":[output_json_data[2],"null"]})
        elif 'attr' in output_json_data:
            if set(output_json_data[1].split()) != set("Birth Date".split()):
                for key, value in exago_data.table_data.items():
                    for temp_value in value:
                        if set(temp_value.split('|')[1].split()) == set(output_json_data[1].split()):
                            entity_name = key
                if 'NSUBJ' in output_json_data:
                    if output_json_data[2].lower() in  output_json_data[1].lower():
                        send_data = {"DisplayField":exago_data.mapped_data[entity_name]+"."+output_json_data[1].replace(' ', ''),"AggMethod": json_data[len(json_data)-1][0]}
                elif 'DOBJ' in output_json_data:
                    if output_json_data[1].lower() in output_json_data[2].lower():
                        send_data = {"DisplayField":exago_data.mapped_data[entity_name]+"."+output_json_data[1].replace(' ', ''),"AggMethod": json_data[len(json_data)-1][0]}
                    else:
                        send_data = {"DisplayField":exago_data.mapped_data[entity_name]+"."+"ProductName","AggMethod": json_data[len(json_data)-1][0]}
                        if json_data[len(json_data)-1][0] == 7 or json_data[len(json_data)-1][0] == 8:
                            sorts =  {"EntityName":exago_data.mapped_data[entity_name],"ColumnName": output_json_data[1].replace(' ', '')}
                else:
                    filter_data.append({"EntityName":exago_data.mapped_data[entity_name],"ColumnName":output_json_data[1],"Operator":operator_output,"Values":[output_json_data[2],"null"]})
    # Add filter to JSON data.
    send_data["Filters"] = filter_data
    # If Operator is 7 i.e. Top or 8 i.e. bottom then apply sorting
    if sorts:
        send_data["Sorts"] = sorts
    print('JSON Data',send_data)
    global json_data_to_send
    json_data_to_send = send_data
    get_data = "No Data Found"
    try:
        # Send created data to getdata method
        get_data = getdata(send_data)["ExecuteData"]
        if not get_data or 'ERROR' in get_data:
            get_data = "No Data Found"
        print('Final Output',get_data)
    except:
        pass
    return get_data
def performtexttoquery(google_output):
    '''
    This function is the algorithm to generate required information to create JSON data for database call.
    This algorithm uses NLTK library to get the word similarities from the user input and map it with the Database schema.
    If there is not any mapped data with the entities then fallback to NER.
    NER - Named Entity Recognition for Product and Categories mapping.
    Once the data is mapped the it is passed to generate JSON for database API.
    Args:
        google_output (dictionary) - Data generated using Google Language Speech API
    Returns:
        Output(dictionary) - Final output returned from the Database API
    '''
    table_output = []
    attr_output_first = []
    attr_output_others = []
    opr_output = []
    agg_output = []
    global entities_type
    # Get entitity name and root words
    print("Get entitity name and root words")
    entities = [text['text'] for text in google_output if text['partOfSpeech']['tag'] == 'NOUN' or (text['dependencyEdge']['label'] == 'ROOT' and 'mood' not in text['partOfSpeech'])]
    entities_type_name = [ent['name'] for ent in entities_type]
    entities_type_type = [ent for ent in entities_type if ent['type'] != 'OTHERS']
    for ent in entities:
        if ent not in [ent_text for ent in entities_type_name for ent_text in ent.split()]:
            entities_type_name.append(ent)
    # Getting List of Table Name from database schema
    print('Getting List of Table Name')
    entities_type_name_temp = entities_type_name[:]
    entities_dependency = []
    for text in google_output:
        if(text['dependencyEdge']['label'] == 'ROOT' or 'OBJ' in text['dependencyEdge']['label']
         or 'SUBJ' in text['dependencyEdge']['label'] or 'NUM' in text['dependencyEdge']['label']
         or 'CONJ' in text['dependencyEdge']['label'] or 'DEP' in text['dependencyEdge']['label'] or 'NPADVMOD' in text['dependencyEdge']['label']):
            if 'NUM' in text['dependencyEdge']['label'] or 'CONJ' in text['dependencyEdge']['label']or 'NPADVMOD' in text['dependencyEdge']['label']:
                entities_dependency.append([text['text'],'POBJ'])
            elif 'DEP' in text['dependencyEdge']['label']:
                entities_dependency.append([text['text'],'NSUBJ'])
            else:
                entities_dependency.append([text['text'],text['dependencyEdge']['label']])
    table_data = [key for key, value in exago_data.table_data.items()]
    # Perform Similarity for Table Name
    print('Perform Similarity for Table Name')
    table_output = performmultiwordsimilarity(entities_type_name,table_data,'table')
    # Getting List of Top entity Attributes
    print('Getting List of Top entity Attributes')
    attr_data =[ get_desc.split('|')[1] for get_desc in exago_data.table_data.get(table_output[0][2], None)]
    if entities_type_name:
        for temp_table_output in table_output:
            # If table_output from Table similarity is greater than 0.74 then remove from table output and then perform attribute similarity.
            if temp_table_output[0] > 0.74:
                entities_type_name.remove(temp_table_output[1])
        # Perform Similarity for Attributes
        print('Perform Similarity for Attributes')
        attr_output_first = performmultiwordsimilarity(entities_type_name,attr_data,'attr')
        if not attr_output_first:
            attr_output_first = [[0.0]]
        if attr_output_first[0][0] < 0.45:
            # If attr_output_first from Attributes similarity is less than 0.45 then perform attribute similarity.
            attr_data =[ get_desc.split('|')[1] for get_desc in (list(itertools.chain.from_iterable(value for key, value in exago_data.table_data.items() if key not in table_output[0][2] )))]
            attr_output_others = performmultiwordsimilarity(entities_type_name,attr_data,'attr')
    # Getting List of Aggregation and Operation Data
    print('Getting List of Aggregation and Operation Data')
    input_for_agg = [text['text'] for text in google_output if text['partOfSpeech']['tag'] != 'NOUN' and text['dependencyEdge']['label'] != 'ROOT']
    input_for_agg = ' '.join(input_for_agg)
    # Getting Similarity of Aggregation Data
    print('Getting Similarity of Aggregation Data')
    for key, value in exago_data.agg_data.items():
        for word in value:
            if not isinstance(word, int):
                if word.lower() in input_for_agg.lower():
                    agg_output = value[0]
    # Getting List of Opertional Data
    print('Getting List of Opertional Data')
    for key, value in exago_data.operator_data.items():
        for word in value:
            if not isinstance(word, int):
                if word.lower() in input_for_agg.lower():
                    opr_output = value[0]
    # Getting Similarity of Opertional Data
    print('Getting Similarity of Opertional Data')
    if table_output:
        print('table output:',table_output)
    if attr_output_first:
        print('Attributes first output:',attr_output_first)
    if attr_output_others:
        print('Attributes Others output:',attr_output_others)
    if opr_output:
        print('Operator output ner:',opr_output)
    else:
        opr_output = 0
        print('Operator output ner:',opr_output)
    if agg_output:
        print('Aggregation output ner:',agg_output)
    else:
        agg_output = 6
        print('Aggregation output ner:',agg_output)
    json_data = {'entities_type_name_temp':entities_type_name_temp,'entities_dependency':entities_dependency,'table_output':table_output,'attr_output_first':attr_output_first,
                'opr_output':opr_output,'agg_output':agg_output}
    temp_final_attr = []
    if attr_output_first:
        if attr_output_first[0][0] != 0.0:
            temp_final_attr.append(attr_output_first[0])
            if attr_output_others:
                temp_final_attr.append(attr_output_others[0])
        else:
            if attr_output_others:
                temp_final_attr.append(attr_output_others[0])
    final_entity = []
    if entities_dependency:
        for temp_entity_dependency in entities_dependency:
            temp_final_entity = []
            for temp_final_table_output in table_output:
                if temp_entity_dependency[0] in temp_final_table_output[1] and temp_entity_dependency[0] in str(entities_type_name_temp):
                    temp_final_entity.extend(['table', temp_final_table_output[2], temp_final_table_output[1],temp_entity_dependency[1]])
            if temp_entity_dependency[1] != 'ROOT' and temp_entity_dependency[0] not in str(temp_final_entity):
                 temp_final_entity.extend(temp_entity_dependency)
            if temp_entity_dependency[0] in str(temp_final_attr[0]):
                check_attr = [temp_attr for temp_attr in table_output if temp_attr[1] in temp_final_attr[0]]
                if check_attr:
                    if temp_final_attr[0][0] > 0.74:
                        temp_final_entity.pop(0)
                        temp_final_entity.pop(0)
                        temp_final_entity.insert(0,temp_final_attr[0][2])
                        temp_final_entity.insert(0, 'attr')
                else:
                    temp_final_entity.insert(0,temp_final_attr[0][2])
                    temp_final_entity.insert(0, 'attr')
            if temp_final_entity:
                final_entity.append(temp_final_entity)
    final_entity.append([agg_output, opr_output])
    # Pass the Raw information to form JSON data.
    get_data = generatejson(final_entity)
    return get_data
def performmultiwordsimilarity(input_list, data_list, data_type):
    '''
    This function is the algorithm to perform Multi word to Multi word similarities.
    Get the list of Input word or multiple words and match that with the list of Data word and get most matched words.
    Args:
        input_list (list) - Input list of words from User Input
        data_list (list) - List of data words i.e. From Database schema
        data_type (string) - Type of word
    Returns:
        Output(list) - Sorted list of most matched words.
    '''
    # Get NLTK directory from settings.py files.
    url = settings.NLTK_DIR
    # Appending to nltk data path so that the data is refered using given path.
    nltk.data.path.append(url)
    final_list = []
    for input_text in input_list:
        for data_text in data_list:
            output_list = []
            # If there is a direct match to name of the input text and data text then return 1.0 i.e. Full match
            if input_text.lower() in data_text.lower() or data_text.lower() in input_text.lower():
                final_list.append((1.0,input_text,data_text))
            else:
                temp_data_text = data_text
                for input_word in input_text.lower().split():
                    temp_final_list = []
                    for data_word in data_text.lower().split():
                        temp_list = []
                        entity_type_type = [dic_entity['type'] for dic_entity in entities_type if dic_entity['type'] != 'OTHER' and dic_entity['name'].lower() == input_word.lower()]
                        # If there is a similarity using the Products NER
                        temp_attr_output_product = [product for product in exago_data.ProductDetails if input_word.lower() in product.lower()]
                        # If there is a similarity using the Categories NER
                        temp_attr_output_category = [category for category in exago_data.CategoryDetails if input_word.lower() in category.lower()]
                        if (temp_attr_output_product or temp_attr_output_category) and data_type == "table":
                            if temp_attr_output_product:
                                # If there is a similarity using the Products NER then set 1.0
                                temp_list.append([1.0,input_word,'Products'])
                                temp_data_text = "Products"
                            elif temp_attr_output_category:
                                # If there is a similarity using the Categories NER then set 1.0
                                temp_list.append([1.0,input_word,'Categories'])
                                temp_data_text = "Categories"
                        elif entity_type_type and data_type == "table":
                            # If no direct match or NER match then perform similarity approach.
                            # Find the Synonyms of the Input and Data word using Synset from wordnet
                            wordFrominput_list = wordnet.synsets(entity_type_type[0])
                            wordFromdata_list = wordnet.synsets(data_word)
                            if wordFrominput_list and wordFromdata_list:
                                for wordfromdata in wordFromdata_list:
                                    # Perform similarity
                                    s = wordFrominput_list[0].wup_similarity(wordfromdata)
                                    if s == None:
                                        s = 0.0
                                    temp_list.append([s, input_word, data_word])
                        else:
                            wordFrominput_list = wordnet.synsets(input_word)
                            wordFromdata_list = wordnet.synsets(data_word)
                            if wordFrominput_list and wordFromdata_list:
                                for wordfromdata in wordFromdata_list:
                                    s = wordFrominput_list[0].wup_similarity(wordfromdata)
                                    if s == None:
                                        s = 0.0
                                    temp_list.append([s, input_word, data_word])
                        if temp_list:
                                # Get the top from all the list.
                                output_list.append(max(temp_list))
                    # Average the multiple words to get output of multi word similarity
                    temp_avg = np.round(np.mean([avg[0] for avg in output_list]),decimals=2)
                    if not math.isnan(temp_avg):
                        temp_final_list.append((temp_avg,input_word,temp_data_text))
                # Average the multiple words to get output of multi word to multi word similarity
                final_avg = np.round(np.mean([avg[0] for avg in temp_final_list]),decimals=2)
                if not math.isnan(final_avg):
                    final_list.append((final_avg,input_text,temp_data_text))
    # Sort it to get top final list
    sorted_final_list = sorted(final_list, reverse=True)
    max_list = True
    top_final_list=[]
    for top_final_temp in sorted_final_list:
        if top_final_temp[1] not in str(top_final_list) and top_final_temp[0] > 0.46:
            top_final_list.append(top_final_temp)
    return top_final_list
def getfeedback(text):
    '''
    This function is to get feedback from the user.
    If there is a direct match of user input with the Products NER or Categories NER then return the Type with the matched entity
    Args:
        text (string) - Input text of words from User Input
    Returns:
        feedback(string) - Type of NER either Products or Categories
        feedback_text(string) - Word matched with the NER
    '''
    print(text)
    feedback = ""
    feedback_text = []
    # Get list of all Categories from exago_data
    for cat_name in exago_data.CategoryDetails:
        # If there is match return feedback and Matched text
        if cat_name.lower() in text.lower():
            feedback = "Categories"
            feedback_text.append(cat_name)
    # Get list of all Products from exago_data
    for pro_name in exago_data.ProductDetails:
        # If there is match return feedback and Matched text
        if pro_name.lower() in text.lower():
            feedback = "Products"
            feedback_text.append(pro_name)
    print(feedback,feedback_text)
    return feedback,feedback_text
def getresults(text,feedback):
    global json_data_to_send
    json_data_to_send = ""
    google_output = ""
    nlp_output = ""
    print('Get Feedback from Input')
    # First step is to get feedback if there is a matched text from NER then ask user for the feedback
    get_feedback,feedback_text = getfeedback(text)
    if get_feedback:
        # If User provides the feedback then execute Text to Query algorithm
        if feedback:
            print('Get Results from Google NLP')
            # Get google output from Google Language Speech API
            google_output = googlettsapi(text)
            print('Passing Results from Google NLP to perform NLP')
            # Execute Text to Query algorithm
            nlp_output = performtexttoquery(google_output)
    else:
        # If there is no feedback required then directly execute Text to Query algorithm
        print('Get Results from Google NLP')
        # Get google output from Google Language Speech API
        google_output = googlettsapi(text)
        print('Passing Results from Google NLP to perform NLP')
        # Execute Text to Query algorithm
        nlp_output = performtexttoquery(google_output)
    return json_data_to_send,nlp_output,get_feedback,feedback_text
