import logging
import pandas as pd
from config import constants
from main.helper import util
from sklearn.feature_extraction.text import TfidfTransformer
from collections import defaultdict
from main.helper.db_helper import SqlHelper
from main.helper.text_analyzer import TextAnalyzer
from main.helper.value import Value

logger = logging.getLogger(__name__)
reviews_df = None

# If you want to, change things here! #
top_how_much = 50
rating = 5
tree_tagger_dir = '../../../data/tree_tagger'
reversed_result = True  # True = absteigend
cumulated = True
stemming = False
tagging = True
language = 'german'
group_by_category = False
#####################################


def run():
    global reviews_df
    global rating
    global language

    reviews_df = fetch_reviews_from_postgres(with_categories=group_by_category)

    if rating:
        reviews_df = reviews_df[reviews_df.rating == rating]

    if language:
        reviews_df = reviews_df[reviews_df.language == language]

    if group_by_category:
        groups = reviews_df.groupby('category')

        for name, group in groups:
            logger.info('Group By Category')
            logger.info('Analyzing ' + str(name))
            name = str(name).replace('/', '_')
            analyze(group, language, str(rating) + '-Star Rating_Group_by_' + name + '_in_' + language)
    else:
        logger.info('Analyzing {0}-Star Reviews in {1}'.format(rating, language))
        analyze(reviews_df, language, '{0}-Star Reviews_in_{1}'.format(rating, language))


def fetch_reviews_from_postgres(with_categories):
    global language

    db = SqlHelper(constants.SQL_DATABASE_NAME)
    session = db.get_connection()

    if with_categories:
        query = 'SELECT r.rating, r.text, r.language, fc.name as category ' \
                'FROM review AS r JOIN food_category AS fc ' \
                'ON (r.restaurant_id = fc.restaurant_id);'
        df = pd.read_sql_query(sql=query, con=session)
    else:
        df = pd.read_sql_table(table_name='review', con=session)
    logger.info('Found {0} Reviews in {1}'.format(df.shape[0], language))

    return df


def analyze(reviews_to_analyze, language_to_analyze, result_file_name):
    global cumulated
    global stemming
    global tagging

    text_analyzer = TextAnalyzer(language_to_analyze, stemming, tagging, tree_tagger_dir)

    count_vectorizer = text_analyzer.create_count_vectorizer()

    top_words_cum = defaultdict(float)  # cumulated words
    top_words = {}

    bow_transformer = count_vectorizer.fit(reviews_to_analyze['text'])

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
    global stemming
    global reviews_df

    top_how_much_string = str(top_how_much)
    title = file_name + '_top_' + top_how_much_string + '_of_' + str(reviews_df.shape[0])
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


if __name__ == '__main__':
    util.setup_logging()
    run()
