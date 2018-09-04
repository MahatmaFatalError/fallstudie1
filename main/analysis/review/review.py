import json
import logging
import string
import pandas as pd
import treetaggerwrapper

from main.helper import util
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from collections import defaultdict
from nltk.stem import SnowballStemmer

from main.helper.value import Value
from main.helper.yelp import YelpHelper

logger = logging.getLogger(__name__)
reviews = None
data_excerpt = []

# If you want to, change things here! #
excerpt_size = 1000
top_how_much = 100
language = 'english'
source_file_name = 'yelp_academic_dataset_review_sample.json'
tree_tagger_dir = '../../../data/tree_tagger'
reversed_result = True  # True = absteigend
cumulated = True
stemming = True
#####################################


def run():
    create_excerpt()
    # enrich_with_category()
    # write_json_file()
    create_df()
    one_star_reviews = reviews[reviews.stars == 1]
    five_star_reviews = reviews[reviews.stars == 5]
    logger.info('Analyzing 1-Star Reviews')
    analyze(one_star_reviews, '1-Star Reviews')
    logger.info('Analyzing 5-Star Reviews')
    analyze(five_star_reviews, '5-Star Reviews')


def analyze(reviews_to_analyze, result_file_name):
    global cumulated

    top_words_cum = defaultdict(float)  # cumulated words
    top_words = {}

    bow_transformer = CountVectorizer(analyzer=text_process).fit(reviews_to_analyze['text'])

    review_bow = bow_transformer.transform(reviews_to_analyze['text'])

    logger.info('Shape of Sparse Matrix: {0}'.format(review_bow.shape))
    logger.info('Amount of Non-Zero occurences: {0}'.format(review_bow.nnz))

    sparsity = (100.0 * review_bow.nnz / (review_bow.shape[0] * review_bow.shape[1]))
    logger.info('sparsity: {0}'.format(sparsity))

    tfidf_transformer = TfidfTransformer().fit(review_bow)
    review_tfidf = tfidf_transformer.transform(review_bow)

    feature_names = bow_transformer.get_feature_names()

    rows, columns = reviews_to_analyze.shape
    for index in range(rows):
        feature_index = review_tfidf[index, :].nonzero()[1]
        tfidf_scores = zip(feature_index, [review_tfidf[index, x] for x in feature_index])
        top5_scores_sorted_by_tfidf = sorted(tfidf_scores, key=lambda tup: tup[1], reverse=reversed_result)[:5]
        for w, s in [(feature_names[i], s) for (i, s) in top5_scores_sorted_by_tfidf]:
            top_words_cum[w] += s
            top_words[Value(w)] = s

    if cumulated:
        write_result(top_words_cum, result_file_name)
    else:
        write_result(top_words, result_file_name)


def write_result(result, file_name):
    global top_how_much
    global cumulated
    global excerpt_size
    global stemming

    top_how_much_string = str(top_how_much)
    title = file_name + '_top_' + top_how_much_string + '_of_' + str(excerpt_size)
    if reversed_result:
        title += '_reversed'
    if cumulated:
        title += '_cumulated'
    if stemming:
        title += '_stemmed'
    title += '.txt'

    with open('result/' + title, 'w') as result_file:
        result_file.write(file_name)
        result_file.write('\n')
        result_file.write('------------------------ TOP ' + top_how_much_string + ' ----------------------------------')
        result_file.write('\n')
        result_sorted_by_tfidf = sorted(result.items(), key=lambda tup: tup[1], reverse=reversed_result)[:top_how_much]
        for word, score in result_sorted_by_tfidf:
            result_file.write('{0} - {1}'.format(word, score))
            result_file.write('\n')


def write_json_file():
    global data_excerpt

    with open('yelp_academic_dataset_review_sample.json', 'w') as outfile:
        for json_object in data_excerpt:
            json.dump(json_object, outfile)
            outfile.write('\n')


def text_process(review_text):
    global language
    global stemming

    # Remove punctutation
    no_punc = [char for char in review_text if char not in string.punctuation]
    # Join the characters again to form the string.
    no_punc = ''.join(no_punc)

    # Remove any stopwords
    no_stopwords = [word for word in no_punc.split() if word.lower() not in stopwords.words(language)]

    # Tag each word
    tagged_words = tag_text(no_stopwords)

    # Remove unwanted tags
    extracted_tags = extract_tags(tagged_words)

    if stemming:
        # Stem it
        stemmer = SnowballStemmer(language)
        result = [stemmer.stem(word) for word in extracted_tags]
    else:
        result = extracted_tags
    return result


def create_excerpt():
    global data_excerpt

    with open(source_file_name, 'r') as file:
        for index, line in enumerate(file):
            if index == excerpt_size:
                break
            else:
                line = line.rstrip()
                json_line = json.loads(line)
                data_excerpt.append(json_line)


def enrich_with_category():
    global data_excerpt

    yelp = YelpHelper()

    for review in data_excerpt:
        category_tupel = ()
        business_id = review['business_id']
        result, status_code = yelp.get_business(business_id, 0)
        status_codes = [403, 404]
        if status_code not in status_codes:
            if 'error' not in result:
                categories = result['categories']
                if categories is not None:
                    for category in categories:
                        cat_title = category['title']
                        title_tuple = (cat_title, )
                        category_tupel += title_tuple
                    review['category'] = category_tupel
                    logger.info('Added Category: {0}'.format(category_tupel))
            else:
                logger.error('{0}: {1}'.format(result['error']['code'], result['error']['description']))
                break


def create_df():
    global reviews

    json_data = json.dumps(data_excerpt)
    reviews = pd.read_json(json_data)


def tag_text(text):
    if language == 'german':
        country_code = 'de'
    else:
        country_code = 'en'
    tagger = treetaggerwrapper.TreeTagger(TAGLANG=country_code, TAGDIR=tree_tagger_dir)
    text_with_tags = tagger.tag_text(text)

    tags = treetaggerwrapper.make_tags(text_with_tags)
    return tags


def extract_tags(tags):
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
    if language == 'german':
        useful_tags = usefult_tags_german
    else:
        useful_tags = useful_tags_english

    for tag in tags:
        pos = tag.pos
        if pos in useful_tags:
            result.append(tag.word)

    return result


if __name__ == '__main__':
    util.setup_logging()
    run()
