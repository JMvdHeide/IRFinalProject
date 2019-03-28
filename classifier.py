#!/usr/bin/python3

import json
import csv
from nltk.tokenize import TweetTokenizer
from featx import bag_of_words, high_information_words, bag_of_words_in_set
from classification import precision_recall

from nltk.classify import SklearnClassifier
from sklearn.naive_bayes import MultinomialNB

import sys

def get_feats(time_of_day, data_sets, feats):
	"""Reads the golden standard CSV file and puts the content in bags of words"""
	print("\n##### Reading {} files...").format(feats)
	feats = list()
	c = 0
	with open(time_of_day + '/' + data_sets[0] + '.csv') as tweets_csv:
		readCSV = csv.reader(tweets_csv, delimiter = ',')
		for line in readCSV:
			c+=1
			text = line[0].lower()
			tokens = TweetTokenizer(text)
			
			bag = bag_of_words(tokens)
			feats.append((bag, line[1]))

	print("{} {} tweets read").format(c, time_of_day)		

	return feats

def train(train_feats):
	"""Trains a classifier"""
	print ("\n##### Training classifier...")
	classifier = SklearnClassifier(MultinomialNB()).train(train_feats)
	return classifier

def calculate_f(precisions, recalls, categories):
	"""Calculates f-measures"""
	f_measures = {}
	for category in categories:
		if precisions[category] == None or recalls[category] == None:
			f_measures[category] = None
		if precisions[category] == 0 or recalls[category] == 0:
			f_measures[category] = 0
		else:
			f_measures[category] = (2*precisions[category]*recalls[category])/(precisions[category]+recalls[category])

	return f_measures

def evaluation(classifier, test_feats, categories):
	"""Calculates and prints accuracy, precision, recall and f-measure"""
	print ("\n##### Evaluating...")
	accuracy = nltk.classify.accuracy(classifier, test_feats)
	print("  Accuracy: %f" % accuracy)
	precisions, recalls = precision_recall(classifier, test_feats)
	f_measures = calculate_f(precisions, recalls, categories)  

	print(" |-----------|-----------|-----------|-----------|")
	print(" |%-11s|%-11s|%-11s|%-11s|" % ("category","precision","recall","F-measure"))
	print(" |-----------|-----------|-----------|-----------|")
	for category in categories:
		if precisions[category] is None:
			print(" |%-11s|%-11s|%-11s|%-11s|" % (category, "NA", "NA", "NA"))
		else:
			print(" |%-11s|%-11f|%-11f|%-11f|" % (category, precisions[category], recalls[category], f_measures[category]))
	print(" |-----------|-----------|-----------|-----------|")

	print(accuracy)

def main():
	categories = ['pos', 'neg', 'neu']
	data_sets = ['train', 'dev']
	times_of_day = ['morning', 'afternoon']

	for time_of_day in times_of_day:
		train_feats = get_feats(time_of_day, data_sets, train_feats)
		test_feats = get_feats(time_of_day, data_sets, test_feats)

		classifier = train(train_feats)
		evaluation(classifier, test_feats, categories)

if __name__ == '__main__':
	main()