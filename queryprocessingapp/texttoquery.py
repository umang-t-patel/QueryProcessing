import nltk
def texttoquery(text):
    tokenized_words =  nltk.tokenize.word_tokenize(text.lower())
    # print(tokenized_words)
    # words = remove_stop_words(tokenized_words)
    # print(words)
    posttag = nltk.pos_tag(tokenized_words)
    # print(posttag)
    return posttag

def remove_stop_words(words):
    stop_words = set(nltk.corpus.stopwords.words("english"))
    filtered_sentence = [w for w in words if not w in stop_words]
    return(filtered_sentence)
