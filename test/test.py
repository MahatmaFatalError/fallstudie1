import string
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import treetaggerwrapper

language = 'english'
tree_tagger_dir = '../data/tree_tagger'


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


def text_process(mess):
    global language

    # Remove punctutation
    no_punc = [char for char in mess if char not in string.punctuation]
    # Join the characters again to form the string.
    no_punc = ''.join(no_punc)

    # Remove any stopwords
    no_stopwords = [word for word in no_punc.split() if word.lower() not in stopwords.words(language)]

    # Tag each word
    tagged_words = tag_text(no_stopwords)

    # Remove unwanted tags
    extracted_tags = extract_tags(tagged_words)

    # Stem it
    # stemmer = SnowballStemmer(language)
    # stemmed_words = [stemmer.stem(word) for word in tagged_words]

    result = extracted_tags
    return result

new_text = "Speaking as a Californian, this is the best In-n-out I've been to. Spacious, clean, beautiful, with a nice " \
           "interior and big outdoor patio seatings, it's the best Cali environment. Lines can get long, but it goes by " \
           "really fast. Waiting time for food wasn't bad at all.Hamburger ($2.70) - 4/5. Nice butter grilled buns, " \
           "slightly overcooked and dry patty, with a sad piece of lettuce and a slice of tomato. It's not the " \
           "'freshest' one I've had that's for sure. The secret sauce was as good as always. " \
           "French Fries ($1.95) - 5/5. I've always hated In-n-out fries because they are very hard. This one was " \
           "amazing, and probably redeemed my 10+ years of bad fries experience. The fires were pipping hot and fresh, " \
           "nice amount of grease, soft but with a nice crisp!"
words = text_process(new_text)

print(words)



