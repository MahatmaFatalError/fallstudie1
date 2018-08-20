import json
import logging
import string
import pandas as pd
from main.helper import util
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from collections import defaultdict

logger = logging.getLogger(__name__)

# If you want to change things here #
data_excerpt = []
reviews = None
excerpt_size = 100
language = 'english'
filename = 'yelp_academic_dataset_review_sample.json'
top_words = defaultdict(float)
#####################################


def run():
    create_excerpt()
    write_json_file()
    create_df()
    analyze()
    # TODO: improve algorithm with stemming, tagging etc. and add categories


def analyze():
    global reviews, top_words

    reviews['length'] = reviews['text'].apply(len)

    reviews['text_token'] = reviews['text'].apply(text_process)

    bow_transformer = CountVectorizer(analyzer=text_process).fit(reviews['text'])

    review_bow = bow_transformer.transform(reviews['text'])

    logger.info('Shape of Sparse Matrix: {0}'.format(review_bow.shape))
    logger.info('Amount of Non-Zero occurences: {0}'.format(review_bow.nnz))

    sparsity = (100.0 * review_bow.nnz / (review_bow.shape[0] * review_bow.shape[1]))
    logger.info('sparsity: {0}'.format(sparsity))

    tfidf_transformer = TfidfTransformer().fit(review_bow)
    review_tfidf = tfidf_transformer.transform(review_bow)

    feature_names = bow_transformer.get_feature_names()

    for index in range(excerpt_size):
        feature_index = review_tfidf[index, :].nonzero()[1]
        tfidf_scores = zip(feature_index, [review_tfidf[index, x] for x in feature_index])
        top5_scores_sorted_by_tfidf = sorted(tfidf_scores, key=lambda tup: tup[1], reverse=True)[:5]
        for w, s in [(feature_names[i], s) for (i, s) in top5_scores_sorted_by_tfidf]:
            top_words[w] += s

    logger.info('------------------------TOP 10 words in corpus----------------------------------')
    top_words_sorted_by_tfidf = sorted(top_words.items(), key=lambda tup: tup[1], reverse=True)[:10]
    for word, score in top_words_sorted_by_tfidf:
        logger.info('{0} - {1}'.format(word, score))


def write_json_file():
    global data_excerpt
    with open('yelp_academic_dataset_review_sample.json', 'w') as outfile:
        for json_object in data_excerpt:
            json.dump(json_object, outfile)
            outfile.write('\n')


def text_process(mess):
    """
    Takes in a string of text, then performs the following:
    1. Remove all punctuation
    2. Remove all stopwords
    3. Returns a list of the cleaned text
    """
    # Check characters to see if they are in punctuation
    global language

    nopunc = [char for char in mess if char not in string.punctuation]

    # Join the characters again to form the string.
    nopunc = ''.join(nopunc)

    # Now just remove any stopwords
    return [word for word in nopunc.split() if word.lower() not in stopwords.words(language)]


def create_excerpt():
    global data_excerpt

    with open(filename, 'r') as file:
        for index, line in enumerate(file):
            if index == excerpt_size:
                break
            else:
                line = line.rstrip()
                json_line = json.loads(line)
                data_excerpt.append(json_line)


def create_df():
    global reviews

    json_data = json.dumps(data_excerpt)
    reviews = pd.read_json(json_data)


if __name__ == '__main__':
    util.setup_logging()

    run()
