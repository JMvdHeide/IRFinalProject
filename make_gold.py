#!/usr/bin/python3

import sklearn
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import operator

sia = SentimentIntensityAnalyzer()
import time
tweets = set()
with open('Tweets/ochtend_tweets.txt','r') as infile:
    for line in infile.readlines():
        line = line.split('\t')
        tweets.add(line[1])

with open('ochtend_tweets_gold','w') as outfile:
    for tweet in tweets:
        scores = sia.polarity_scores(tweet)
        del scores['compound']
        sorted_scores = sorted(scores.items(),key=operator.itemgetter(1),reverse=True)
        outfile.write("{}\t{}\n".format(tweet,sorted_scores[0][0]))
