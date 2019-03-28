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
from os import listdir # to read files
from os.path import isfile, join # to read files

def get_filenames_in_folder(folder):
	return [f for f in listdir(folder) if isfile(join(folder, f))]

def get_feats(times_of_day, data_set):
	"""Reads the golden standard CSV file and puts the content in bags of words"""
	print("\n##### Reading {} files...".format(data_set))
	feats = list()
	for item in times_of_day:
		tweets_txt =  open(item + '/' + data_set + '.txt')
		c = 0
		for line in tweets_txt.readlines():
			c+=1
			text = line.lower()
			tokens = TweetTokenizer().tokenize(text)
			bag = bag_of_words(tokens)
			feats.append((bag, item))

		print("{} {} tweets read".format(c, item))

	return feats

def train(train_feats):
	"""Trains a classifier"""
	print ("\n##### Training classifier...")
	classifier = SklearnClassifier(LogisticRegression()).train(train_feats)
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
		train_feats = get_feats(times_of_day, 'train')
		test_feats = get_feats(times_of_day, 'dev')

		classifier = train(train_feats)
		evaluation(classifier, test_feats, categories)

if __name__ == '__main__':
	main()
