#!/usr/bin/python3

import json
import csv
from nltk.tokenize import TweetTokenizer
from featx import bag_of_words, high_information_words, bag_of_words_in_set
from classification import precision_recall
import nltk
from nltk.classify import SklearnClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC, NuSVC
import sys
from os import listdir  # to read files
from os.path import isfile, join  # to read files


from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
import re
from collections import defaultdict


def onlyDigits(token):  # 7
    '''Is the token made up entirely of digits?'''
    if re.search(r'\D', token):
        return 0
    return 1


def isUrl(token):  # 12
    '''Is the token a URL? URLs are defined as starting with "http" followed by either ":" or "/".'''
    if re.match(r'http[:/]', token):
        return 1
    return 0


def containsDigitAndAlpha(token):  # 6
    '''Does the token contain both digits and alphanumeric characters?'''
    if re.search(r'\d', token) and re.search(r'[a-zA-Z]', token):
        return 1
    return 0


def get_filenames_in_folder(folder):
    return [f for f in listdir(folder) if isfile(join(folder, f))]


def get_feats(times_of_day, data_set):
    """Reads the golden standard CSV file and puts the content in bags of words"""
    print("\n##### Reading {} files...".format(data_set))
    feats = list()
    stemmer = SnowballStemmer("english")
    stop_words = set(stopwords.words('english'))

    for item in times_of_day:
        tweets_txt = open(item + '/' + data_set + '.csv')
        c = 0
        for line in tweets_txt.readlines():
            c += 1
            line = line.split(',')
            text = line[0].lower()
            tweets_txt = tweets_txt
            tokens = TweetTokenizer().tokenize(text)

            filtered_tokens = [stemmer.stem(
                w) for w in tokens if w not in stop_words if not onlyDigits(w)]
            bag = bag_of_words(filtered_tokens)
            feats.append((bag, item))
            #if c == 50000:
                #break

        print("{} {} tweets read".format(c, item))

    # return high_information(feats, times_of_day)
    return feats


def train(train_feats):
    """Trains a classifier"""
    print("\n##### Training classifier...")
    classifier = SklearnClassifier(LogisticRegression()).train(train_feats)
    return classifier


def calculate_f(precisions, recalls):
    f_measures = {}
    # calculates the f measure for each category using as input the precisions and recalls
    for key in precisions:
        if precisions[key] is None:
            f_measures[key] = 0
        elif precisions[key] > 0 and recalls[key] > 0:
            f_measure = (
                2 * (precisions[key] * recalls[key])) / (precisions[key] + recalls[key])
            f_measures[key] = f_measure
        else:
            f_measures[key] = 0
    return f_measures


def evaluation(classifier, test_feats, categories):
    """Calculates and prints accuracy, precision, recall and f-measure"""
    print("\n##### Evaluating...")
    accuracy = nltk.classify.accuracy(classifier, test_feats)
    print("  Accuracy: %f" % accuracy)
    precisions, recalls = precision_recall(classifier, test_feats)
    f_measures = calculate_f(precisions, recalls)

    print(" |-----------|-----------|-----------|-----------|")
    print(" |%-11s|%-11s|%-11s|%-11s|" %
          ("category", "precision", "recall", "F-measure"))
    print(" |-----------|-----------|-----------|-----------|")
    for category in categories:
        if precisions[category] is None:
            print(" |%-11s|%-11s|%-11s|%-11s|" % (category, "NA", "NA", "NA"))
        else:
            print(" |%-11s|%-11f|%-11f|%-11f|" % (category,
                                                  precisions[category], recalls[category], f_measures[category]))
    print(" |-----------|-----------|-----------|-----------|")


def high_information(feats, categories):
    """Obtain the high information words."""
    print("\n##### Obtaining high information words...")
    labelled_words = [(category, []) for category in categories]

    words = defaultdict(list)
    all_words = list()
    for category in categories:
        words[category] = list()

    for feat in feats:
        category = feat[1]
        bag = feat[0]
        for w in bag.keys():
            words[category].append(w)
            all_words.append(w)
    labelled_words = [(category, words[category]) for category in categories]

    hfw_lst = list(high_information_words(labelled_words))

    hfw_feats = []
    for c, words in labelled_words:

        for w in words:

            if w not in hfw_lst:
                words.remove(w)
        hfw = words.copy()
        hfw = dict((el, True) for el in hfw)
        hfw_feats.append((hfw, c))

    print("  Number of words in the data: %i" % len(all_words))
    print("  Number of distinct words in the data: %i" % len(set(all_words)))
    print("  Number of distinct 'high-information' words in the data: %i"
          % len(hfw_feats))

    return hfw_feats


def main():
    data_sets = ['train', 'test']
    times_of_day = ['morning', 'afternoon']
    train_feats = get_feats(times_of_day, 'train')
    test_feats = get_feats(times_of_day, 'test')

    classifier = train(train_feats)
    evaluation(classifier, test_feats, times_of_day)


if __name__ == '__main__':
    main()
