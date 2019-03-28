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

def get_feats(time_of_day, data_set):
	"""Reads the golden standard CSV file and puts the content in bags of words"""
	print("\n##### Reading {} files...".format(data_set))
	feats = list()
	c = 0
	with open(time_of_day + '/' + data_set + '.csv') as tweets_csv:
		readCSV = csv.reader(tweets_csv, delimiter = ',')
		for line in readCSV:
			c+=1
			text = line[0].lower()
			tokens = TweetTokenizer().tokenize(text)

			bag = bag_of_words(tokens)
			feats.append((bag, line[1]))
			if c == 100000:
				break
	print("{} {} tweets read".format(c, time_of_day))

	return feats

def train(train_feats):
	"""Trains a classifier"""
	print ("\n##### Training classifier...")
	classifier = SklearnClassifier(LinearSVC()).train(train_feats)
	return classifier

def calculate_f(precisions, recalls):
	f_measures = {}
	#calculates the f measure for each category using as input the precisions and recalls
	for key in precisions:
		if precisions[key] is None:
			f_measures[key] = 0
		elif precisions[key] > 0 and recalls[key] > 0:
			print(precisions[key],recalls[key])
			f_measure = (2 * (precisions[key] * recalls[key]))/(precisions[key] + recalls[key])
			f_measures[key] = f_measure
		else:
			f_measures[key] = 0
	return f_measures

def evaluation(classifier, test_feats, categories):
	"""Calculates and prints accuracy, precision, recall and f-measure"""
	print ("\n##### Evaluating...")
	accuracy = nltk.classify.accuracy(classifier, test_feats)
	print("  Accuracy: %f" % accuracy)
	precisions, recalls = precision_recall(classifier, test_feats)
	f_measures = calculate_f(precisions, recalls)

	print(" |-----------|-----------|-----------|-----------|")
	print(" |%-11s|%-11s|%-11s|%-11s|" % ("category","precision","recall","F-measure"))
	print(" |-----------|-----------|-----------|-----------|")
	for category in categories:
		if precisions[category] is None:
			print(" |%-11s|%-11s|%-11s|%-11s|" % (category, "NA", "NA", "NA"))
		else:
			print(" |%-11s|%-11f|%-11f|%-11f|" % (category, precisions[category], recalls[category], f_measures[category]))
	print(" |-----------|-----------|-----------|-----------|")


def main():
	categories = ['pos', 'neg', 'neu']
	data_sets = ['train', 'dev']
	times_of_day = ['morning', 'afternoon']

	for time_of_day in times_of_day:
		train_feats = get_feats(time_of_day, 'train')
		test_feats = get_feats(time_of_day, 'test')

		classifier = train(train_feats)
		evaluation(classifier, test_feats, categories)

if __name__ == '__main__':
	main()
