#!/usr/bin/python3

import sklearn
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import operator
import csv
import time
sia = SentimentIntensityAnalyzer()
tweets = set()
with open('Tweets/ochtend_tweets.txt','r') as infile:
    for line in infile.readlines():
        line = line.split('\t')
        tweets.add(line[1])

with open('ochtend_tweets_gold.csv',mode='w') as outfile:
    writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for tweet in tweets:
        scores = sia.polarity_scores(tweet)
        del scores['compound']
        sorted_scores = sorted(scores.items(),key=operator.itemgetter(1),reverse=True)
        writer.writerow((tweet,sorted_scores[0][0]))
