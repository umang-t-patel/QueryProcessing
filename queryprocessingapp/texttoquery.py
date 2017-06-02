import nltk
from django.conf import settings
pos_dict = {'.': 'sentence terminator',
'CC': 'Coordinating conjunction',
'CD': 'Cardinal number',
'DT': 'Determiner',
'EX': 'Existential there',
'FW': 'Foreign word',
'IN': 'Preposition or subordinating conjunction',
'JJ': 'Adjective',
'JJR': 'Adjective',
'JJS': 'Adjective',
'LS': 'List item marker',
'MD': 'Modal',
'NN': 'Noun',
'NNS': 'Noun plural',
'NNP': 'Proper noun',
'NNPS': 'Proper noun plural',
'PDT': 'Predeterminer',
'POS': 'Possessive ending',
'PRP': 'Personal pronoun',
'PRP$': 'Possessive pronoun',
'RB': 'Adverb',
'RBR': 'Adverb comparative',
'RBS': 'Adverb superlative',
'RP': 'Particle',
'SYM': 'Symbol',
'TO': 'to',
'UH': 'Interjection',
'VB': 'Verb',
'VBD': 'Verb past tense',
'VBG': 'Verb gerund or present participle',
'VBN': 'Verb past participle',
'VBP': 'Verb non-3rd person singular present',
'VBZ': 'Verb 3rd person singular present',
'WDT': 'Wh-determiner',
'WP': 'Wh-pronoun',
'WP$': 'Possessive wh-pronoun',
'WRB': 'Wh-adverb'}
def texttoquery(text):
    url = settings.NLTK_DIR
    nltk.data.path.append(url)
    tokenized_words =  nltk.tokenize.word_tokenize(text.lower())
    # print(tokenized_words)
    # words = remove_stop_words(tokenized_words)
    # print(words)
    temp_posttag = nltk.pos_tag(tokenized_words)
    posttag = []
    for temp_pos_tag in temp_posttag:
        temp_var = (temp_pos_tag,pos_dict[temp_pos_tag[1]])
        posttag.append(temp_var)
    return posttag

def remove_stop_words(words):
    stop_words = set(nltk.corpus.stopwords.words("english"))
    filtered_sentence = [w for w in words if not w in stop_words]
    return(filtered_sentence)
