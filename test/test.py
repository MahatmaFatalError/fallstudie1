import string
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

language = 'german'


def text_process(mess):
    """
    Takes in a string of text, then performs the following:
    1. Remove all punctuation
    2. Remove all stopwords
    3. Returns a list of the cleaned text
    """
    # Check characters to see if they are in punctuation
    global language

    no_punc = [char for char in mess if char not in string.punctuation]

    # Join the characters again to form the string.
    no_punc = ''.join(no_punc)

    # Now just remove any stopwords
    no_stopwords = [word for word in no_punc.split() if word.lower() not in stopwords.words(language)]
    return [stemmer.stem(word) for word in no_stopwords]


stemmer = SnowballStemmer(language)

new_text = "Als Anna abends aß, aß Anna abends Ananas."

words = text_process(new_text)

print(words)


