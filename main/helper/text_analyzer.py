import logging
import string

import treetaggerwrapper
from nltk import SnowballStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer


class TextAnalyzer:

    language = None
    stemming = None
    tree_tagger_dir = None
    count_vectorizer = None

    logger = logging.getLogger(__name__)

    def __init__(self, language, stemming, tagger_dir):
        self.tree_tagger_dir = tagger_dir
        self.language = language
        self.stemming = stemming

    def create_count_vectorizer(self):
        self.count_vectorizer = CountVectorizer(analyzer=self.text_process)
        return self.count_vectorizer

    def text_process(self, text):

        # Remove punctutation
        no_punc = [char for char in text if char not in string.punctuation]
        # Join the characters again to form the string.
        no_punc = ''.join(no_punc)

        # Remove any stopwords
        no_stopwords = [word for word in no_punc.split() if word.lower() not in stopwords.words(self.language)]

        # Tag each word
        tagged_words = self._tag_text(no_stopwords)

        # Remove unwanted tags
        extracted_tags = self._extract_tags(tagged_words)

        if self.stemming:
            # Stem it
            stemmer = SnowballStemmer(self.language)
            result = [stemmer.stem(word) for word in extracted_tags]
        else:
            result = extracted_tags
        return result

    def _tag_text(self, text):
        if self.language == 'german':
            country_code = 'de'
        else:
            country_code = 'en'
        tagger = treetaggerwrapper.TreeTagger(TAGLANG=country_code, TAGDIR=self.tree_tagger_dir)
        text_with_tags = tagger.tag_text(text)

        tags = treetaggerwrapper.make_tags(text_with_tags)
        return tags

    def _extract_tags(self, tags):
        result = []
        usefult_tags_german = [
            'ADJA',
            'ADJD',
            'FM',
            'NA',
            'NE',
            'NN'
        ]
        useful_tags_english = [
            'FW',
            'JJ',
            'JJR',
            'JJS',
            'RB',
            'RBS',
            'RBR',
            'NNS',
            'NN',
            'NP',
            'NPS'
        ]
        if self.language == 'german':
            useful_tags = usefult_tags_german
        else:
            useful_tags = useful_tags_english

        for tag in tags:
            pos = tag.pos
            if pos in useful_tags:
                result.append(tag.word)

        return result
