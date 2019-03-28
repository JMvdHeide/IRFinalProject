#!/usr/bin/python3

import sklearn
import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import operator
import csv
import sys
sia = SentimentIntensityAnalyzer()


def open_tweets(file,folder):
    tweets = set()
    filename = folder + '/' + file + '.txt'
    print(filename)
    with open(filename,'r') as infile:
        for line in infile.readlines():
            tweets.add(line)
    return tweets

def write_tweets(tweets,file,folder):
    with open(folder + '/' + file + '.csv',mode='w') as outfile:
        writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for tweet in tweets:
            scores = sia.polarity_scores(tweet)
            del scores['compound']
            sorted_scores = sorted(scores.items(),key=operator.itemgetter(1),reverse=True)
            writer.writerow((tweet,sorted_scores[0][0]))
    outfile.close()


def main():
    filenames = ['train','dev','test']
    for filename in filenames:
        morning_tweets = open_tweets(filename,'morning')
        write_tweets(morning_tweets,filename,'morning')
        afternoon_tweets = open_tweets(filename,'afternoon')
        write_tweets(afternoon_tweets,filename,'afternoon')
if __name__ == "__main__":
    main()
