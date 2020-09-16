from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import string

NUMBERS = ['1','2','3','4','5','6','7','8','9','0']
LANGUAGE_LIST = ['english','portuguese', 'spanish', 'italian', 'french']

def find_stop_words(languages=LANGUAGE_LIST):
    try:
        stop_words = []
        for language in languages:
            stop_words += stopwords.words(language)
    except:
        import nltk
        nltk.download('stopwords')
        stop_words = []
        for language in languages:
            stop_words += stopwords.words(language)
    return stop_words

class TextNormalization:

    def __init__(self):
        self.number = NUMBERS
        self.stop_words = find_stop_words()
        self.porter = PorterStemmer()

    def text_normalization(self, text, use_stop_words=True, use_porter=True):
        table = str.maketrans('', '', string.punctuation)
        # remove punctuations
        text = str(text).translate(table)
        #lower case
        text = text.lower()
        # eliminating numbers
        for number in NUMBERS:
            text = text.replace(number, '')
        text = text.strip()


        # eliminate stop words and/or normalizes verbs to the infinitive form
        if use_stop_words and not use_porter:
            text = ' '.join([i for i in text.split(' ') if i not in self.stop_words])
        elif use_porter and not use_stop_words:
            text = self.porter.stem(text)
        elif use_porter and use_stop_words:
            text = ' '.join([self.porter.stem(i) for i in text.split(' ') if i not in self.stop_words])

        return text
